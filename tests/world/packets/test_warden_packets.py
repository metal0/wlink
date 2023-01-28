from wlink.world.packets import SMSG_WARDEN_DATA


def test_SMSG_WARDEN_DATA():
    data = b"\x00'\xe6\x02\x1d\xae\xaax/\xf8Na]\x13\xe1\x9a`\xc5\xb4\nQ\xfciN\xf7\xaf35\x85\xb6c\x0f\xfb$\xa1\x0c\n;\xe8\x9e\xfd"
    packet = SMSG_WARDEN_DATA.parse(data)
    print(packet)
