from enum import Enum

import construct

from prowl.utility.construct import PackEnum, GuidConstruct
from .headers import ClientHeader, ServerHeader
from prowl.protocol.world.opcode import Opcode
from prowl.guid import Guid, GuidType


class Language(Enum):
	universal = 0
	orcish = 1
	darnassian = 2
	taurahe = 3
	dwarvish = 6
	common = 7
	demonic = 8
	tita = 9
	thalassian = 10
	draconic = 11
	kalimag = 12
	gnomish = 13
	troll = 14
	gutterspeak = 33
	draenai = 35
	zombie = 36
	gnomish_binary = 37
	goblin_binary = 38
	worgen = 39
	goblin = 40
	addon = -1

class MessageType(Enum):
	system = 0x00
	say = 0x01
	party = 0x02
	raid = 0x03
	guild = 0x04
	officer = 0x05
	yell = 0x06
	whisper = 0x07
	whisper_foreign = 0x08
	whisper_inform = 0x09
	emote = 0x0a
	text_emote = 0x0b
	monster_say = 0x0c
	monster_party = 0x0d
	monster_yell = 0x0e
	monster_whisper = 0x0f
	monster_emote = 0x10
	channel = 0x11
	channel_join = 0x12
	channel_leave = 0x13
	channel_list = 0x14
	channel_notice = 0x15
	channel_notice_user = 0x16
	afk = 0x17
	dnd = 0x18
	ignored = 0x19
	skill = 0x1a
	loot = 0x1b
	money = 0x1c
	opening = 0x1d
	tradeskills = 0x1e
	pet_info = 0x1f
	combat_misc_info = 0x20
	combat_xp_gain = 0x21
	combat_honor_gain = 0x22
	combat_faction_change = 0x23
	bg_system_neutral = 0x24
	bg_system_alliance = 0x25
	bg_system_horde = 0x26
	raid_leader = 0x27
	raid_warning = 0x28
	raid_boss_emote = 0x29
	raid_boss_whisper = 0x2a
	filtered = 0x2b
	battleground = 0x2c
	battleground_leader = 0x2d
	restricted = 0x2e
	battlenet = 0x2f
	achievement = 0x30
	guild_achievement = 0x31
	arena_points = 0x32
	party_leader = 0x33
	addon = 0xFFFFFFFF

CMSG_MESSAGECHAT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_MESSAGECHAT, 0),
	'message_type' / PackEnum(MessageType, construct.Int32sl),
	'language' / PackEnum(Language, construct.Int32sl),
	'channel' / construct.If(
		construct.this.message_type == MessageType.channel,
		construct.CString('utf-8')
	),
	'receiver' / construct.If(
		construct.this.message_type == MessageType.whisper,
		construct.CString('utf-8')
	),
	'text' / construct.CString('utf-8')
)

MonsterMessage = construct.Struct(
	'sender' / construct.Prefixed(construct.Int32ul, construct.CString('ascii')),
	'receiver_guid' / GuidConstruct(Guid),
	'receiver' / construct.If(
		construct.this.receiver_guid != Guid() and construct.this.receiver_guid.type not in (GuidType.player, GuidType.pet),
		construct.Prefixed(construct.Int32ul, construct.CString('ascii'))
	),
)

WhisperForeign = construct.Struct(
	'sender' / construct.Prefixed(construct.Int32ul, construct.CString('ascii')),
	'receiver_guid' / GuidConstruct(Guid),
)

BGMessage = construct.Struct(
	'receiver_guid' / GuidConstruct(Guid),
	'receiver' / construct.If(
		construct.this.receiver_guid != Guid() and construct.this.receiver_guid.type != GuidType.player,
		construct.Prefixed(construct.Int32ul, construct.CString('ascii'))
	),
)

AchievementMessage = construct.Struct(
	'receiver_guid' / GuidConstruct(Guid),
)


def ChannelMessage(gm_chat=False):
	if gm_chat:
		return construct.Struct(
			'sender' / construct.Prefixed(construct.Int32ul, construct.CString('ascii')),
			'channel' / construct.CString('ascii'),
			'receiver_guid' / GuidConstruct(Guid),
		)
	else:
		return construct.Struct(
			'channel' / construct.CString('ascii'),
			'receiver_guid' / GuidConstruct(Guid),
		)

def DefaultMessage(gm_chat=False):
	if gm_chat:
		return construct.Struct(
			'sender' / construct.Prefixed(construct.Int32ul, construct.CString('ascii')),
			'receiver_guid' / GuidConstruct(Guid),
		)
	else:
		return construct.Struct(
			'receiver_guid' / GuidConstruct(Guid),
		)

def make_messagechat_packet(gm_chat=False):
	return construct.Struct(
		'header' / ServerHeader(Opcode.SMSG_GM_MESSAGECHAT if gm_chat else Opcode.SMSG_MESSAGECHAT, 0),
		'message_type' / PackEnum(MessageType, construct.Int8sl),
		'language' / PackEnum(Language, construct.Int32sl),
		'sender_guid' / GuidConstruct(Guid),
		'flags' / construct.Default(construct.Int32ul, 0),
		'info' / construct.Switch(
			construct.this.message_type, {
				MessageType.monster_say: MonsterMessage,
				MessageType.monster_emote: MonsterMessage,
				MessageType.monster_party: MonsterMessage,
				MessageType.monster_yell: MonsterMessage,
				MessageType.monster_whisper: MonsterMessage,
				MessageType.raid_boss_emote: MonsterMessage,
				MessageType.raid_boss_whisper: MonsterMessage,

				MessageType.whisper_foreign: WhisperForeign,

				MessageType.bg_system_alliance: BGMessage,
				MessageType.bg_system_horde: BGMessage,
				MessageType.bg_system_neutral: BGMessage,

				MessageType.achievement: AchievementMessage,
				MessageType.guild_achievement: AchievementMessage,

				MessageType.channel: ChannelMessage(gm_chat=gm_chat),

			}, default=DefaultMessage(gm_chat=gm_chat)
		),

		'text' / construct.Prefixed(construct.Int32ul, construct.CString('utf-8')),
		'chat_tag' / construct.Byte, # 4 appears when a GM has their chat tag visible
		'achievement_id' / construct.Switch(
			construct.this.message_type, {
				MessageType.achievement: construct.Int32ul,
				MessageType.guild_achievement: construct.Int32ul,
			}
		)
	)

SMSG_GM_MESSAGECHAT = make_messagechat_packet(gm_chat=True)
SMSG_MESSAGECHAT = make_messagechat_packet(gm_chat=False)
