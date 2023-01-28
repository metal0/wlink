from enum import Enum

import construct

from .opcode import Opcode
from .headers import ServerHeader
from wlink.guid import Guid
from wlink.utility.construct import PackEnum, PackGuid, Coordinates, GuidConstruct


class UpdateFlags(Enum):
    # none = 0x0
    self_target = 0x1
    transport = 0x2
    target_guid = 0x4
    low_guid = 0x8
    high_guid = 0x10
    living = 0x20
    has_position = 0x40
    vehicle = 0x80
    game_object_position = 0x100
    game_object_rotation = 0x200
    unk = 0x400


class UpdateType(Enum):
    partial = 0
    movement = 1
    create_object = 2
    create_object2 = 3
    far_objects = 4
    near_objects = 5


class ObjectType(Enum):
    object = 0
    item = 1
    container = 2
    unit = 3
    player = 4
    game_object = 5
    dynamic_object = 6
    corpse = 7


ObjectUpdateInfo = construct.Struct(
    "update_masks" / construct.PrefixedArray(construct.Byte, construct.Int32ul),
    # 'values' / construct.Array(construct.len_(construct.this.update_masks) * 4 * 8, construct.Int32ul),
)

ValuesUpdate = construct.Struct(
    "guid" / PackGuid(Guid),
    "object_info" / ObjectUpdateInfo,
)
MovementInfo = construct.Struct()
SplineInfo = construct.Struct()

GameObjectPositionInfo = construct.Struct(
    "transport_guid" / PackGuid(Guid),
    "position" / Coordinates(),
    "transport_position" / Coordinates(),
    "facing" / construct.Float32l,
    "transport_facing" / construct.Float32l,
)
GameObjectRotationInfo = construct.Struct("long_rotation" / construct.Int64ul)

HasPositionInfo = construct.Struct(
    "position" / Coordinates(), "rotation" / construct.Float32l
)

LowGuidInfo = construct.Struct("value" / construct.Int32ul)
HighGuidInfo = construct.Struct("value" / construct.Int32ul)

TargetGuidInfo = construct.Struct("guid" / PackGuid(Guid))
TransportInfo = construct.Struct(
    "time" / construct.Int32ul,
)
VehicleInfo = construct.Struct(
    "id" / construct.Int32ul, "aim_adjustment" / construct.Float32l
)

LivingMovementInfo = construct.Struct(
    "info" / MovementInfo,
    "speeds" / construct.Array(9, construct.Float32l),
    "spline" / construct.If(construct.this.flags.spline_enabled, SplineInfo),
)

MovementBlock = construct.Struct(
    "flags" / construct.FlagsEnum(construct.Int16ul, UpdateFlags),
    "living" / construct.If(construct.this.flags.living, LivingMovementInfo),
    "go_position"
    / construct.If(
        not construct.this.flags.living and construct.this.flags.game_object_position,
        GameObjectPositionInfo,
    ),
    "has_position"
    / construct.If(
        not construct.this.flags.living and construct.this.flags.has_position,
        HasPositionInfo,
    ),
    "low_guid" / construct.If(construct.this.flags.low_guid, LowGuidInfo),
    "high_guid" / construct.If(construct.this.flags.low_guid, HighGuidInfo),
    "target" / construct.If(construct.this.flags.low_guid, TargetGuidInfo),
    "transport" / construct.If(construct.this.flags.low_guid, TransportInfo),
    "vehicle" / construct.If(construct.this.flags.low_guid, VehicleInfo),
    "go_rotation"
    / construct.If(construct.this.flags.game_object_rotation, GameObjectRotationInfo),
)


class ObjectUpdateFlags(Enum):
    none = 0x0000
    self = 0x0001
    transport = 0x0002
    has_target = 0x0004
    unknown = 0x0008
    low_guid = 0x0010
    living = 0x0020
    stationary_position = 0x0040
    vehicle = 0x0080
    position = 0x0100
    rotation = 0x0200


CreateObjectUpdate = construct.Struct(
    "guid" / PackGuid(Guid),
    "type" / PackEnum(ObjectType),
    "movement" / MovementBlock,
)

CreateObject2Update = construct.Struct()
MovementUpdate = construct.Struct(
    "guid" / PackGuid(Guid),
    "flags" / construct.Int16ul,
    # construct.IfThenElse(
    # )
)
NearObjectsUpdate = construct.Struct()
OutOfRangeObjectsUpdate = construct.Struct(
    "out_of_range_guids" / construct.PrefixedArray(construct.Int32ul, PackGuid(Guid))
)

Update = construct.Struct(
    "type" / PackEnum(UpdateType),
    "contents"
    / construct.Switch(
        construct.this.type,
        {
            UpdateType.partial: ValuesUpdate,
            UpdateType.create_object: CreateObjectUpdate,
            UpdateType.create_object2: CreateObject2Update,
            UpdateType.movement: MovementUpdate,
            UpdateType.near_objects: NearObjectsUpdate,
            UpdateType.far_objects: OutOfRangeObjectsUpdate,
        },
    ),
)

UpdatesType = construct.PrefixedArray(construct.Int32ul, Update)

SMSG_UPDATE_OBJECT = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_UPDATE_OBJECT, 0),
    "updates" / UpdatesType,
)

SMSG_COMPRESSED_UPDATE_OBJECT = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_COMPRESSED_UPDATE_OBJECT, 0),
    "uncompressed_size" / construct.Int32ul,
    "updates" / construct.Compressed(UpdatesType, "zlib"),
)

SMSG_DESTROY_OBJECT = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_DESTROY_OBJECT),
    "guid" / GuidConstruct(Guid),
    "player" / construct.Flag,  # Not sure
)

__all__ = [
    "SMSG_DESTROY_OBJECT",
    "SMSG_UPDATE_OBJECT",
    "SMSG_COMPRESSED_UPDATE_OBJECT",
    "CreateObjectUpdate",
    "CreateObject2Update",
    "ObjectUpdateInfo",
    "ObjectType",
    "OutOfRangeObjectsUpdate",
    "GameObjectPositionInfo",
    "GameObjectRotationInfo",
    "HasPositionInfo",
    "UpdateType",
    "Update",
    "UpdateFlags",
    "MovementUpdate",
    "ValuesUpdate",
    "NearObjectsUpdate",
    "MovementInfo",
    "MovementBlock",
    "LivingMovementInfo",
    "VehicleInfo",
    "SplineInfo",
    "TransportInfo",
    "LowGuidInfo",
    "HighGuidInfo",
    "TargetGuidInfo",
]
