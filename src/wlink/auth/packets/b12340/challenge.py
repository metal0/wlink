import time
import construct

from wlink.utility.construct import UpperPascalString, IPv4Address, PaddedStringByteSwapped, \
    VersionString, PackEnum

from .header import ResponseHeader, Response
from .opcode import Opcode

ChallengeRequest = construct.Struct(
    'header' / ResponseHeader(Opcode.login_challenge, Response.db_busy),
    'size' / construct.ByteSwapped(
        construct.Default(construct.Short, 30 + construct.len_(construct.this.account_name))),
    'game' / construct.Default(construct.PaddedString(4, 'utf8'), 'WoW'),
    'version' / construct.Default(VersionString(num_bytes=3), '3.3.5'),
    'build' / construct.Default(construct.Int16ul, 12340),
    'architecture' / construct.Default(PaddedStringByteSwapped(4), 'x86'),
    'os' / construct.Default(PaddedStringByteSwapped(4), 'OSX'),
    'country' / construct.Default(PaddedStringByteSwapped(4), 'enUS'),
    'timezone_bias' / construct.Default(construct.ByteSwapped(construct.Int32sb), int(-time.timezone / 60)),
    'ip' / construct.Default(IPv4Address, '127.0.0.1'),
    'account_name' / UpperPascalString('utf8'),
)

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
