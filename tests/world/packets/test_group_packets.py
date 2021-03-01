from prowl.world.packets import SMSG_GROUP_INVITE, Opcode

def test_group_invite():
	data = b'\x00\x10o\x00\x01Act\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	packet = SMSG_GROUP_INVITE.parse(data)
	print(packet)

	assert packet.header.opcode == Opcode.SMSG_GROUP_INVITE
	assert packet.in_group == True
	assert packet.inviter == 'Act'
