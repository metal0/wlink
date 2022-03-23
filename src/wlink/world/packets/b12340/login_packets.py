from typing import Tuple

import construct

from wlink.utility.construct import Coordinates, GuidConstruct
from .headers import ServerHeader, ClientHeader
from .opcode import Opcode
from wlink.guid import Guid

SMSG_LOGIN_VERIFY_WORLD = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGIN_VERIFY_WORLD, 20),
	'map' / construct.Int32ul,
	'position' / construct.ByteSwapped(Coordinates()),
	'rotation' / construct.Float32l,
)

def make_SMSG_LOGIN_VERIFY_WORLD(map: int, position, rotation) -> bytes:
	return SMSG_LOGIN_VERIFY_WORLD.build(dict(
		map=map,
		position=position,
		rotation=rotation
	))

SMSG_LOGOUT_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGOUT_RESPONSE, 5),
	'reason' / construct.Int32ul,
	'instant_logout' / construct.Flag,
)

def make_SMSG_LOGOUT_RESPONSE(reason: int, instant_logout: bool) -> bytes:
	return SMSG_LOGOUT_RESPONSE.build(dict(
		reason=reason,
		instant_logout=instant_logout,
	))

SMSG_LOGOUT_CANCEL_ACK = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGOUT_CANCEL_ACK, 0),
)

def make_SMSG_LOGOUT_CANCEL_ACK():
	return SMSG_LOGOUT_CANCEL_ACK.build(dict())

SMSG_LOGOUT_COMPLETE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_LOGOUT_COMPLETE, 0),
)

def make_SMSG_LOGOUT_COMPLETE():
	return SMSG_LOGOUT_COMPLETE.build(dict())

CMSG_PLAYER_LOGIN = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_PLAYER_LOGIN, 8),
	'guid' / GuidConstruct(Guid)
)

def make_CMSG_PLAYER_LOGIN(guid):
	return CMSG_PLAYER_LOGIN.build(dict(
		guid=guid
	))

CMSG_LOGOUT_REQUEST = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_LOGOUT_REQUEST, 0),
)

def make_CMSG_LOGOUT_REQUEST():
	return CMSG_LOGOUT_REQUEST.build(dict())

CMSG_LOGOUT_CANCEL = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_LOGOUT_CANCEL, 0),
)

def make_CMSG_LOGOUT_CANCEL():
	return CMSG_LOGOUT_REQUEST.build(dict())

__all__ = [
	'make_CMSG_LOGOUT_CANCEL', 'make_CMSG_LOGOUT_REQUEST', 'make_SMSG_LOGOUT_RESPONSE', 'make_SMSG_LOGOUT_COMPLETE',
	'make_SMSG_LOGIN_VERIFY_WORLD', 'make_CMSG_PLAYER_LOGIN', 'make_SMSG_LOGOUT_CANCEL_ACK', 'CMSG_LOGOUT_CANCEL',
	'CMSG_LOGOUT_REQUEST', 'CMSG_PLAYER_LOGIN', 'SMSG_LOGOUT_RESPONSE', 'SMSG_LOGOUT_COMPLETE', 'SMSG_LOGOUT_CANCEL_ACK',
	'SMSG_LOGIN_VERIFY_WORLD',
]