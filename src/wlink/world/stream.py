import trio
from construct import ConstructError

from wlink.world.errors import ProtocolError, Disconnected
from wlink.world.packets import *
from wlink.world.packets.b12340.protocol import WorldClientProtocol, WorldServerProtocol
from ..log import logger

class WorldStream:
	def __init__(self, stream, protocol):
		self._send_lock, self._read_lock = trio.StrictFIFOLock(), trio.StrictFIFOLock()
		self._stream = stream
		self._num_packets_received = 0
		self._num_packets_sent = 0
		self._average_num_frames = 1
		self.protocol = protocol

	@property
	def num_packets_sent(self):
		return self._num_packets_sent

	@property
	def num_packets_received(self):
		return self._num_packets_received

	async def _send_all(self, data: bytes):
		async with self._send_lock:
			result = await self._stream.send_all(data)
			return result

	async def _receive_some(self, max_bytes=None) -> bytes:
		async with self._read_lock:
			result = await self._stream.receive_some(max_bytes)
			if type(result) is not bytes:
				return bytes(result)
			return result

	async def next_decrypted_packet(self):
		raise NotImplemented()

	async def decrypted_packets(self):
		while True:
			try:
				packet = await self.next_decrypted_packet()
				yield packet
			except KeyError as e:
				logger.log('PACKETS', f'Dropped {e}')

	async def receive_encrypted_packet(self, packet):
		data = self.protocol.decrypt_packet(await self._receive_some())
		packet = packet.parse(data)
		self._num_packets_received += 1

		logger.log('PACKETS', f'{packet=}')
		logger.log('PACKETS', f'{data=}')
		return packet

	async def receive_unencrypted_packet(self, packet_type):
		data = await self._receive_some()
		packet_type = packet_type.parse(data)
		self._num_packets_received += 1

		logger.log('PACKETS', f'{packet_type=}')
		return packet_type

	async def send_unencrypted_packet(self, packet_type, data: bytes):
		packet = packet_type.parse(data)
		await self._send_all(data)
		self._num_packets_sent += 1

		logger.log('PACKETS', f'{packet=}')
		logger.log('PACKETS', f'{data=}')

	async def send_encrypted_packet(self, packet_type, data: bytes):
		packet = packet_type.parse(data)
		encrypted = self.protocol.encrypt_packet(data, packet.header)
		await self._send_all(encrypted)
		self._num_packets_sent += 1

		logger.log('PACKETS', f'{packet=}')
		logger.log('PACKETS', f'{data=}')

class WorldClientStream(WorldStream):
	def __init__(self, stream: trio.abc.HalfCloseableStream, session_key: int):
		super().__init__(stream, WorldClientProtocol(session_key))

	def decrypt_packet(self, data: bytes):
		start = self.protocol.crypto.decrypt(bytes([data[0]]))
		body_start = 5 if headers.is_large_server_packet(start) else 4
		rest = self.protocol.crypto.decrypt(data[1:body_start])
		return (start + rest) + data[body_start:]

	def encrypt_packet(self, data: bytes, header):
		return self.protocol.crypto.encrypt(data[0:6]) + data[6:]

	async def next_decrypted_packet(self):
		# Receive header first
		original_data = await self._receive_some(max_bytes=4)
		if original_data is None or len(original_data) == 0:
			raise Disconnected('received EOF from server')

		logger.log('PACKETS', f'(Client) Incoming packet...')

		try:
			logger.log('TRACE', f'{original_data=}')

			header_data = self.protocol.crypto.decrypt(original_data[:4])
			logger.log('TRACE', f'{header_data=}')

			is_large = headers.is_large_server_packet(header_data)

			if is_large:
				header_data += self.protocol.crypto.decrypt(await self._receive_some(max_bytes=1))

			header = ServerHeader().parse(header_data)
			logger.log('PACKETS', f'{header=}')
			data = header_data

			num_packets = 0
			bytes_left = header.size - (3 if is_large else 2)
			while bytes_left > 0:
				leftover_bytes = await self._receive_some(max_bytes=bytes_left)

				num_packets += 1
				data += leftover_bytes
				bytes_left -= len(leftover_bytes)
				if leftover_bytes is None or len(leftover_bytes) == 0:
					raise ProtocolError('received EOF from server')

			try:
				self._average_num_frames += num_packets
				self._average_num_frames /= 2
				fragmentation = abs(int(100 * (num_packets / self._average_num_frames - 1)))

				logger.log('PACKETS', f'fragmentation: {fragmentation}%, average: {self._average_num_frames}')
				logger.log('PACKETS', f'{data=}')

				packet = self.protocol.parser.parse(data, header)
				self._num_packets_received += 1
				return packet
			except KeyError:
				self._num_packets_received += 1
				raise KeyError(header)

		except ValueError as e:
			if 'is not a valid Opcode' in str(e):
				raise ProtocolError('Invalid opcode, stream might be out of sync')
			else:
				logger.exception(e)

class WorldServerStream(WorldStream):
	def __init__(self, stream: trio.abc.HalfCloseableStream, session_key: int):
		super().__init__(stream, WorldServerProtocol(session_key))

	def encrypt_packet(self, data: bytes, header):
		packed_header = ServerHeader().build(dict(
			opcode=header.opcode,
			size=header.size
		))

		body_start = 5 if headers.is_large_server_packet(header) else 4
		logger.debug(f'{data[:body_start]=} {packed_header=}')
		return self.protocol.crypto.encrypt(packed_header) + data[body_start:]

	def decrypt_packet(self, data: bytes):
		if data is None or len(data) == 0:
			return None

		return self.protocol.crypto.decrypt(data[:6]) + data[6:]

	async def next_decrypted_packet(self):
		# Receive header first
		original_data = await self._receive_some(max_bytes=6)

		if original_data is None or len(original_data) == 0:
			raise Disconnected('received EOF from client')

		logger.log('PACKETS', f'(Server) Incoming packet...')
		logger.log('PACKETS', f'{original_data=}')

		try:
			header_data = self.protocol.crypto.decrypt(original_data[:6])
			header = ClientHeader().parse(header_data)
			bytes_left = header.size - ClientHeader().sizeof() + 2
			logger.log('PACKETS', f'{header=}')

			data = header_data
			while bytes_left > 0:
				logger.log('PACKETS', f'Listening for {bytes_left} byte body...')
				body = await self._receive_some(max_bytes=bytes_left)
				if body is None or len(data) == 0:
					raise ProtocolError('received EOF from server')

				data += body
				bytes_left -= len(body)

			try:
				logger.log('PACKETS', f'{data=}')
				packet = self.protocol.parser.parse(data, header)
				logger.log('PACKETS', f'{packet=}')
				self._num_packets_received += 1
				return packet

			except (KeyError, ConstructError) as e:
				if type(e) is KeyError:
					logger.log('PACKETS', f'Dropped packet: {header=}')
				else:
					logger.exception(e)
					raise e

		except ValueError as e:
			if 'is not a valid Opcode' in str(e):
				raise ProtocolError('Invalid opcode, stream might be out of sync')
			else:
				logger.exception(e)
