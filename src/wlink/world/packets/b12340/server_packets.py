from enum import Enum

import construct

from wlink.utility.construct import PackEnum
from .headers import ServerHeader
from .opcode import Opcode


class ServerMessageType(Enum):
    shutdown_time = 1
    restart_time = 2
    custom = 3
    shutdown_cancelled = 4
    restart_cancelled = 5


SMSG_SERVER_MESSAGE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_SERVER_MESSAGE, 50),
    "type" / PackEnum(ServerMessageType),
    "text" / construct.CString("ascii"),
)

SMSG_NOTIFICATION = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_NOTIFICATION, 1),
    "message" / construct.CString("ascii"),
)

SMSG_MOTD = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_MOTD, 4),
    "lines" / construct.PrefixedArray(construct.Int32ul, construct.CString("ascii")),
)


def make_SMSG_MOTD(lines):
    if type(lines) is str:
        lines = (lines,)

    size = 2 + 4
    for line in lines:
        size += len(line) + 1

    return SMSG_MOTD.build(dict(header=dict(size=size), lines=lines))


__all__ = [
    "SMSG_MOTD",
    "SMSG_NOTIFICATION",
    "SMSG_SERVER_MESSAGE",
    "ServerMessageType",
    "make_SMSG_MOTD",
]
