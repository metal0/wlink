from prowl.world.packets import SMSG_WHO

def test_SMSG_WHO():
	data = b'\x00\nc\x00\x00\x00\x00\x00\x00\x00\x00\x00'
	packet = SMSG_WHO.parse(data)
	print(packet)

	assert packet.header.size == 10
	assert packet.total_num_matches == 0
	assert len(packet.matches) == 0
