from wlink.guid import Guid, GuidType


def test_guid():
    guid = Guid(counter=3, high=7)
    assert guid.value == 0x7000000000003
    assert int(guid) == 0x7000000000003
    assert guid.counter == 3
    assert guid.high == 7
    assert guid.type == GuidType.player
    assert str(guid) == "0x7000000000003, GuidType.player"

    guid.counter = 16
    guid.high = 37
    assert guid.high == 37
    assert guid.counter == 16
    assert guid.type == GuidType.player
    assert guid.has_entry()

    guid = Guid(counter=32, type=GuidType.unit)
    assert guid.value == 0xF130000000000020
    assert int(guid) == 0xF130000000000020
    assert guid.counter == 32
    assert guid.type == GuidType.unit
    assert not guid.has_entry()
    assert str(guid) == "0xf130000000000020, GuidType.unit"

    guid.type = GuidType.item
    assert guid.type == GuidType.item
    guid.high = GuidType.dynamic_object.value

    assert guid.has_entry()
    assert guid.type == GuidType.dynamic_object

    guid.high = GuidType.corpse.value
    assert guid.type == GuidType.corpse
    assert guid.has_entry()

    guid = Guid(value=0x7000000003372CC)
    assert guid.value == 0x7000000003372CC
    assert int(guid) == 0x7000000003372CC
    assert guid.type == GuidType.player
    assert guid.counter == 0x3372CC
    assert guid.has_entry()
    assert str(guid) == "0x7000000003372cc, GuidType.player"

    guid = Guid(counter=1, type=GuidType.player)
    assert guid.value == 0x1
    assert int(guid) == 0x1
    assert guid.counter == 1
    assert guid.type == GuidType.player
    assert str(guid) == "0x1, GuidType.player"
