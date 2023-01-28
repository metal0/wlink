import construct

from wlink.guid import Guid
from wlink.utility.construct import GuidConstruct
from wlink.world.packets.b12340.opcode import Opcode
from wlink.world.packets.b12340.headers import ServerHeader

SMSG_INVALIDATE_PLAYER = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_INVALIDATE_PLAYER),
    "player_guid" / GuidConstruct(Guid),
)

__all__ = ["SMSG_INVALIDATE_PLAYER"]
