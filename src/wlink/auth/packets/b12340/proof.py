import construct
from wlink.utility.construct import PackEnum

from .header import ResponseHeader
from .opcode import Opcode

ProofRequest = construct.Struct(
	'opcode' / construct.Default(construct.Const(Opcode.login_proof, PackEnum(Opcode)), Opcode.login_proof),
	'client_public' / construct.BytesInteger(32, swapped=True),
	'session_proof' / construct.BytesInteger(20, swapped=True),
	'checksum' / construct.BytesInteger(20, swapped=True),
	'num_keys' / construct.Default(construct.Byte, 0),
	'security_flags' / construct.Default(construct.Byte, 0),
)

ProofResponse = construct.Struct(
	'header' / ResponseHeader(Opcode.login_proof),
	'session_proof_hash' / construct.BytesInteger(20, swapped=True),
	'account_flags' / construct.Default(construct.Int, 32768),
	'survey_id' / construct.Default(construct.Int, 0),
	'login_flags' / construct.Default(construct.Short, 0)
)

