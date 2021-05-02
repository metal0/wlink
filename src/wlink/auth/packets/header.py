import construct

from wlink.utility.construct import PackEnum
from ..opcode import Opcode
from ..response import Response


def ResponseHeader(opcode, response=Response.success):
	return construct.Struct(
		'opcode' / construct.Default(construct.Const(opcode, PackEnum(Opcode)), opcode),
		'response' / construct.Switch(
		construct.this.opcode, {
			Opcode.login_challenge: construct.Default(PackEnum(Response), response),
			Opcode.login_proof: construct.Default(PackEnum(Response), response),
			Opcode.realm_list: construct.Pass
		}
	))

