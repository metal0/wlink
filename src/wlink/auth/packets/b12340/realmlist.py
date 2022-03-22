import construct

from wlink.utility.construct import PackEnum
from wlink.auth.packets.b12340.opcode import Opcode
from wlink.auth.realm import Realm, RealmFlags

RealmlistRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	construct.Padding(4)
)

def make_realmlist_request():
	return RealmlistRequest.build({})

RealmlistResponse = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.realm_list, PackEnum(Opcode)), Opcode.realm_list),
	'size' / construct.Default(construct.Int16ul, 8),
	construct.Padding(4),
	'realms' / construct.PrefixedArray(construct.Int16ul, Realm),
)

def make_realmlist_response(realms):
	size = 8
	for realm in realms:
		size += 3 + len(realm['name']) + 1 + len(':'.join(map(str, realm['address']))) + 1 + 4 + 3
		if 'flags' in realm and (realm['flags'] & RealmFlags.specify_build) == RealmFlags.specify_build.value:
			size += 5

	return RealmlistResponse.build(dict(
		realms=realms, size=size
	)) + b'\x10\x00'
