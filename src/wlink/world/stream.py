import trio
import hashlib
import hmac
import random
from typing import Optional, List
from construct import ConstructError

from wlink.world.packets import *
from wlink.world.packets.b12340.parse import WorldServerPacketParser, WorldClientPacketParser
from wlink.utility.construct import compute_packed_guid_byte_size, pack_guid, NamedConstruct
from wlink.world.errors import ProtocolError, Disconnected
from wlink.cryptography import rc4
from wlink.log import logger

class WorldStream:
	def __init__(self, stream: trio.abc.HalfCloseableStream, session_key: int, encryption_key: bytes, decryption_key: bytes):
		self._stream = stream
		self._encryption_key = encryption_key
		self._decryption_key = decryption_key

		self._send_lock, self._read_lock = trio.StrictFIFOLock(), trio.StrictFIFOLock()

		self._has_encryption = False
		self._encrypter, self._decrypter = None, None
		self._num_packets_received = 0
		self._num_packets_sent = 0
		self._average_num_frames = 1

		self._init_encryption(session_key)

	@property
	def num_packets_sent(self):
		return self._num_packets_sent

	@property
	def num_packets_received(self):
		return self._num_packets_received

	def _init_encryption(self, session_key: int):
		session_key_bytes = session_key.to_bytes(length=40, byteorder='little')
		encrypt_hmac = hmac.new(key=self._encryption_key, digestmod=hashlib.sha1)
		encrypt_hmac.update(session_key_bytes)

		decrypt_hmac = hmac.new(key=self._decryption_key, digestmod=hashlib.sha1)
		decrypt_hmac.update(session_key_bytes)

		self._encrypter = rc4.RC4(encrypt_hmac.digest())
		self._encrypter.encrypt(bytes([0] * 1024))

		self._decrypter = rc4.RC4(decrypt_hmac.digest())
		self._decrypter.encrypt(bytes([0] * 1024))
		self._has_encryption = True

	def encrypt_packet(self, data: bytes, header):
		raise NotImplemented()

	def decrypt_packet(self, data: bytes):
		raise NotImplemented()

	def enable_encryption(self):
		self._has_encryption = True

	def disable_encryption(self):
		self._has_encryption = False

	def encrypt(self, data: bytes):
		if self.has_encryption():
			encrypted = self._encrypter.encrypt(data)
			return encrypted

		return data

	def decrypt(self, data: bytes):
		if self.has_encryption():
			decrypted = self._decrypter.encrypt(data)
			return decrypted

		return data

	def has_encryption(self):
		return self._has_encryption

	async def send_all(self, data: bytes):
		async with self._send_lock:
			result = await self._stream.send_all(data)
			return result

	async def receive_some(self, max_bytes=None) -> bytes:
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

	async def _receive_encrypted_packet(self, packet):
		data = self.decrypt_packet(await self.receive_some())
		packet = packet.parse(data)
		self._num_packets_received += 1

		logger.log('PACKETS', f'{type(packet)=}')
		# logger.log('PACKETS', packet)
		# logger.log('PACKETS', f'{data=}')
		return packet

	async def receive_unencrypted_packet(self, packet_type):
		data = await self.receive_some()
		packet_type = packet_type.parse(data)
		self._num_packets_received += 1

		logger.log('PACKETS', f'{packet_type=}')
		return packet_type

	async def _send_unencrypted_packet(self, packet_type, **params):
		data = packet_type.build(params)
		await self.send_all(data)
		self._num_packets_sent += 1

		logger.log('PACKETS', f'{packet_type=}')
		# logger.log('PACKETS', f'{data=}')

	async def _send_encrypted_packet(self, packet_type, **params):
		data = packet_type.build(params)
		packet = packet_type.parse(data)
		encrypted = self.encrypt_packet(data, packet.header)
		await self.send_all(encrypted)
		self._num_packets_sent += 1

		logger.log('PACKETS', f'{packet.header.opcode=} {packet=}')
		logger.log('PACKETS', f'{data=}')

class WorldClientStream(WorldStream):
	def __init__(self, stream: trio.abc.HalfCloseableStream, session_key: int):
		super().__init__(stream, session_key,
			encryption_key=bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE]),
			decryption_key=bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57]),
		)

		self.parser = WorldServerPacketParser()

	def decrypt_packet(self, data: bytes):
		# logger.debug(f'(Client) {data=}')
		if data is None or len(data) == 0:
			return None

		start = self.decrypt(bytes([data[0]]))
		body_start = 5 if headers.is_large_server_packet(start) else 4
		rest = self.decrypt(data[1:body_start])
		return (start + rest) + data[body_start:]

	def encrypt_packet(self, data: bytes, header):
		# logger.debug(f'(Client) {data=}')
		return self.encrypt(data[0:6]) + data[6:]

	async def next_decrypted_packet(self):
		# Receive header first
		original_data = await self.receive_some(max_bytes=4)
		if original_data is None or len(original_data) == 0:
			raise Disconnected('received EOF from server')

		logger.log('PACKETS', f'(Client) Incoming packet...')

		try:
			header_data = self.decrypt(original_data[:4])
			is_large = headers.is_large_server_packet(header_data)

			if is_large:
				header_data += self.decrypt(await self.receive_some(max_bytes=1))

			header = ServerHeader().parse(header_data)
			logger.log('PACKETS', f'{header=}')
			data = header_data

			num_packets = 0
			bytes_left = header.size - 2
			while bytes_left > 0:
				leftover_bytes = await self.receive_some(max_bytes=bytes_left)

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

				packet = self.parser.parse(data, header)
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
		super().__init__(stream, session_key,
			encryption_key=bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57]),
			decryption_key=bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE]),
		)

		self.parser = WorldClientPacketParser()

	def encrypt_packet(self, data: bytes, header):
		packed_header = ServerHeader().build(dict(
			opcode=header.opcode,
			size=header.size
		))

		body_start = 5 if headers.is_large_server_packet(header) else 4
		logger.debug(f'{data[:body_start]=} {packed_header=}')
		return self.encrypt(packed_header) +  data[body_start:]

	def decrypt_packet(self, data: bytes):
		if data is None or len(data) == 0:
			return None

		return self.decrypt(data[:6]) + data[6:]

	async def next_decrypted_packet(self):
		# Receive header first
		original_data = await self.receive_some(max_bytes=6)

		if original_data is None or len(original_data) == 0:
			raise Disconnected('received EOF from client')

		logger.log('PACKETS', f'(Server) Incoming packet...')
		logger.log('PACKETS', f'{original_data=}')

		try:
			header_data = self.decrypt(original_data[:6])
			header = ClientHeader().parse(header_data)
			bytes_left = header.size - ClientHeader().sizeof()
			logger.log('PACKETS', f'{header=}')

			data = header_data
			while bytes_left > 0:
				logger.log('PACKETS', f'Listening for {bytes_left} byte body...')
				body = await self.receive_some(max_bytes=bytes_left)
				if body is None or len(data) == 0:
					raise ProtocolError('received EOF from server')

				data += body
				bytes_left -= len(body)

			try:
				logger.log('PACKETS', f'{data=}')
				packet = self.parser.parse(data, header)
				logger.log('PACKETS', f'{packet=}')
				self._num_packets_received += 1
				return packet

			except (KeyError, ConstructError) as e:
				if type(e) is KeyError:
					logger.log('PACKETS', f'Dropped packet: {header=}')
				else:
					logger.exception(e)

		except ValueError as e:
			if 'is not a valid Opcode' in str(e):
				raise ProtocolError('Invalid opcode, stream might be out of sync')
			else:
				logger.exception(e)
