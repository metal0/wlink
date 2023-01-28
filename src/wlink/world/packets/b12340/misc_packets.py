import construct

# TODO: There is DOS potential here as well as with SMSG_ADDON_INFO as mentioned on the TrinityCore Github.
#  I suspect this is due to world protocol using zlib DEFLATE compression, which is susceptible to decompression bombs.
#  Though I don't know how effective this will be in the context of TCP streams.
from .opcode import Opcode
from .headers import ServerHeader, is_large_server_packet

SMSG_ADDON_INFO = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_ADDON_INFO, 0),
    "addon_data" / construct.GreedyBytes,
)


def make_SMSG_ADDON_INFO(addon_data: bytes):
    body_size = len(addon_data)
    is_large = is_large_server_packet(body_size)
    return SMSG_ADDON_INFO.build(
        dict(
            header=dict(
                opcode=Opcode.SMSG_ADDON_INFO,
                size=(3 if is_large else 2) + len(addon_data),
            ),
            addon_data=addon_data,
        )
    )


SMSG_CLIENTCACHE_VERSION = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_CLIENTCACHE_VERSION, body_size=4),
    "version" / construct.Default(construct.Int32ul, 3),
)


def make_SMSG_CLIENTCACHE_VERSION(version: int = 3):
    return SMSG_CLIENTCACHE_VERSION.build(dict(version=version))


SMSG_TRIGGER_CINEMATIC = construct.Struct(
    "header" / ServerHeader(opcode=Opcode.SMSG_TRIGGER_CINEMATIC, body_size=4),
    "cinematic_id" / construct.Int32ul,
)


def make_SMSG_TRIGGER_CINEMATIC(cinematic_id: int) -> bytes:
    return SMSG_TRIGGER_CINEMATIC.build(
        dict(
            header=dict(opcode=Opcode.SMSG_TRIGGER_CINEMATIC, size=4),
            cinematic_id=cinematic_id,
        )
    )


SMSG_TRIGGER_MOVIE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_TRIGGER_MOVIE, 4),
    "movid_id" / construct.Int32ul,
)


def make_SMSG_TRIGGER_MOVIE(movid_id: int) -> bytes:
    return SMSG_TRIGGER_MOVIE.build(
        dict(header=dict(opcode=Opcode.SMSG_TRIGGER_MOVIE, size=4), movid_id=movid_id)
    )


SMSG_INIT_WORLD_STATES = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_INIT_WORLD_STATES, 14),
    "map_id" / construct.Int32ul,
    "zone_id" / construct.Int32ul,
    "area_id" / construct.Int32ul,
    "world_states"
    / construct.PrefixedArray(
        construct.Int16ul, construct.Sequence(construct.Int32ul, construct.Int32ul)
    ),
)

SMSG_UPDATE_WORLD_STATES = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_UPDATE_WORLD_STATE, 4 + 4),
    "field" / construct.Int32ul,
    "value" / construct.Int32ul,
)

SMSG_CRITERIA_UPDATE = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_CRITERIA_UPDATE),
)

__all__ = [
    "SMSG_CRITERIA_UPDATE",
    "SMSG_UPDATE_WORLD_STATES",
    "SMSG_INIT_WORLD_STATES",
    "SMSG_ADDON_INFO",
    "SMSG_TRIGGER_CINEMATIC",
    "SMSG_TRIGGER_MOVIE",
    "SMSG_CLIENTCACHE_VERSION",
    "make_SMSG_TRIGGER_MOVIE",
    "make_SMSG_ADDON_INFO",
    "make_SMSG_CLIENTCACHE_VERSION",
    "make_SMSG_TRIGGER_CINEMATIC",
]
