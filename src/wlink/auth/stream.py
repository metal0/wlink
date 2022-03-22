import construct
import trio

from ..log import logger

class AuthProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._send_lock = trio.Lock()
		self._read_lock = trio.Lock()

	async def send_all(self, data: bytes):
		async with self._send_lock:
			await self.stream.send_all(data)

	async def _receive_some(self, max_bytes=None):
		async with self._read_lock:
			return await self.stream.receive_some(max_bytes)

	async def receive_packet(self, packet_type):
		data = bytearray()
		while True:
			try:
				data.extend(await self._receive_some())
				packet = packet_type.parse(data)
				logger.log('PACKETS', f'{data=} {packet=}')
				return packet
			except construct.ConstructError:
				pass

	async def receive(self, expected_size: int):
		data = bytearray()
		while expected_size > 0:
			data += await self._receive_some(expected_size)
			expected_size -= len(data)

		return bytes(data)

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
