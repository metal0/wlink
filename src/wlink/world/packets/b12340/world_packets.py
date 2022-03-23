from enum import Enum

import construct

from wlink.guid import Guid
from wlink.utility.construct import Coordinates, PackEnum, GuidConstruct
from wlink.world.packets.b12340.opcode import Opcode
from wlink.world.packets.b12340.headers import ServerHeader, ClientHeader

SMSG_CANCEL_COMBAT = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_CANCEL_COMBAT),
)

TransferTransportInfo = construct.Struct(
    'entry' / construct.Int32ul,
    'map_id' / construct.Int32ul
)

SMSG_TRANSFER_PENDING = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_TRANSFER_PENDING),
    'map_id' / construct.Int32ul,
    'transport' / construct.Optional(TransferTransportInfo)
)

class TransferAbortedReason(Enum):
    error = 1
    max_players = 2
    not_found = 3
    not_found2 = 0xC
    not_found3 = 0xD
    not_found4 = 0xE

    too_many_instances = 4
    zone_in_combat = 6
    insufficient_expansion = 7
    difficulty = 8
    unique_message = 9
    too_many_realm_instances = 0xA
    need_group = 0xB
    realm_only = 0xF
    map_not_allowed = 0x10

SMSG_TRANSFER_ABORTED = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_TRANSFER_ABORTED),
    'map_id' / construct.Int32ul,
    'reason' / PackEnum(TransferAbortedReason),
    'id' / construct.If(
        construct.this.reason in (
            TransferAbortedReason.insufficient_expansion, TransferAbortedReason.difficulty,
            TransferAbortedReason.unique_message
        ), construct.Int32ul
    ),
)

SMSG_NEW_WORLD = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_NEW_WORLD),
    'map_id' / construct.Int32ul,
    'position' / Coordinates(construct.Float32l),
    'rotation' / construct.Float32l,
)

SMSG_PLAY_SOUND = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_PLAY_SOUND),
    'sound_id' / construct.Int32ul
)

CMSG_BATTLEMASTER_HELLO = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_BATTLEMASTER_HELLO, 8),
    'guid' / GuidConstruct(Guid),
)

CMSG_BANKER_ACTIVATE = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_BANKER_ACTIVATE, 8),
    'guid' / GuidConstruct(Guid),
)

CMSG_GUILD_BANKER_ACTIVATE = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_BANKER_ACTIVATE, 8),
    'guid' / GuidConstruct(Guid),
)

CMSG_AREA_SPIRIT_HEALER_QUERY = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_BANKER_ACTIVATE, 8),
    'guid' / GuidConstruct(Guid),
)

CMSG_SPIRIT_HEALER_ACTIVATE = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_BANKER_ACTIVATE, 8),
    'guid' / GuidConstruct(Guid),
)

class WeatherType(Enum):
    nice = 0
    rain = 1
    snow = 2
    storm = 3
    thunders = 86
    black_rain = 90

class WeatherState(Enum):
    nice = 0
    fog = 1
    light_rain = 3
    medium_rain = 4
    heavy_rain = 5

    light_snow = 6
    medium_snow = 7
    heavy_snow = 8

    light_sandstorm = 22
    medium_sandstorm = 41
    heavy_sandstorm = 42

    thunders = 86

    black_rain = 90
    black_snow = 106

def get_weather_state(type, grade) -> WeatherState:
    if grade < 0.27:
        return WeatherState.nice

    if type == WeatherType.rain:
        if grade < 0.4:
            return WeatherState.light_rain
        elif grade < 0.7:
            return WeatherState.medium_rain
        else:
            return WeatherState.heavy_rain
    elif type == WeatherType.snow:
        if grade < 0.4:
            return WeatherState.light_snow
        elif grade < 0.7:
            return WeatherState.medium_snow
        else:
            return WeatherState.heavy_snow
    elif type == WeatherType.storm:
        if grade < 0.4:
            return WeatherState.light_sandstorm
        elif grade < 0.7:
            return WeatherState.medium_sandstorm
        else:
            return WeatherState.heavy_sandstorm

    elif type == WeatherType.black_rain:
        return WeatherState.black_rain
    elif type == WeatherType.thunders:
        return WeatherState.thunders
    else:
        return WeatherState.nice

SMSG_WEATHER = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_WEATHER),
    'weather' / PackEnum(WeatherType, construct.Int32ul),
    'grade' / construct.Float32l,
    construct.Padding(1)
)

SMSG_HEALTH_UPDATE = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_HEALTH_UPDATE),
    'guid' / GuidConstruct(Guid),
    'health' / construct.Int32ul
)

__all__ = [
    'SMSG_WEATHER', 'SMSG_HEALTH_UPDATE', 'SMSG_NEW_WORLD', 'SMSG_CANCEL_COMBAT', 'SMSG_PLAY_SOUND',
    'SMSG_TRANSFER_ABORTED', 'SMSG_TRANSFER_PENDING', 'CMSG_SPIRIT_HEALER_ACTIVATE', 'CMSG_AREA_SPIRIT_HEALER_QUERY',
    'CMSG_BATTLEMASTER_HELLO', 'CMSG_BANKER_ACTIVATE', 'CMSG_GUILD_BANKER_ACTIVATE', 'TransferAbortedReason',
    'WeatherState', 'TransferTransportInfo', 'WeatherType',
]