from enum import Enum
from typing import Optional

import construct

from wlink.utility.construct import PackEnum, GuidConstruct
from .headers import ClientHeader, ServerHeader
from .opcode import Opcode
from wlink.guid import Guid, GuidType


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
    emote = 0x0A
    text_emote = 0x0B
    monster_say = 0x0C
    monster_party = 0x0D
    monster_yell = 0x0E
    monster_whisper = 0x0F
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
    skill = 0x1A
    loot = 0x1B
    money = 0x1C
    opening = 0x1D
    tradeskills = 0x1E
    pet_info = 0x1F
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
    raid_boss_whisper = 0x2A
    filtered = 0x2B
    battleground = 0x2C
    battleground_leader = 0x2D
    restricted = 0x2E
    battlenet = 0x2F
    achievement = 0x30
    guild_achievement = 0x31
    arena_points = 0x32
    party_leader = 0x33
    addon = 0xFFFFFFFF


CMSG_MESSAGECHAT = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_MESSAGECHAT, 0),
    "message_type" / PackEnum(MessageType, construct.Int32sl),
    "language" / PackEnum(Language, construct.Int32sl),
    "channel"
    / construct.If(
        construct.this.message_type == MessageType.channel, construct.CString("utf-8")
    ),
    "receiver"
    / construct.If(
        construct.this.message_type == MessageType.whisper, construct.CString("utf-8")
    ),
    "text" / construct.CString("utf-8"),
)


def make_CMSG_MESSAGECHAT(
    text: str,
    message_type,
    language,
    recipient: Optional[str] = None,
    channel: Optional[str] = None,
):
    size = 4 + 4 + len(text)
    if message_type in (MessageType.whisper, MessageType.channel):
        size += max(len(channel), len(recipient))

    return CMSG_MESSAGECHAT.build(
        dict(
            header={"size": size + 5},
            text=text,
            message_type=message_type,
            language=language,
            receiver=recipient,
            channel=channel,
        )
    )


MonsterMessage = construct.Struct(
    "sender" / construct.Prefixed(construct.Int32ul, construct.CString("ascii")),
    "receiver_guid" / GuidConstruct(Guid),
    "receiver"
    / construct.If(
        construct.this.receiver_guid != Guid()
        and construct.this.receiver_guid.type not in (GuidType.player, GuidType.pet),
        construct.Prefixed(construct.Int32ul, construct.CString("ascii")),
    ),
)

WhisperForeign = construct.Struct(
    "sender" / construct.Prefixed(construct.Int32ul, construct.CString("ascii")),
    "receiver_guid" / GuidConstruct(Guid),
)

BGMessage = construct.Struct(
    "receiver_guid" / GuidConstruct(Guid),
    "receiver"
    / construct.If(
        construct.this.receiver_guid != Guid()
        and construct.this.receiver_guid.type != GuidType.player,
        construct.Prefixed(construct.Int32ul, construct.CString("ascii")),
    ),
)

AchievementMessage = construct.Struct(
    "receiver_guid" / GuidConstruct(Guid),
)


def ChannelMessage(gm_chat=False):
    if gm_chat:
        return construct.Struct(
            "sender"
            / construct.Prefixed(construct.Int32ul, construct.CString("ascii")),
            "channel" / construct.CString("ascii"),
            "receiver_guid" / GuidConstruct(Guid),
        )
    else:
        return construct.Struct(
            "channel" / construct.CString("ascii"),
            "receiver_guid" / GuidConstruct(Guid),
        )


def DefaultMessage(gm_chat=False):
    if gm_chat:
        return construct.Struct(
            "sender"
            / construct.Prefixed(construct.Int32ul, construct.CString("ascii")),
            "receiver_guid" / GuidConstruct(Guid),
        )
    else:
        return construct.Struct(
            "receiver_guid" / GuidConstruct(Guid),
        )


def make_messagechat_packet(gm_chat=False):
    return construct.Struct(
        "header"
        / ServerHeader(
            Opcode.SMSG_GM_MESSAGECHAT if gm_chat else Opcode.SMSG_MESSAGECHAT, 0
        ),
        "message_type" / PackEnum(MessageType, construct.Int8sl),
        "language" / PackEnum(Language, construct.Int32sl),
        "sender_guid" / GuidConstruct(Guid),
        "flags" / construct.Default(construct.Int32ul, 0),
        "info"
        / construct.Switch(
            construct.this.message_type,
            {
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
            },
            default=DefaultMessage(gm_chat=gm_chat),
        ),
        "text" / construct.Prefixed(construct.Int32ul, construct.CString("utf-8")),
        "chat_tag" / construct.Byte,  # 4 appears when a GM has their chat tag visible
        "achievement_id"
        / construct.Switch(
            construct.this.message_type,
            {
                MessageType.achievement: construct.Int32ul,
                MessageType.guild_achievement: construct.Int32ul,
            },
        ),
    )


SMSG_GM_MESSAGECHAT = make_messagechat_packet(gm_chat=True)
SMSG_MESSAGECHAT = make_messagechat_packet(gm_chat=False)

# def make_SMSG_MESSAGECHAT() -> SMSG_MESSAGECHAT:
# 	return SMSG_MESSAGECHAT.build(dict())

SMSG_EMOTE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_EMOTE),
    "emote_id" / construct.Int32ul,
    "guid" / GuidConstruct(Guid),
)

__all__ = [
    "SMSG_EMOTE",
    "SMSG_MESSAGECHAT",
    "SMSG_GM_MESSAGECHAT",
    "MessageType",
    "CMSG_MESSAGECHAT",
    "ChannelMessage",
    "AchievementMessage",
    "BGMessage",
    "MonsterMessage",
    "DefaultMessage",
    "WhisperForeign",
    "Language",
]
