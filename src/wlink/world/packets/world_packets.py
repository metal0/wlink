from enum import Enum

import construct

from wlink.utility.construct import Coordinates, PackEnum
from wlink.world import Opcode
from wlink.world.packets import ServerHeader

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

SMSG_NEW_WORLD = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_NEW_WORLD),
    'map_id' / construct.Int32ul,
    'position' / Coordinates(construct.Float32l),
    'rotation' / construct.Float32l,
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