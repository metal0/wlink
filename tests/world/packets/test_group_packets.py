from wlink import Guid
from wlink.world.packets import SMSG_GROUP_INVITE, Opcode, SMSG_GROUP_LIST, GroupType


def test_group_invite():
	data = b'\x00\x10o\x00\x01Act\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	packet = SMSG_GROUP_INVITE.parse(data)
	print(packet)

	assert packet.header.opcode == Opcode.SMSG_GROUP_INVITE
	assert packet.can_accept
	assert packet.inviter == 'Act'

def test_group_list():
	data = b'\x00>}\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00P\x1fC\x00\x00\x00\x01\x00\x00\x00Imbued\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00'
	packet = SMSG_GROUP_LIST.parse(data)
	print(packet)

	assert packet.type.party
	assert packet.group == 0
	assert packet.flags == 0
	assert packet.roles == 0
	assert packet.guid == Guid(value=0x1f50000000000001)
	assert packet.total_num_groups == 67
	assert packet.size == 1

	imbued = packet.members[0]
	assert imbued.name == 'Imbued'
	assert imbued.guid == Guid(value=0x6)
	assert imbued.online is False
	assert imbued.group_id == 0
	assert imbued.flags == 0
	assert imbued.roles == 0

	assert packet.leader_guid == Guid(value=0x6)


	data = b'\x00\x1e}\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00P\x1f\x00\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x00\x00\x00\x00'
	packet = SMSG_GROUP_LIST.parse(data)
	print(packet)

	assert packet.type.party
	assert packet.guid == Guid(value=0x1f50000000000006)
	assert packet.members == []
	assert packet.leader_guid == Guid(value=0x30)

	data = b'\x00\x1e}\x00\x10\x00\x00\x00\x07\x00\x00\x00\x00\x00P\x1f\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	packet = SMSG_GROUP_LIST.parse(data)
	print(packet)

	assert packet.guid == Guid(value=0x1f50000000000007)
	assert packet.members == []
	assert packet.type.party
	assert packet.size == 0