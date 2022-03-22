import construct
import trio

from .packets import ChallengeRequest, ChallengeResponse, ProofRequest, ProofResponse, RealmlistRequest, \
	RealmlistResponse
from .packets import Response
from .realm import RealmFlags
from ..log import logger

class AuthProtocol:
	def __init__(self, stream: trio.abc.HalfCloseableStream):
		self.stream = stream
		self._send_lock = trio.Lock()
		self._read_lock = trio.Lock()

	async def _send_all(self, data: bytes):
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

	async def send_proof_request(self, client_public: int, session_proof: int, checksum: int=4601254584545541958749308449812234986282924510, num_keys: int=0, security_flags: int=0):
		await self._send_all(ProofRequest.build(dict(
			client_public=client_public,
			session_proof=session_proof,
			checksum=checksum,
			num_keys=num_keys,
			security_flags=security_flags
		)))

	async def receive(self, expected_size: int):
		data = bytearray()
		while expected_size > 0:
			data += await self._receive_some(expected_size)
			expected_size -= len(data)

		return bytes(data)

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
