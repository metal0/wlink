import construct

from wlink.utility.construct import (
    GuidConstruct,
    PackGuid,
    PackEnum,
    NegatedFlag,
    compute_packed_guid_byte_size,
    NamedConstruct,
    pack_guid,
)
from wlink.world.packets.b12340.character_enum_packets import CombatClass, Gender, Race
from .headers import ServerHeader, ClientHeader
from .opcode import Opcode
from wlink.guid import Guid

CMSG_NAME_QUERY = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_NAME_QUERY, 8), "guid" / GuidConstruct(Guid)
)


def make_CMSG_NAME_QUERY(guid):
    return CMSG_NAME_QUERY.build(dict(guid=guid))


NameInfo = construct.Struct(
    "name" / construct.CString("utf-8"),
    "realm_name" / construct.CString("utf-8"),
    "race" / PackEnum(Race),
    "gender" / PackEnum(Gender),
    "combat_class" / PackEnum(CombatClass),
    "declined" / construct.Default(construct.Flag, False),
)

SMSG_NAME_QUERY_RESPONSE = construct.Struct(
    "header"
    / ServerHeader(Opcode.SMSG_NAME_QUERY_RESPONSE, 8 + 1 + 1 + 1 + 1 + 1 + 10),
    "guid" / PackGuid(Guid),
    "found" / NegatedFlag(),
    "info" / construct.If(construct.this.found, NameInfo),
)


def make_SMSG_NAME_QUERY_RESPONSE(guid, found: bool, info):
    info_size = len(info["name"]) + 1 + len(info["realm_name"]) + 1 + 4
    guid_size = compute_packed_guid_byte_size(pack_guid(guid)[0])

    if type(info) is NamedConstruct:
        info = info.as_dict()

    return SMSG_NAME_QUERY_RESPONSE.build(
        dict(
            header=dict(size=2 + guid_size + 2 + info_size),
            guid=guid,
            found=found,
            info=info,
        )
    )


__all__ = [
    "make_CMSG_NAME_QUERY",
    "make_SMSG_NAME_QUERY_RESPONSE",
    "CMSG_NAME_QUERY",
    "SMSG_NAME_QUERY_RESPONSE",
    "NameInfo",
]
