import construct
from enum import Enum

 from prowl.protocol.world.opcode import Opcode
from prowl.protocol.world.packets import ServerHeader
from prowl.utility.construct import PackEnum

class ItemClass(Enum):
    consumable  = 0
    container   = 1
    weapon      = 2
    gem         = 3
    armor       = 4
    reagent     = 5
    projectile  = 6
    trade_good  = 7
    generic     = 8
    recipe      = 9
    money       = 10
    quiver      = 11
    quest       = 12
    key         = 13
    permanent   = 14
    misc        = 15
    glyph       = 16

SMSG_SET_PROFICIENCY = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_SET_PROFICIENCY, 1 + 4),
	'item_class' / PackEnum(ItemClass, construct.Byte),
	'item_subclass_mask' / construct.Int32ul
)