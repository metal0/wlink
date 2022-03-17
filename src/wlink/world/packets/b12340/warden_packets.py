import construct

from .headers import ServerHeader, ClientHeader
from .opcode import Opcode


SMSG_WARDEN_DATA = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_WARDEN_DATA, size=39),
	'encrypted' / construct.GreedyBytes
)

CMSG_WARDEN_DATA = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_WARDEN_DATA),
	'encrypted' / construct.GreedyBytes,
)