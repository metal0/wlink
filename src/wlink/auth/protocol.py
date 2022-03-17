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

	async def send_challenge_request(self, username: str, build=12340, version='3.3.5', country='enUS', game='WoW', arch='x86', os='OSX', ip='127.0.0.1'):
		await self._send_all(ChallengeRequest.build(dict(
			country=country,
			build=build,
			version=version,
			game=game,
			architecture=arch,
			account_name=username,
			ip=ip,
			os=os,
			size=30 + len(username),
		)))

	async def send_challenge_response(self, prime: int, server_public: int, salt: int, response: Response = Response.success,
			generator_length=1, generator=7, prime_length=32, checksum=0, security_flag=0):
		await self._send_all(ChallengeResponse.build(dict(
			rc4=dict(
				server_public=server_public,
				response=response,
				generator_length=generator_length,
				generator=generator,
				prime_length=prime_length,
				prime=prime,
				salt=salt,
				checksum=checksum,
				security_flag=security_flag
		))))

	async def receive_challenge_request(self) -> ChallengeRequest:
		return await self.receive_packet(ChallengeRequest)

	async def receive_challenge_response(self) -> ChallengeResponse:
		return await self.receive_packet(ChallengeResponse)

	async def send_proof_response(self, response: Response, session_proof_hash: int=0, account_flags=32768, survey_id=0, login_flags=0):
		await self._send_all(ProofResponse.build(dict(
			header=dict(response=response),
			session_proof_hash=session_proof_hash,
			account_flags=account_flags,
			survey_id=survey_id,
			login_flags=login_flags
		)))

	async def send_proof_request(self, client_public: int, session_proof: int, checksum: int=4601254584545541958749308449812234986282924510, num_keys: int=0, security_flags: int=0):
		await self._send_all(ProofRequest.build(dict(
			client_public=client_public,
			session_proof=session_proof,
			checksum=checksum,
			num_keys=num_keys,
			security_flags=security_flags
		)))

	async def receive_proof_request(self) -> ProofRequest:
		return await self.receive_packet(ProofRequest)

	async def receive(self, expected_size: int):
		data = bytearray()
		while expected_size > 0:
			data += await self._receive_some(expected_size)
			expected_size -= len(data)

		return bytes(data)

	async def receive_proof_response(self) -> ProofResponse:
		return await self.receive_packet(ProofResponse)

	async def send_realmlist_request(self):
		await self._send_all(RealmlistRequest.build({}))

	async def receive_realmlist_request(self) -> RealmlistRequest:
		return await self.receive_packet(RealmlistRequest)

	async def send_realmlist_response(self, realms):
		size = 8
		for realm in realms:
			size += 3 + len(realm['name']) + 1 + len(':'.join(map(str, realm['address']))) + 1 + 4 + 3
			if 'flags' in realm and (realm['flags'] & RealmFlags.specify_build) == RealmFlags.specify_build.value:
				size += 5

		await self._send_all(RealmlistResponse.build(dict(
			realms=realms, size=size
		)) + b'\x10\x00')

	async def receive_realmlist_response(self) -> RealmlistResponse:
		return await self.receive_packet(RealmlistResponse)

	async def aclose(self):
		await self.stream.aclose()
		self.stream = None
