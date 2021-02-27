import construct
from enum import Enum

from pont.utility.construct import PackEnum
from ..opcode import Opcode
from ..realm import Realm

class RealmFlags(Enum):
	none = 0
	unavailable = 1
	offline = 2
	specify_build = 4
	unknown1 = 8
	unknown2 = 0x10
	new_players = 0x20
	recommended = 0x40
	full = 0x80

	def __and__(self, other):
		value = self.value & other.value
		return RealmFlags(value)

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	'size' / construct.Default(construct.Int16ul,  8),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.Int16ul, Realm),
)
