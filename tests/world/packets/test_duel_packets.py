from wlink.guid import Guid
from wlink.world.packets import (
    SMSG_DUEL_REQUESTED,
    SMSG_DUEL_COMPLETE,
    SMSG_DUEL_WINNER,
)


def test_SMSG_DUEL_REQUESTED():
    data = b"\x00\x12g\x01`\xf1 \xb0T\x00\x10\xf1\x01\x00\x00\x00\x00\x00\x00\x00"
    packet = SMSG_DUEL_REQUESTED.parse(data)
    print(packet)

    assert packet.requester == Guid(value=0x1)
    assert packet.flag_obj == Guid(value=0xF1100054B020F160)


def test_SMSG_DUEL_COMPLETE():
    data = b"\x00\x03j\x01\x01"
    packet = SMSG_DUEL_COMPLETE.parse(data)
    print(packet)


def test_SMSG_DUEL_WINNER():
    data = b"\x00\x0ck\x01\x01Pont\x00Act\x00"
    packet = SMSG_DUEL_WINNER.parse(data)

    assert packet.loser_fled
    assert packet.winner == "Pont"
    assert packet.loser == "Act"

    data = b"\x00\x0ck\x01\x00Pont\x00Act\x00"
    packet = SMSG_DUEL_WINNER.parse(data)

    assert not packet.loser_fled
    assert packet.winner == "Pont"
    assert packet.loser == "Act"
