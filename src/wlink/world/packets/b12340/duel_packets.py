import construct

from wlink.utility.construct import GuidConstruct
from .headers import ServerHeader, ClientHeader
from .opcode import Opcode
from wlink.guid import Guid
from .query_packets import NegatedFlag

CMSG_DUEL_ACCEPTED = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_DUEL_ACCEPTED, 8),
	'unk' / construct.Default(GuidConstruct(Guid), Guid()),
)
def make_CMSG_DUEL_ACCEPTED():
	return CMSG_DUEL_ACCEPTED.build(dict())

CMSG_DUEL_CANCELLED = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_DUEL_CANCELLED, 8),
	'unk' / GuidConstruct(Guid),
)

SMSG_DUEL_REQUESTED = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_DUEL_REQUESTED, 8 + 8),
	'flag_obj' / GuidConstruct(Guid),
	'requester' / GuidConstruct(Guid),
)

SMSG_DUEL_COMPLETE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_DUEL_COMPLETE),
	'cancelled' / NegatedFlag(),
)

SMSG_DUEL_WINNER = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_DUEL_WINNER),
	'loser_fled' / construct.Flag,
	'winner' / construct.CString('utf8'),
    'loser' / construct.CString('utf8'),
)