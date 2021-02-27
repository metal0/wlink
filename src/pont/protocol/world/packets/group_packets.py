import construct

from .headers import ClientHeader, ServerHeader
from pont.protocol.world.opcode import Opcode

CMSG_GROUP_INVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_INVITE, 10),
	'invitee' / construct.CString('ascii'),
	construct.Padding(4)
)

CMSG_GROUP_ACCEPT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_ACCEPT, 4),
	construct.Padding(4)
)

SMSG_GROUP_INVITE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_INVITE, 10),
	'in_group' / construct.Flag,
	'inviter' / construct.CString('ascii'),
	construct.Padding(4 + 1 + 4)
)