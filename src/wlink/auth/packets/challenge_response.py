import construct

from .header import ResponseHeader
from ..response import Response
from ..opcode import Opcode
from ...utility.construct import PackEnum

ChallengeResponse = construct.Struct(
	'header' / ResponseHeader(Opcode.login_challenge),
	'response' / construct.Default(PackEnum(Response), Response.success),

	'rc4' / construct.IfThenElse(
		construct.this.response == Response.success,
		construct.Struct(
			'server_public' / construct.BytesInteger(32, swapped=True),
			'generator_length' / construct.Default(construct.Byte, 1),
			'generator' / construct.Default(construct.BytesInteger(construct.this.generator_length, swapped=True), 7),

			'prime_length' / construct.Default(construct.Byte, 32),
			'prime' / construct.BytesInteger(construct.this.prime_length, swapped=True),
			'salt' / construct.BytesInteger(32, swapped=True),
			'checksum' / construct.BytesInteger(16, swapped=True),
			'security_flag' / construct.Default(construct.Byte, 0),
		),
		construct.Pass
	)
)
