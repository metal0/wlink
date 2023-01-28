from enum import Enum

import construct

from wlink import Guid
from wlink.utility.construct import PackGuid
from .headers import ServerHeader, is_large_server_packet
from .opcode import Opcode


class SocialFlag(Enum):
    friend = 0x01
    ignored = 0x02
    muted = 0x04
    unknown = 0x8

    def __or__(self, other):
        return self.value | other.value

    all = friend | ignored | muted | unknown


FriendInfo = construct.Struct(
    "guid" / PackGuid(Guid),
    "flags" / construct.Int32ul,
    "note" / construct.CString("utf8"),
)

SMSG_CONTACT_LIST = construct.Struct(
    "header"
    / ServerHeader(
        Opcode.SMSG_CONTACT_LIST,
    ),
    "flags" / construct.Int32ul,
    construct.Padding(4),
    "friends" / construct.PrefixedArray(construct.Int32ul, FriendInfo),
)

# TODO: Finish
def make_SMSG_CONTACT_LIST(friends: list):
    body_size = 4 + 4
    body_size += 4
    for friend in friends:
        body_size += 4 + 4 + 1 + len(friend["note"])

    is_large = is_large_server_packet(body_size)
    return SMSG_CONTACT_LIST.build(
        dict(header=dict(size=(3 if is_large else 2) + body_size))
    )
