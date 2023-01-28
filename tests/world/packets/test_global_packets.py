from wlink import Guid
from wlink.world.packets import SMSG_INVALIDATE_PLAYER


def test_SMSG_INVALIDATE_PLAYER():
    data = b"\x00\n\x1c\x03\xd0S\x00\x00\x00\x00\x00\x00"
    packet = SMSG_INVALIDATE_PLAYER.parse(data)
    print(packet)

    assert packet.player_guid == Guid(value=0x53D0)
