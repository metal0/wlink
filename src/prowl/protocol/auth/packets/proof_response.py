import construct

from . import ResponseHeader
from ..opcode import Opcode

ProofResponse = construct.Struct(
	'header' / ResponseHeader(Opcode.login_proof),
	'session_proof_hash' / construct.BytesInteger(20, swapped=True),
	'account_flags' / construct.Default(construct.Int, 32768),
	'survey_id' / construct.Default(construct.Int, 0),
	'login_flags' / construct.Default(construct.Short, 0)
)

