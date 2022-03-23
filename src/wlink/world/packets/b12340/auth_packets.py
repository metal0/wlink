import random
from typing import Optional

import construct
from enum import Enum

from wlink.utility.construct import PackEnum, UpperCString
from .headers import ServerHeader, ClientHeader
from .opcode import Opcode

default_addon_bytes = b'\x9e\x02\x00\x00x\x9cu\xd2AN\xc30\x10\x05Pw\xc1\x19X\x94\x9b\xb0"\xa9\x14E\xd4\x9b\xc6\xac\xab\x89=$\xa3\xd8\xe3h\xe2\x94\xb6\xf7\xe0\x08\x9c\x8b\xab \x90@ \r\xeb\xaf7\xdf\x1e\xcd\xad1\xa6\x8at\xbd\x82\x84\xe3\x83\x1f\tO\x98\x90\xcbSk6\xe9\xe5no\xfe\xe4\x82\x0cz\xb2\xfaB\x99\xbf\xb3\xed\xfb\xcd\xdbOV\x81\xf4(\xcb\x98g\x95VPJ\xc4g\xc2\x18,1%\x98\xb5\x19\xc4\x81xP\x07\xd4\x10\x91\x03\x88\xc2\xea\x9cz(\xfb<h\xec+sx.\n\xdca\xbf\x0e.\xe7\xb8(\xb2\xb1\xf5\x08E\xfdkc\xbbUNxQ\x1f\xda\xc4\xcb<\xeal\xa5\x18*\xe0Iu-/3z\xbd\xb0-\x98\xba\xec\',\xff\xad\xc7\x82\x97\xac\xda\x03PP\x89\xfb\xdc\xa8\xde\xe7(\xa1\x05\x86\x01E\x83yB\xfd\x08\x9c@\xc0n\xa2\x18\xf5F\x01b\x94\xdf\xf4\xfeu\xf7\xf8\x01\\~\xda\x99'

class Expansion(Enum):
	vanilla = 0,
	tbc = 1,
	wotlk = 2

CMSG_AUTH_SESSION = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_AUTH_SESSION, 0),
	'build' / construct.Default(construct.Int32ul, 12340),
	'login_server_id' / construct.Default(construct.Int32ul, 0),
	'account_name' / UpperCString('ascii'),
	'login_server_type' / construct.Default(construct.Int32ul, 0),
	'client_seed' / construct.Int32ul,
	'region_id' / construct.Default(construct.Int32ul, 0),
	'battlegroup_id' / construct.Default(construct.Int32ul, 0),
	'realm_id' / construct.Default(construct.Int32ul, 1),
	'dos_response' / construct.Default(construct.ByteSwapped(construct.Int64ul), 3),
	'account_hash' / construct.BytesInteger(20, swapped=True),
	'addon_info' / construct.Default(
		construct.GreedyBytes,
		# construct.Compressed(AddonsInfo, 'zlib'),
		default_addon_bytes
	),
)

# 'addon_info' / construct.Default(
def make_CMSG_AUTH_SESSION(
	account_name, client_seed, account_hash, realm_id,
	build=12340, login_server_id=0, login_server_type=0, region_id=0, battlegroup_id=0,
	addon_info: bytes = default_addon_bytes, dos_response=3
) -> bytes:
	size = 0
	size += 4 + 4
	size += len(account_name) + 1
	size += 4 + 4 + 4 + 4 + 4 + 8 + 20 + len(addon_info)
	return CMSG_AUTH_SESSION.build(dict(
		build=build,
		login_server_id=login_server_id,
		account_name=account_name,
		login_server_type=login_server_type,
		client_seed=client_seed,
		region_id=region_id,
		battlegroup_id=battlegroup_id,
		realm_id=realm_id,
		account_hash=account_hash,
		addon_info=addon_info,
		dos_response=dos_response,
		header=dict(size=4 + size)
	))

SMSG_AUTH_CHALLENGE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUTH_CHALLENGE, 40),
	construct.Padding(4),
	'server_seed' / construct.Int32ul,
	'encryption_seed1' / construct.BytesInteger(16, swapped=True),
	'encryption_seed2' / construct.BytesInteger(16, swapped=True)
)

def make_SMSG_AUTH_CHALLENGE(
	server_seed: int = random.getrandbits(32),
	encryption_seed1: int = random.getrandbits(16),
	encryption_seed2: int = random.getrandbits(16)
) -> bytes:
	return SMSG_AUTH_CHALLENGE.build(dict(
		server_seed=server_seed,
		encryption_seed1=encryption_seed1,
		encryption_seed2=encryption_seed2
	))

class AuthResponse(Enum):
	ok = 0x0C
	failed = 0x0D
	reject = 0x0E
	bad_server_proof = 0x0F
	unavailable = 0x10
	system_error = 0x11
	billing_error = 0x12
	billing_expired = 0x13
	version_mismatch = 0x14
	unknown_account = 0x15
	incorrect_password = 0x16
	session_expired = 0x17
	server_shutting_down = 0x18
	already_logging_in = 0x19
	login_server_not_found = 0x1A
	wait_queue = 0x1B
	banned = 0x1C
	already_online = 0x1D
	no_time = 0x1E
	db_busy = 0x1F
	suspended = 0x20
	parental_control = 0x21

BillingInfo = construct.Struct(
	'time_left' / construct.ByteSwapped(construct.Default(construct.Int, 0)),
	'plan' / construct.Default(construct.Byte, 0),
	'time_rested' / construct.ByteSwapped(construct.Default(construct.Int, 0)),
)

SMSG_AUTH_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_AUTH_RESPONSE, 15),
	'response' / PackEnum(AuthResponse),
	'billing' / BillingInfo, #
	'expansion' / construct.Default(PackEnum(Expansion), Expansion.wotlk), # which WoW expansion
	'queue_position' / construct.Default(construct.Switch(
		construct.this.response == AuthResponse.wait_queue, {
			True: construct.Int32ul,
			False: construct.Pass
		}
	), construct.Pass)
)

def make_SMSG_AUTH_RESPONSE(
	response: AuthResponse, expansion=Expansion.wotlk,
	queue_position: Optional[int] = None,
	billing=None
) -> bytes:
	if billing is None:
		billing = dict(
			billing=dict(
			time_left=0, time_rested=0,
			plan=0,
		))

	size = 1 + (4 + 1 + 4) + 1
	if queue_position is not None:
		size += 4

	return SMSG_AUTH_RESPONSE.build(dict(
		header=dict(opcode=Opcode.SMSG_AUTH_RESPONSE, size=size + 2),
		response=response, expansion=expansion,
		queue_position=queue_position,
		billing=billing,
	))

__all__ = [
	'make_SMSG_AUTH_RESPONSE', 'make_SMSG_AUTH_CHALLENGE', 'make_CMSG_AUTH_SESSION', 'CMSG_AUTH_SESSION',
	'SMSG_AUTH_RESPONSE', 'SMSG_AUTH_CHALLENGE', 'AuthResponse', 'Expansion', 'BillingInfo'
]