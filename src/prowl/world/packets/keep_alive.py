import construct

from .headers import ClientHeader
from prowl.world.opcode import Opcode

CMSG_KEEP_ALIVE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_KEEP_ALIVE, 0)
)