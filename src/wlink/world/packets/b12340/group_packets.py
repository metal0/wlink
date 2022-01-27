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

CMSG_GROUP_DISBAND = construct.Struct('header' / ClientHeader(Opcode.CMSG_GROUP_DISBAND, 0))
SMSG_GROUP_DESTROYED = construct.Struct('header' / ServerHeader(Opcode.SMSG_GROUP_DESTROYED, 0))

CMSG_GROUP_UNINVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_UNINVITE),
	'member' / construct.CString('utf8'),
	construct.Padding(4),
)

CMSG_GROUP_UNINVITE_GUID = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_UNINVITE_GUID),
	'guid' / GuidConstruct(Guid),
	'reason' / construct.CString('utf8')
)

SMSG_GROUP_UNINVITE = construct.Struct('header' / ServerHeader(Opcode.SMSG_GROUP_UNINVITE, 0))

# SMSG_GROUP_CANCEL = construct.Struct(
# 	'header' / ServerHeader(Opcode.SMSG_GROUP_CANCEL),
# )

CMSG_GROUP_CANCEL = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_CANCEL, 0),
)

CMSG_GROUP_DECLINE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_DECLINE, 0),
)

SMSG_GROUP_DECLINE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_DECLINE, 4),
	'decliner' / construct.CString('utf8'),
)

CMSG_GROUP_ACCEPT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_ACCEPT, 4),
	construct.Padding(4)
)

CMSG_GROUP_INVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_INVITE, 10),
	'invitee' / construct.CString('utf8'),
	construct.Padding(4)
)

SMSG_GROUP_INVITE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_INVITE, 10),
	'can_accept' / construct.Flag,
	'inviter' / construct.CString('utf8'),
	construct.Padding(4 + 1 + 4)
)

SMSG_GROUP_JOINED_BATTLEGROUND = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_JOINED_BATTLEGROUND),
	'id' / construct.Int32ul
)

GroupMemberInfo = construct.Struct(
	'name' / construct.CString('utf8'),
	'guid' / GuidConstruct(Guid),
	'online' / construct.Flag,
	'group_id' / construct.Byte,
	'flags' / construct.Byte,
	'roles' / construct.Byte,
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
	return _old_to_str(self).replace('GroupType.', '')

GroupType.__str__ = _to_str

SMSG_GROUP_LIST = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_LIST),
	'type' / construct.FlagsEnum(construct.Byte, GroupType),
	'group' / construct.Byte,
	'flags' / construct.Byte,
	'roles' / construct.Byte,
		construct.If(construct.this.type.lfg,
		construct.Struct(
			'lfg_dungeon_state' / construct.Byte,
			'lfg_dungeon_guid' / construct.Int,
		)
	),
	'guid' / GuidConstruct(Guid),
	'total_num_groups' / construct.Int32ul,
	'size' / construct.Int32ul,
	'members' / construct.Array(construct.this.size, GroupMemberInfo),
	'leader_guid' / GuidConstruct(Guid),
	construct.If(
		construct.this.size > 0,
		construct.Struct(
			'loot_method' / construct.Byte,
			'looter_guid' / GuidConstruct(Guid),
			'loot_threshold' / construct.Byte,
			'dungeon_difficulty' / construct.Byte,
			'raid_difficulty' / construct.Byte,
			'dynamic_raid_difficulty' / construct.Byte,
		)
	)
)

# SMSG_PARTY_MEMBER_STATS = construct.Struct(
# 	'header' / ServerHeader(Opcode.SMSG_PARTY_MEMBER_STATS),
# 	'guid' / PackGuid(Guid),
# 	'update_flags' / construct.FlagsEnum(construct.Int32ul,)
# )