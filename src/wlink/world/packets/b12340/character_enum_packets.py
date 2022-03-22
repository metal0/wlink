from enum import Enum

import construct

from wlink.utility.construct import PackEnum, GuidConstruct, Coordinates
from .headers import ServerHeader, ClientHeader
from .opcode import Opcode
from wlink.guid import Guid

class Race(Enum):
	none = 0
	human = 1
	orc = 2
	dwarf = 3
	night_elf = 4
	undead = 5
	tauren = 6
	gnome = 7
	troll = 8
	blood_elf = 10
	draenai = 11

class CombatClass(Enum):
	none = 0
	warrior = 1
	paladin = 2
	hunter = 3
	rogue = 4
	priest = 5
	death_knight = 6
	shaman = 7
	mage = 8
	warlock = 9
	druid = 11

class Gender(Enum):
	male = 0
	female = 1
	none = 2

DisplayInfo = construct.Struct(
	'skin' / construct.Byte,
	'face' / construct.Byte,
	'hair_style' / construct.Byte,
	'hair_color' / construct.Byte,
	'facial_hair' / construct.Byte,
)

PetInfo = construct.Struct(
	'display_id' / construct.Int32ul,
	'level' / construct.Int32ul,
	'family' / construct.Int32ul,
)

ItemInfo = construct.Struct(
	'display_id' / construct.Int32ul,
	'inventory_type' / construct.Byte,
	'enchant_aura_id' / construct.Int32ul,
)

BagInfo = construct.Struct(
	'display_id' / construct.Int32ul,
	'inventory_type' / construct.Byte,
	'enchant_id' / construct.Int32ul,
)

CharacterInfo = construct.Struct(
	'guid' / GuidConstruct(Guid),
	'name' / construct.CString('utf8'),
	'race' / PackEnum(Race),
	'combat_class' / PackEnum(CombatClass),
	'gender' / PackEnum(Gender),
	'skin' / construct.Byte,
	'face' / construct.Byte,
	'hair_style' / construct.Byte,
	'hair_color' / construct.Byte,
	'facial_hair' / construct.Byte,
	'level' / construct.Byte,
	'zone' / construct.Int32ul,
	'map' / construct.Int32ul,
	'position' / construct.ByteSwapped(Coordinates()),
	'guild_guid' / construct.Int32ul,
	'flags' / construct.Int32ul,
	'customization_flags' / construct.Int32ul,
	# 'slot' / construct.Byte,
	'is_first_login' / construct.Flag,
	'pet' / PetInfo,
	'items' / construct.Array(19, ItemInfo),
	'bags' / construct.Array(4, BagInfo)
)

CMSG_CHAR_CREATE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_CHAR_CREATE),
	'name' / construct.CString('utf8'),
	'race' / PackEnum(Race),
	'combat_class' / PackEnum(CombatClass),
	'gender' / PackEnum(Gender),
	'skin' / construct.Byte,
	'face' / construct.Byte,
	'hair_style' / construct.Byte,
	'hair_color' / construct.Byte,
	'facial_hair' / construct.Byte,
	'outfit_id' / construct.Byte,
)

def make_CMSG_CHAR_CREATE(self, name: str,
	race=Race.human,
	combat_class=CombatClass.rogue,
	gender=Gender.male,
	skin=0,
	face=0,
	hair_style=0,
	hair_color=0,
	facial_hair=0,
	outfit_id=0,
):
	return CMSG_CHAR_CREATE.build(dict(
		header=dict(size=(len(name) + 1) + 9 + 4),
		name=name,
		race=race,
		combat_class=combat_class,
		gender=gender,
		skin=skin,
		face=face,
		hair_style=hair_style,
		hair_color=hair_color,
		facial_hair=facial_hair,
		outfit_id=outfit_id,
	))

SMSG_CHAR_CREATE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CHAR_CREATE),
)

CMSG_CHAR_ENUM = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_CHAR_ENUM, 0),
)

def send_CMSG_CHAR_ENUM():
	return CMSG_CHAR_ENUM.build(dict())

SMSG_CHAR_ENUM = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CHAR_ENUM, 4 + construct.len_(construct.this.characters)),
	'characters' / construct.PrefixedArray(construct.Byte, CharacterInfo),
)

def make_SMSG_CHAR_ENUM(characters=None):
	raise NotImplemented()
	# return SMSG_CHAR_ENUM.build(dict())


CMSG_CHAR_RENAME = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_CHAR_RENAME),
	'guid' / GuidConstruct(Guid),
	'new_name' / construct.CString('utf8')
)


def make_CMSG_CHAR_RENAME(new_name: str, guid):
	"""
	Sends an encrypted CMSG_CHAR_RENAME packet.
	:return: None.
	"""
	return CMSG_CHAR_RENAME.build(dict(
		header=dict(size=len(new_name) + 1 + 8 + 4),
		guid=guid,
		new_name=new_name
	))

RenameInfo = construct.Struct(
	'guid' / GuidConstruct(Guid),
	'new_name' / construct.CString('utf8')
)

class CharacterNameResponse(Enum):
	success = 0x57
	failure = 0x58
	no_name = 0x59
	too_share = 0x5A
	too_long = 0x5B
	invalid_character = 0x5C
	mixed_languages = 0x5D
	profane = 0x5E
	reserved = 0x5F
	invalid_apostrophes = 0x60
	multiple_apostrophes = 0x61
	three_consecutive = 0x62
	invalid_space = 0x63
	consecutive_spaces = 0x64
	russian_consecutive_silent_characters = 0x65
	russian_silent_character_at_beginning_or_end = 0x66
	declension_doesnt_match_base_name = 0x67

SMSG_CHAR_RENAME = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_CHAR_RENAME),
	'response' / PackEnum(CharacterNameResponse),
	'info' / construct.IfThenElse(
		(construct.this.response == CharacterNameResponse.no_name or
			construct.this.response == CharacterNameResponse.reserved), # also when == CHAR_CREATE_ERROR
		construct.Pass,
		RenameInfo,
	)
)