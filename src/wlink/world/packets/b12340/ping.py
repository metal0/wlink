import construct

from .headers import ServerHeader, ClientHeader
from .opcode import Opcode
from ....log import logger

CMSG_PING = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_PING, body_size=8),
	'id' / construct.Default(construct.Int32ul, 0),
	'latency' / construct.Default(construct.Int32ul, 60),
)

def make_CMSG_PING(id, latency=60):
	logger.debug(f'{id=} {latency=}')
	return CMSG_PING.build(dict(
		header=dict(size=4 + 8),
		id=id, latency=latency
	))

SMSG_PONG = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_PONG, 4),
	'ping' / construct.Int32ul,
)

__all__ = [
	'SMSG_PONG', 'make_CMSG_PING', 'CMSG_PING'
]