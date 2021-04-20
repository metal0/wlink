from enum import Enum

import construct

from .headers import ClientHeader, ServerHeader
from wlink.world.opcode import Opcode
from wlink.guid import Guid
from ...utility.construct import GuidConstruct, PackEnum

CMSG_GROUP_ACCEPT = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_ACCEPT, 4),
	construct.Padding(4)
)

CMSG_GROUP_INVITE = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_GROUP_INVITE, 10),
	'invitee' / construct.CString('ascii'),
	construct.Padding(4)
)

SMSG_GROUP_INVITE = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_INVITE, 10),
	'in_group' / construct.Flag,
	'inviter' / construct.CString('ascii'),
	construct.Padding(4 + 1 + 4)
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
	normal = 0
	bg = 1
	raid = 2
	bg_raid = bg | raid
	lfg_restricted = 4
	lfg = 8

SMSG_GROUP_LIST = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_GROUP_LIST),
	'type' / PackEnum(GroupType),
	'group' / construct.Byte,
	'flags' / construct.Byte,
	'roles' / construct.Byte,
		construct.If(construct.this.type == GroupType.lfg,
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
		construct.this.size - 1 != 0,
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
