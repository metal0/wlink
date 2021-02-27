import pont
from pont.guid import Guid
from pont.protocol.world.packets import SMSG_DUEL_REQUESTED


def test_SMSG_DUEL_REQUESTED():
	data = b'\x00\x12g\x01`\xf1 \xb0T\x00\x10\xf1\x01\x00\x00\x00\x00\x00\x00\x00'
	packet = SMSG_DUEL_REQUESTED.parse(data)
	print(packet)

	assert packet.requester == Guid(value=0x1)
	assert packet.flag_obj == Guid(value=0xf1100054b020f160)