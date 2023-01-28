from wlink.world.packets import SMSG_NOTIFICATION, SMSG_MOTD


def test_SMSG_NOTIFICATION():
    data = b"\x00\x13\xcb\x01Unknown language\x00"
    packet = SMSG_NOTIFICATION.parse(data)
    assert packet.message == "Unknown language"


def test_SMSG_MOTD():
    data = b"\x00t=\x03\x02\x00\x00\x00Welcome to an AzerothCore server.\x00|cffFF4A2DThis server runs on AzerothCore|r |cff3CE7FFwww.azerothcore.org|r\x00"
    packet = SMSG_MOTD.parse(data)

    assert packet.header.size == 116
    assert packet.lines == [
        "Welcome to an AzerothCore server.",
        "|cffFF4A2DThis server runs on AzerothCore|r |cff3CE7FFwww.azerothcore.org|r",
    ]
