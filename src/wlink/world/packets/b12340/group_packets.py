from enum import Enum

import construct

from .headers import ClientHeader, ServerHeader
from .opcode import Opcode
from wlink.guid import Guid
from wlink.utility.construct import GuidConstruct, NegatedFlag

# CMSG_GROUP_SET_LEADER = 0x078
# SMSG_GROUP_SET_LEADER = 0x079
# CMSG_LOOT_METHOD = 0x07A
# SMSG_PARTY_MEMBER_STATS = 0x07E
# SMSG_PARTY_COMMAND_RESULT = 0x07F
# UMSG_UPDATE_GROUP_MEMBERS = 0x080

CMSG_GROUP_DISBAND = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GROUP_DISBAND, 0)
)


def make_CMSG_GROUP_DISBAND():
    return CMSG_GROUP_DISBAND.build(dict())


SMSG_GROUP_DESTROYED = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GROUP_DESTROYED, 0)
)


def make_SMSG_GROUP_DESTROYED():
    return SMSG_GROUP_DESTROYED.build(dict())


CMSG_GROUP_UNINVITE = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GROUP_UNINVITE),
    "member" / construct.CString("utf8"),
    construct.Padding(4),
)


def make_CMSG_GROUP_UNINVITE(member: str):
    return CMSG_GROUP_UNINVITE.build(
        dict(header=dict(size=4 + len(member) + 1 + 4), member=member)
    )


CMSG_GROUP_UNINVITE_GUID = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GROUP_UNINVITE_GUID),
    "guid" / GuidConstruct(Guid),
    "reason" / construct.CString("utf8"),
)


def make_CMSG_GROUP_UNINVITE_GUID(member: str, reason: str):
    return CMSG_GROUP_UNINVITE_GUID.build(
        dict(
            header=dict(size=4 + len(reason) + 1 + GuidConstruct(Guid).sizeof()),
            guid=member,
            reason=reason,
        )
    )


SMSG_GROUP_UNINVITE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GROUP_UNINVITE, 0)
)

# SMSG_GROUP_CANCEL = construct.Struct(
# 	'header' / ServerHeader(Opcode.SMSG_GROUP_CANCEL),
# )

CMSG_GROUP_CANCEL = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GROUP_CANCEL, 0),
)


def make_CMSG_GROUP_CANCEL():
    return CMSG_GROUP_CANCEL.build(dict())


CMSG_GROUP_DECLINE = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GROUP_DECLINE, 0),
)


def make_CMSG_GROUP_DECLINE():
    return CMSG_GROUP_DECLINE.build(dict())


SMSG_GROUP_DECLINE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GROUP_DECLINE, 4),
    "decliner" / construct.CString("utf8"),
)


def make_SMSG_GROUP_DECLINE(decliner: str):
    return SMSG_GROUP_DECLINE.build(
        dict(header=dict(size=4 + len(decliner) + 1), decliner=decliner)
    )


CMSG_GROUP_ACCEPT = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GROUP_ACCEPT, 4), construct.Padding(4)
)


def make_CMSG_GROUP_ACCEPT():
    return CMSG_GROUP_ACCEPT.build(dict())


CMSG_GROUP_INVITE = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_GROUP_INVITE, 10),
    "recipient" / construct.CString("utf8"),
    construct.Padding(4),
)


def make_CMSG_GROUP_INVITE(recipient: str):
    return CMSG_GROUP_INVITE.build(
        dict(
            header=dict(size=4 + len(recipient) + 1 + 4),
            recipient=recipient,
        )
    )


SMSG_GROUP_INVITE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GROUP_INVITE, 10),
    "can_accept" / construct.Flag,
    "sender" / construct.CString("utf8"),
    construct.Padding(4 + 1 + 4),
)


def make_SMSG_GROUP_INVITE(sender: str, in_group=False):
    return SMSG_GROUP_INVITE.build(
        dict(
            header=dict(size=1 + len(sender) + 4 + 1 + 4),
            in_group=in_group,
            sender=sender,
        )
    )


SMSG_GROUP_JOINED_BATTLEGROUND = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GROUP_JOINED_BATTLEGROUND, body_size=4),
    "id" / construct.Int32ul,
)


def make_SMSG_GROUP_JOINED_BATTLEGROUND(inviter: str, in_group=False):
    return SMSG_GROUP_JOINED_BATTLEGROUND.build(
        dict(
            id=id,
        )
    )


GroupMemberInfo = construct.Struct(
    "name" / construct.CString("utf8"),
    "guid" / GuidConstruct(Guid),
    "online" / construct.Flag,
    "group_id" / construct.Byte,
    "flags" / construct.Byte,
    "roles" / construct.Byte,
)


class GroupType(Enum):
    party = 0
    bg = 1
    raid = 2
    bg_raid = bg | raid
    lfg_restricted = 4
    lfg = 8


_old_to_str = GroupType.__str__


def _to_str(self):
    return _old_to_str(self).replace("GroupType.", "")


GroupType.__str__ = _to_str

SMSG_GROUP_LIST = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_GROUP_LIST),
    "type" / construct.FlagsEnum(construct.Byte, GroupType),
    "group" / construct.Byte,
    "flags" / construct.Byte,
    "roles" / construct.Byte,
    construct.If(
        construct.this.type.lfg,
        construct.Struct(
            "lfg_dungeon_state" / construct.Byte,
            "lfg_dungeon_guid" / construct.Int,
        ),
    ),
    "guid" / GuidConstruct(Guid),
    "total_num_groups" / construct.Int32ul,
    "size" / construct.Int32ul,
    "members" / construct.Array(construct.this.size, GroupMemberInfo),
    "leader_guid" / GuidConstruct(Guid),
    construct.If(
        construct.this.size > 0,
        construct.Struct(
            "loot_method" / construct.Byte,
            "looter_guid" / GuidConstruct(Guid),
            "loot_threshold" / construct.Byte,
            "dungeon_difficulty" / construct.Byte,
            "raid_difficulty" / construct.Byte,
            "dynamic_raid_difficulty" / construct.Byte,
        ),
    ),
)

# SMSG_PARTY_MEMBER_STATS = construct.Struct(
# 	'header' / ServerHeader(Opcode.SMSG_PARTY_MEMBER_STATS),
# 	'guid' / PackGuid(Guid),
# 	'update_flags' / construct.FlagsEnum(construct.Int32ul,)
# )

__all__ = [
    "SMSG_GROUP_LIST",
    "SMSG_GROUP_UNINVITE",
    "SMSG_GROUP_DECLINE",
    "SMSG_GROUP_DESTROYED",
    "SMSG_GROUP_INVITE",
    "SMSG_GROUP_JOINED_BATTLEGROUND",
    "CMSG_GROUP_ACCEPT",
    "CMSG_GROUP_CANCEL",
    "CMSG_GROUP_INVITE",
    "CMSG_GROUP_DECLINE",
    "CMSG_GROUP_DISBAND",
    "CMSG_GROUP_UNINVITE",
    "CMSG_GROUP_UNINVITE_GUID",
    "GroupType",
    "GroupMemberInfo",
    "make_CMSG_GROUP_INVITE",
    "make_SMSG_GROUP_INVITE",
    "make_SMSG_GROUP_DECLINE",
    "make_CMSG_GROUP_UNINVITE",
    "make_CMSG_GROUP_UNINVITE_GUID",
    "make_CMSG_GROUP_CANCEL",
    "make_CMSG_GROUP_ACCEPT",
    "make_CMSG_GROUP_DECLINE",
    "make_CMSG_GROUP_DISBAND",
    "make_SMSG_GROUP_DESTROYED",
    "make_SMSG_GROUP_JOINED_BATTLEGROUND",
]
