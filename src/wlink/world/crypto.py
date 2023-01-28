import hashlib
import hmac

from wlink.cryptography import rc4


class WorldCrypto:
    def __init__(self, session_key: int, encryption_key: bytes, decryption_key: bytes):
        session_key_bytes = session_key.to_bytes(length=40, byteorder="little")
        encrypt_hmac = hmac.new(key=encryption_key, digestmod=hashlib.sha1)
        encrypt_hmac.update(session_key_bytes)

        decrypt_hmac = hmac.new(key=decryption_key, digestmod=hashlib.sha1)
        decrypt_hmac.update(session_key_bytes)

        self._encrypter = rc4.RC4(encrypt_hmac.digest())
        self._encrypter.encrypt(bytes([0] * 1024))

        self._decrypter = rc4.RC4(decrypt_hmac.digest())
        self._decrypter.encrypt(bytes([0] * 1024))
        self._enabled = True

    @property
    def enabled(self):
        return self._enabled

    def encrypt(self, data: bytes):
        if self.enabled:
            encrypted = self._encrypter.encrypt(data)
            return encrypted

        return data

    def decrypt(self, data: bytes):
        if self.enabled:
            decrypted = self._decrypter.encrypt(data)
            return decrypted

        return data

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False
