from enum import Enum
from typing import List

import construct

from wlink.utility.construct import GuidConstruct, PackEnum
from wlink.world.packets.b12340.character_enum_packets import Gender, CombatClass
from .headers import ServerHeader, ClientHeader
from .opcode import Opcode
from wlink.guid import Guid


class GuildBankData:
    max_tabs = 6
    max_slots = 98


class GuildBankRightsData(Enum):
    view_tab = 1
    put_item = 2
    update_text = 4
    deposit_item = view_tab | put_item
    full = 0xFF


GuildRankData = construct.ByteSwapped(
    construct.Struct(
        "flags" / construct.Int,
        "withdraw_gold_limit" / construct.Int,
        "tab_flags"
        / construct.Array(
            GuildBankData.max_tabs, construct.Sequence(construct.Int, construct.Int)
        ),
    )
)


class MemberStatus(Enum):
    offline = 0
    online = 1
    afk = 2
    dnd = 4
    mobile = 8


RosterMemberData = construct.Struct(
    "guid" / GuidConstruct(Guid),
    "status" / PackEnum(MemberStatus),
    "name" / construct.CString("ascii"),
    "rank_id" / construct.Int32ul,
    "level" / construct.Byte,
    "combat_class" / PackEnum(CombatClass),
    "gender" / PackEnum(Gender),
    "area_id" / construct.Int32ul,
    "last_save"
    / construct.IfThenElse(
        construct.this.status == MemberStatus.offline,
        construct.Float32l,
        construct.Pass,
    ),
    "note" / construct.CString("ascii"),
    "officer_note" / construct.CString("ascii"),
)

CMSG_GUILD_ROSTER = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_ROSTER, 0)
)


def make_CMSG_GUILD_ROSTER():
    return CMSG_GUILD_ROSTER.build(dict())


SMSG_GUILD_ROSTER = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GUILD_ROSTER, 0),
    "total_members" / construct.Int32ul,
    "motd" / construct.CString("ascii"),
    "info" / construct.CString("ascii"),
    "ranks" / construct.PrefixedArray(construct.Int32ul, GuildRankData),
    "members" / construct.Array(construct.this.total_members, RosterMemberData),
)

CMSG_GUILD_CREATE = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_CREATE, 8),
    "guild_name" / construct.CString("ascii"),
)


def make_CMSG_GUILD_CREATE(guild_name: str):
    return CMSG_GUILD_CREATE.build(
        dict(header=dict(size=4 + len(guild_name) + 1), guild_name=guild_name)
    )


CMSG_GUILD_ACCEPT = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_ACCEPT, 0)
)


def make_CMSG_GUILD_ACCEPT():
    return CMSG_GUILD_ACCEPT.build(dict())


CMSG_GUILD_DECLINE = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_DECLINE, 0)
)


def make_CMSG_GUILD_DECLINE():
    return CMSG_GUILD_DECLINE.build(dict())


class GuildMemberDataType(Enum):
    zone_id = 1
    level = 2


class GuildCommandType(Enum):
    create = 0
    invite = 1
    quit = 3
    roster = 5
    promote = 6
    demote = 7
    remove = 8
    change_leader = 10
    edit_motd = 11
    guild_chat = 13
    founder = 14
    change_rank = 16
    public_note = 19
    view_tab = 21
    move_item = 22
    repair = 25


class GuildCommandError(Enum):
    success = 0
    internal_error = 1
    already_in_guild = 2
    already_in_guild_s = 3
    already_invited_to_guild = 4
    already_invited_to_guild_s = 5
    guild_name_invalid = 6
    guild_name_exists = 7
    error_leader_leave = 8
    error_guild_permissions = 8
    player_not_in_guild = 9
    player_not_in_guild_s = 10
    player_not_found_s = 11
    not_allied = 12
    rank_too_high_s = 13
    rank_too_low_s = 14
    ranks_locked = 17
    rank_in_use = 18
    ignoring_you_s = 19
    unknown1 = 20  # Forces roster update
    withdraw_limit = 25
    not_enough_money = 26
    bank_full = 28
    item_not_found = 29


SMSG_GUILD_COMMAND_RESULT = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GUILD_COMMAND_RESULT, 8 + 1),
    "command_type" / PackEnum(GuildCommandType, construct.Int32ul),
    "parameters" / construct.CString("utf-8"),
    "error_code" / PackEnum(GuildCommandError, construct.Int32ul),
)

CMSG_GUILD_INVITE = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_INVITE, 48),
    "name" / construct.PaddedString(48, "utf8"),
)

SMSG_GUILD_INVITE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GUILD_INVITE, 10),
    "sender" / construct.CString("utf8"),
    "guild" / construct.CString("utf8"),
)


def make_SMSG_GUILD_INVITE(sender: str, guild: str):
    return SMSG_GUILD_INVITE.build(
        dict(header=dict(size=len(sender) + len(guild) + 2), sender=sender, guild=guild)
    )


class GuildEventType(Enum):
    promotion = 0
    demotion = 1
    motd = 2
    joined = 3
    left = 4
    removed = 5
    leader_is = 6
    leader_changed = 7
    disbanded = 8
    tabard_change = 9
    rank_updated = 10
    rank_deleted = 11
    signed_on = 12
    signed_off = 13

    bank_bag_slots_changed = 14
    bank_tab_purchased = 15
    bank_tab_updated = 16
    bank_money_set = 17
    bank_tab_and_money_updated = 18
    bank_text_changed = 19


SMSG_GUILD_EVENT = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GUILD_EVENT, 19),
    "type" / PackEnum(GuildEventType),
    # TODO: Figure out what this is
    "parameters"
    / construct.PrefixedArray(construct.Byte, construct.CString(encoding="utf8")),
    "guid"
    / construct.Switch(
        construct.this.type,
        {
            GuildEventType.joined: GuidConstruct(Guid),
            GuildEventType.left: GuidConstruct(Guid),
            GuildEventType.signed_on: GuidConstruct(Guid),
            GuildEventType.signed_off: GuidConstruct(Guid),
        },
    ),
)

CMSG_GUILD_QUERY = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_QUERY, 4),
    "guild_id" / construct.Int32ul,
)


def make_CMSG_GUILD_QUERY(guild_id: int):
    return CMSG_GUILD_QUERY.build(dict(guild_id=guild_id))


SMSG_GUILD_QUERY_RESPONSE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GUILD_QUERY_RESPONSE, 8 * 32 + 200),
    "guild_id" / construct.Int32ul,
    "name" / construct.CString("utf8"),
    "ranks" / construct.Array(10, construct.CString("utf8")),
    "emblem_style" / construct.Int32ul,
    "emblem_color" / construct.Int32ul,
    "border_style" / construct.Int32ul,
    "border_color" / construct.Int32ul,
    "background_color" / construct.Int32ul,
    "num_ranks" / construct.Int32ul,
)


def make_SMSG_GUILD_QUERY_RESPONSE(
    guild_id: int,
    name: str,
    ranks: List[str],
    emblem_style: int,
    emblem_color: int,
    border_style: int,
    border_color: int,
    background_color: int,
    num_ranks: int,
):
    ranks_size = sum((len(s) + 1 for s in ranks))
    return SMSG_GUILD_QUERY_RESPONSE.build(
        dict(
            header=dict(size=2 + len(name) + 1 + ranks_size + 4 * 6),
            guild_id=guild_id,
            name=name,
            ranks=ranks,
            emblem_style=emblem_style,
            emblem_color=emblem_color,
            border_style=border_style,
            border_color=border_color,
            background_color=background_color,
            num_ranks=num_ranks,
        )
    )


CMSG_GUILD_SET_OFFICER_NOTE = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_SET_OFFICER_NOTE),
    "player" / construct.CString("utf8"),
    "note" / construct.CString("utf8"),
)

CMSG_GUILD_SET_PUBLIC_NOTE = construct.Struct(
    "header"
    / ClientHeader(
        Opcode.CMSG_GUILD_SET_PUBLIC_NOTE,
    ),
    "player" / construct.CString("utf8"),
    "note" / construct.CString("utf8"),
)


def make_CMSG_GUILD_SET_PUBLIC_NOTE(player: str, note: str):
    return CMSG_GUILD_SET_PUBLIC_NOTE.build(
        dict(header=dict(size=4 + 2 * (len(player) + 1)), player=player, note=note)
    )


CMSG_GUILD_MOTD = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_INFO, 0),
    "motd" / construct.CString("utf8"),  # max length is 128 (TODO: check for overflow)
)

CMSG_GUILD_INFO = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_INFO, 0),
)


def make_CMSG_GUILD_INFO():
    return CMSG_GUILD_INFO.build(dict())


SMSG_GUILD_INFO = construct.Struct(
    "header"
    / ServerHeader(
        Opcode.SMSG_GUILD_INFO, construct.len_(construct.this.name) + 4 + 4 + 4
    ),
    "name" / construct.CString("utf8"),
    "created" / construct.Int32ul,
    "num_members" / construct.Int32ul,
    "num_accounts" / construct.Int32ul,
)

CMSG_GUILD_INFO_TEXT = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GUILD_INFO_TEXT),
    "info" / construct.CString("utf8"),  # max length is 500 (TODO: check for overflow)
)


def make_CMSG_GUILD_INFO_TEXT(info: str):
    return CMSG_GUILD_INFO_TEXT.build(
        dict(header=dict(size=4 + len(info) + 1), info=info)
    )


CMSG_GUILD_EVENT_LOG_QUERY = construct.Struct(
    "header" / ClientHeader(Opcode.MSG_GUILD_EVENT_LOG_QUERY),
)


def make_CMSG_GUILD_EVENT_LOG_QUERY():
    return CMSG_GUILD_EVENT_LOG_QUERY.build(dict())


SMSG_GUILD_EVENT_LOG_QUERY = construct.Struct(
    "header" / ServerHeader(Opcode.MSG_GUILD_EVENT_LOG_QUERY),
)


def make_SMSG_GUILD_EVENT_LOG_QUERY():
    return SMSG_GUILD_EVENT_LOG_QUERY.build(dict())


__all__ = [
    "make_SMSG_GUILD_EVENT_LOG_QUERY",
    "make_CMSG_GUILD_EVENT_LOG_QUERY",
    "make_CMSG_GUILD_QUERY",
    "make_CMSG_GUILD_INFO_TEXT",
    "make_CMSG_GUILD_INFO",
    "make_SMSG_GUILD_INVITE",
    "make_CMSG_GUILD_ACCEPT",
    "make_CMSG_GUILD_ROSTER",
    "make_CMSG_GUILD_DECLINE",
    "make_CMSG_GUILD_CREATE",
    "make_CMSG_GUILD_SET_PUBLIC_NOTE",
    "CMSG_GUILD_EVENT_LOG_QUERY",
    "CMSG_GUILD_QUERY",
    "CMSG_GUILD_DECLINE",
    "CMSG_GUILD_CREATE",
    "CMSG_GUILD_MOTD",
    "CMSG_GUILD_INVITE",
    "CMSG_GUILD_ACCEPT",
    "CMSG_GUILD_ROSTER",
    "CMSG_GUILD_INFO_TEXT",
    "CMSG_GUILD_INFO",
    "CMSG_GUILD_SET_PUBLIC_NOTE",
    "CMSG_GUILD_SET_OFFICER_NOTE",
    "SMSG_GUILD_EVENT",
    "SMSG_GUILD_EVENT_LOG_QUERY",
    "SMSG_GUILD_INFO",
    "SMSG_GUILD_INVITE",
    "SMSG_GUILD_ROSTER",
    "SMSG_GUILD_COMMAND_RESULT",
    "SMSG_GUILD_QUERY_RESPONSE",
    "GuildEventType",
    "GuildMemberDataType",
    "GuildCommandType",
    "GuildBankRightsData",
    "GuildRankData",
    "GuildBankData",
    "RosterMemberData",
    "GuildCommandError",
    "MemberStatus",
]
