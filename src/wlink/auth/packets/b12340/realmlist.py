import construct

from wlink.utility.construct import PackEnum
from wlink.auth.packets.b12340.opcode import Opcode
from wlink.auth.realm import Realm

RealmlistRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	construct.Padding(4)
)

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	'size' / construct.Default(construct.Int16ul, 8),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.Int16ul, Realm),
)
