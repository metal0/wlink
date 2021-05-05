import construct

from wlink import Guid
from wlink.utility.construct import PackGuid
from wlink.world import Opcode
from wlink.world.packets import ServerHeader


def MSG_MOVE_TELEPORT_ACK(header_type):
    return construct.Struct(
        'header' / header_type,
        'mover_guid' / PackGuid(Guid),
        'flags' / construct.Int32ul,
        'time' / construct.Int32ul
    )

SMSG_MOVE_TELEPORT_ACK = MSG_MOVE_TELEPORT_ACK(ServerHeader(Opcode.MSG_MOVE_TELEPORT_ACK, 20))