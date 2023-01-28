from wlink.world.packets.b12340.friendslist_packets import SMSG_CONTACT_LIST


def test_contact_list():
    data = b"\x00\ng\x00\x07\x00\x00\x00\x00\x00\x00\x00"
    packet = SMSG_CONTACT_LIST.parse(data)
    print(f"{packet=}")
