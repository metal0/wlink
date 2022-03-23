import construct

from .headers import ClientHeader
from .opcode import Opcode

CMSG_KEEP_ALIVE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_KEEP_ALIVE, 0)
)

def make_CMSG_KEEP_ALIVE():
	return CMSG_KEEP_ALIVE.build(dict())

__all__ = [
	'make_CMSG_KEEP_ALIVE', 'CMSG_KEEP_ALIVE'
]