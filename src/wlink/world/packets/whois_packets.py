import construct

from wlink.world.opcode import Opcode
from .char_enum import CombatClass, Race, Gender
from .headers import ClientHeader, ServerHeader
from wlink.utility.construct import PackEnum

CMSG_WHOIS = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_WHOIS),
	'name' / construct.CString('utf8')
)

SMSG_WHOIS = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_WHOIS),
	'message' / construct.CString('utf8')
)

# WHO is a non-privileged ingame character query
CMSG_WHO = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_WHO, 4 + 4 + 0 + 0 + 4 + 4 + 4 + 4 * 0),
	'min_level' / construct.Default(construct.Int32ul, 1),
	'max_level' / construct.Default(construct.Int32ul, 80),
	'name' / construct.CString('utf8'),
	'guild_name' / construct.Default(construct.CString('utf8'), ''),
	'race' / construct.Default(construct.Int32ul, 0),
	'combat_class' / construct.Default(construct.Int32ul, 0),
	'zones' / construct.Default( # max length is 10 (TODO: check overflow)
		construct.PrefixedArray(construct.Int32ul, construct.Int32ul),
		[]
	),
	'search_terms' / construct.Default( # max num of strings is 4 (TODO: check overflow)
		construct.PrefixedArray(construct.Int32ul, construct.CString('utf8')),
		[]
	)
)

WhoMatchInfo = construct.Struct(
	'name' / construct.CString('utf8'),
	'guild' / construct.CString('utf8'),
	'level' / construct.Int32ul,
	'combat_class' / PackEnum(CombatClass),
	'race' / PackEnum(Race),
	'gender' / PackEnum(Gender),
	'zone_id' / construct.Int32ul,
)

SMSG_WHO = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_WHO),
	'total_num_matches' / construct.Int32ul,
	'matches' / construct.PrefixedArray(construct.Int32ul, WhoMatchInfo),
)