import construct

from .headers import ServerHeader, ClientHeader
from .opcode import Opcode

CMSG_TIME_SYNC_RESP = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_TIME_SYNC_RESP, 8),
	'id' / construct.Int32ul,
	'client_ticks' / construct.Int32ul,
)

def make_CMSG_TIME_SYNC_RESP(id: int, client_ticks: int):
	return CMSG_TIME_SYNC_RESP.build(dict(
		id=id, client_ticks=(client_ticks & 0xFFFFFFFF),
	))

SMSG_TIME_SYNC_REQ = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_TIME_SYNC_REQ, 4),
	'id' / construct.Int32ul,
)

def make_SMSG_TIME_SYNC_REQ(id: int):
	return SMSG_TIME_SYNC_REQ.build(dict(id=id))

CMSG_QUERY_TIME = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_QUERY_TIME, 0),
)

def make_CMSG_QUERY_TIME():
	return CMSG_QUERY_TIME.build(dict())

SMSG_QUERY_TIME_RESPONSE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_QUERY_TIME_RESPONSE, 8),
	'game_time' / construct.Int32ul,
	'time_until_reset' / construct.Int32ul
)
def make_SMSG_QUERY_TIME_RESPONSE(game_time: int, time_until_reset: int):
	return SMSG_QUERY_TIME_RESPONSE.build(dict(
		game_time=game_time, time_until_reset=time_until_reset,
	))

__all__ = [
	'make_SMSG_QUERY_TIME_RESPONSE', 'make_CMSG_QUERY_TIME', 'make_CMSG_TIME_SYNC_RESP', 'make_SMSG_TIME_SYNC_REQ',
	'CMSG_QUERY_TIME', 'CMSG_TIME_SYNC_RESP', 'SMSG_TIME_SYNC_REQ', 'SMSG_QUERY_TIME_RESPONSE'
]