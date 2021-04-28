import construct
from enum import Enum

from wlink.guid import Guid
from wlink.world.opcode import Opcode
from .headers import ServerHeader, ClientHeader
from wlink.utility.construct import GuidConstruct, PackEnum


class MailType(Enum):
    normal = 0
    auction = 2
    creature = 3
    gameobject = 4
    calendar = 5


CMSG_GET_MAIL_LIST = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_GET_MAIL_LIST, 8),
    'mailbox' / GuidConstruct(Guid),
)

MailEnchantmentInfo = construct.Struct(
    'charges' / construct.Int32ul,
    'duration' / construct.Int32ul,
    'id' / construct.Int32ul
)

MailItemData = construct.Struct(
    'index' / construct.Byte,
    'guid_low' / construct.Int32ul,
    'entry' / construct.Int32ul,
    'enchantment' / construct.Array(7, MailEnchantmentInfo),
    'property_id' / construct.Int32ul,
    'suffix_factor' / construct.Int32ul,
    'count' / construct.Int32ul,
    'charges' / construct.Int32ul,
    'max_durability' / construct.Int32ul,
    'durability' / construct.Int32ul,
    construct.Padding(1)
)

MailMessageData = construct.Struct(
    'size' / construct.Int16ul,
    'id' / construct.Int32ul,
    'type' / PackEnum(MailType),
    'sender' / construct.Switch(
        construct.this.type, {
            MailType.normal: GuidConstruct(Guid),
            MailType.creature: construct.Int32ul,
            MailType.gameobject: construct.Int32ul,
            MailType.auction: construct.Int32ul,
            MailType.calendar: construct.Int32ul,
        }
    ),

    'cod' / construct.Int32ul,
    construct.Padding(4),
    'stationery' / construct.Int32ul,
    'money' / construct.Int32ul,
    'checked' / construct.Int32ul,
    'timestamp' / construct.Float32l,
    'mail_template' / construct.Int32ul,
    'subject' / construct.CString('utf8'),
    'body' / construct.CString('utf8'),
    'sent_items' / construct.PrefixedArray(construct.Byte, MailItemData)
)

SMSG_MAIL_LIST_RESULT = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_MAIL_LIST_RESULT),
    'total_num_mail' / construct.Int32ul,
    'mail' / construct.PrefixedArray(construct.Byte, MailMessageData)
)

SMSG_RECEIVED_MAIL = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_RECEIVED_MAIL, 4),
    'unk' / construct.Int
)

CMSG_SEND_MAIL = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_SEND_MAIL),
    'mailbox' / GuidConstruct(Guid),
    'receiver' / construct.CString('utf8'),
    'subject' / construct.CString('utf8'),
    'body' / construct.CString('utf8'),
    construct.Padding(8),
    'items' / construct.PrefixedArray(construct.Int8ul, construct.Struct(
        construct.Padding(1),
        'guid' / GuidConstruct(Guid)
    )),
    'money' / construct.Int32ul,
    'cod' / construct.Int32ul,
    construct.Padding(9),
)

class MailResponseType(Enum):
    send = 0
    money_taken = 1
    item_taken = 2
    returned_to_sender = 3
    deleted = 4
    made_permanent = 5


class MailResponse(Enum):
    ok = 0
    equip_error = 1
    cannot_send_to_self = 3
    not_enough_money = 3
    recipient_not_found = 4
    not_your_team = 5
    internal_error = 6
    dsiabled_for_trial_acc = 14
    recipient_cap_reached = 15
    cant_send_wrapped_cod = 16
    mail_and_chat_suspended = 17
    too_many_attachments = 18
    mail_attachment_invalid = 19
    item_has_expired = 21

SMSG_SEND_MAIL_RESULT = construct.Struct(
    'header' / ServerHeader(Opcode.SMSG_SEND_MAIL_RESULT),
    'mail_id' / construct.Int32ul,
    'mail_action' / PackEnum(MailResponseType, construct.Int32ul),
    'mail_response' / PackEnum(MailResponse, construct.Int32ul),
    construct.IfThenElse(
        construct.this.mail_response == MailResponse.equip_error,
        construct.Struct('equip_error' / construct.Int32ul),
        construct.If(
            construct.this.mail_action == MailResponseType.item_taken,
            construct.Struct(
                'item_guid' / construct.Int32ul,
                'item_count' / construct.Int32ul
            )
        )
    )
)

CMSG_MAIL_TAKE_MONEY = construct.Struct(
    'header' / ClientHeader(Opcode.CMSG_MAIL_TAKE_MONEY),
    'mailbox' / GuidConstruct(Guid),
    'mailbox_id' / construct.Int32ul,
)
