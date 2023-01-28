import construct
from wlink.utility.construct import PackEnum

from .header import ResponseHeader, Response
from .opcode import Opcode

ProofRequest = construct.Struct(
    "opcode"
    / construct.Default(
        construct.Const(Opcode.login_proof, PackEnum(Opcode)), Opcode.login_proof
    ),
    "client_public" / construct.BytesInteger(32, swapped=True),
    "session_proof" / construct.BytesInteger(20, swapped=True),
    "checksum" / construct.BytesInteger(20, swapped=True),
    "num_keys" / construct.Default(construct.Byte, 0),
    "security_flags" / construct.Default(construct.Byte, 0),
)


def make_proof_request(
    client_public: int,
    session_proof: int,
    checksum: int = 4601254584545541958749308449812234986282924510,
    num_keys: int = 0,
    security_flags: int = 0,
):
    return ProofRequest.build(
        dict(
            client_public=client_public,
            session_proof=session_proof,
            checksum=checksum,
            num_keys=num_keys,
            security_flags=security_flags,
        )
    )


ProofResponse = construct.Struct(
    "header" / ResponseHeader(Opcode.login_proof),
    "session_proof_hash" / construct.BytesInteger(20, swapped=True),
    "account_flags" / construct.Default(construct.Int, 32768),
    "survey_id" / construct.Default(construct.Int, 0),
    "login_flags" / construct.Default(construct.Short, 0),
)


def make_proof_response(
    response: Response,
    session_proof_hash: int = 0,
    account_flags=32768,
    survey_id=0,
    login_flags=0,
):
    return ProofResponse.build(
        dict(
            header=dict(response=response),
            session_proof_hash=session_proof_hash,
            account_flags=account_flags,
            survey_id=survey_id,
            login_flags=login_flags,
        )
    )
