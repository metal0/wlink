from .headers import ServerHeader, is_large_server_packet
from ...crypto import WorldCrypto
from .parse import WorldServerPacketParser, WorldClientPacketParser

class WorldProtocol:
	def __init__(self, session_key: int, encryption_key: bytes, decryption_key: bytes):
		self._num_packets_received = 0
		self._num_packets_sent = 0
		self._average_num_frames = 1
		self.crypto = WorldCrypto(session_key, encryption_key=encryption_key, decryption_key=decryption_key)

	def encrypt_packet(self, data: bytes, header):
		raise NotImplemented()

	def decrypt_packet(self, data: bytes):
		raise NotImplemented()

class WorldClientProtocol(WorldProtocol):
	def __init__(self, session_key: int):
		super().__init__(session_key,
			encryption_key=bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE]),
			decryption_key=bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57]),
		)

		self.parser = WorldServerPacketParser()

	def decrypt_packet(self, data: bytes):
		start = self.crypto.decrypt(bytes([data[0]]))
		body_start = 5 if is_large_server_packet(start) else 4
		rest = self.crypto.decrypt(data[1:body_start])
		return (start + rest) + data[body_start:]

	def encrypt_packet(self, data: bytes, header):
		return self.crypto.encrypt(data[0:6]) + data[6:]

class WorldServerProtocol(WorldProtocol):
	def __init__(self, session_key: int):
		super().__init__(session_key,
			encryption_key=bytes([0xCC, 0x98, 0xAE, 0x04, 0xE8, 0x97, 0xEA, 0xCA, 0x12, 0xDD, 0xC0, 0x93, 0x42, 0x91, 0x53, 0x57]),
			decryption_key=bytes([0xC2, 0xB3, 0x72, 0x3C, 0xC6, 0xAE, 0xD9, 0xB5, 0x34, 0x3C, 0x53, 0xEE, 0x2F, 0x43, 0x67, 0xCE]),
		)

		self.parser = WorldClientPacketParser()

	def encrypt_packet(self, data: bytes, header):
		packed_header = ServerHeader().build(dict(
			opcode=header.opcode,
			size=header.size
		))

		body_start = 5 if is_large_server_packet(header) else 4
		return self.crypto.encrypt(packed_header) + data[body_start:]

	def decrypt_packet(self, data: bytes):
		if data is None or len(data) == 0:
			return None

		return self.crypto.decrypt(data[:6]) + data[6:]

__all__ = [
	'WorldServerProtocol', 'WorldClientProtocol', 'WorldProtocol'
]