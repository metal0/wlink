import construct

from wlink.guid import Guid
from wlink.utility.construct import GuidConstruct
from wlink.world import Opcode
from wlink.world.packets import ServerHeader

SMSG_INVALIDATE_PLAYER = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_INVALIDATE_PLAYER),
    'player_guid' / GuidConstruct(Guid)
)