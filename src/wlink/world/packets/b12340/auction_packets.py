import construct

from wlink.guid import Guid
from .opcode import Opcode
from .headers import ServerHeader, ClientHeader
from wlink.utility.construct import GuidConstruct

SMSG_AUCTION_HELLO = construct.Struct(
    "header" / ServerHeader(Opcode.MSG_AUCTION_HELLO),
    "auctioneer" / GuidConstruct(Guid),
    "house_id" / construct.Default(construct.Int32ul, 1),
    "is_ah_enabled" / construct.Default(construct.Flag, True),
)

CMSG_AUCTION_HELLO = construct.Struct(
    "header" / ClientHeader(Opcode.MSG_AUCTION_HELLO),
    "auctioneer" / GuidConstruct(Guid),
)


def MSG_AUCTION_HELLO(server=False):
    return SMSG_AUCTION_HELLO if server else CMSG_AUCTION_HELLO


SMSG_AUCTION_COMMAND_RESULT = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_AUCTION_COMMAND_RESULT, 4 + 4 + 4),
    "auction_id" / construct.Int32sl,
    "action" / construct.Int32sl,
    "error" / construct.Int32sl,
)

AuctionSellData = construct.Struct(
    "guid" / GuidConstruct(Guid), "count" / construct.Int32ul
)

CMSG_AUCTION_SELL_ITEM = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_AUCTION_SELL_ITEM),
    "auctioneer" / GuidConstruct(Guid),
    "auction_items" / construct.PrefixedArray(construct.Int32ul, AuctionSellData),
    "bid" / construct.Int32ul,
    "buyout" / construct.Int32ul,
    "expiry_time" / construct.Int32ul,
)


def make_CMSG_AUCTION_SELL_ITEM(
    auctioneer, auction_items: list, bid: int, buyout: int, expiry_time: int
):
    if type(auctioneer) is int:
        auctioneer = Guid(value=auctioneer)

    data_size = 8 + len(auction_items) * (8 + 4) + 4 + 4 + 4 + 4
    return CMSG_AUCTION_SELL_ITEM.build(
        dict(
            header=dict(size=4 + data_size),
            auctioneer=auctioneer,
            auction_items=auction_items,
            bid=bid,
            buyout=buyout,
            expiry_time=expiry_time,
        )
    )


CMSG_AUCTION_REMOVE_ITEM = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_AUCTION_REMOVE_ITEM, 8 + 4),
    "auctioneer" / GuidConstruct(Guid),
    "auction_id" / construct.Int32sl,
)

CMSG_AUCTION_PLACE_BID = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_AUCTION_PLACE_BID, 8 + 4 + 4),
    "auctioneer" / GuidConstruct(Guid),  # TODO: Check here or above packet
    "auction_id" / construct.Int32sl,
    "price" / construct.Int32sl,
)


def make_CMSG_AUCTION_PLACE_BID(auctioneer, auction_id: int, price: int):
    if type(auctioneer) is int:
        auctioneer = Guid(value=auctioneer)

    data_size = 8 + 4 + 4
    return CMSG_AUCTION_PLACE_BID.build(
        dict(
            header=dict(size=4 + data_size),
            auctioneer=auctioneer,
            auction_id=auction_id,
            price=price,
        )
    )


# We might need to do some more work to explore this packet's structure but this might be okay for now.
CMSG_AUCTION_LIST_ITEMS = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_AUCTION_LIST_ITEMS),
    "auctioneer" / GuidConstruct(Guid),
    "list_start" / construct.Int32ul,
    "search_term" / construct.CString("utf8"),
    "min_level" / construct.Default(construct.Byte, 0),
    "max_level" / construct.Default(construct.Byte, 80),
    "slot_id" / construct.Default(construct.Int32ul, 0),
    "category" / construct.Default(construct.Int32ul, 0),
    "subcategory" / construct.Default(construct.Int32ul, 0),
    "rarity" / construct.Default(construct.Int32ul, 0),
    "usable" / construct.Default(construct.Flag, False),
    "is_full" / construct.Default(construct.Flag, True),
    construct.Padding(1)
    # construct.PrefixedArray(construct.Default(construct.Byte, 0), construct.Padding(2)),
)


def make_CMSG_AUCTION_LIST_ITEMS(
    auctioneer,
    search_term: str,
    list_start: int = 0,
    min_level=0,
    max_level=80,
    slot_id=0,
    category=0,
    subcategory=0,
    rarity=0,
    usable=False,
    is_full=True,
):
    data_size = 8 + 4
    data_size += len(search_term) + 1
    data_size += 1 * 2
    data_size += 4 * 4
    data_size += 1 * 2
    data_size += 1

    return CMSG_AUCTION_LIST_ITEMS.build(
        dict(
            header=dict(size=4 + data_size),
            auctioneer=auctioneer,
            list_start=list_start,
            search_term=search_term,
            min_level=min_level,
            max_level=max_level,
            slot_id=slot_id,
            category=category,
            subcategory=subcategory,
            rarity=rarity,
            usable=usable,
            is_full=is_full,
        )
    )


# Based on the following:
# vType));           // usable
#     CDataStore::PutInt8(v7 != 0);                   // full query?
#     LOBYTE(itemClass) = 0;
#     itemSubClass2 = data.m_size;
#     CDataStore::PutInt8(0);                         // placeholder
#     v10 = 0;
#     v11 = g_auctionSort;
#     HIDWORD(invType) = 12;
#     do
#     {
#         if ( v10 < 12 && v11 && v11->isSorted )
#         {
#             CDataStore::PutInt8(v11->sortColumn);
#             CDataStore::PutInt8(v11->Reversed != 0);
#             LOBYTE(itemClass) = itemClass + 1;
#         }
#         ++v10;
#         ++v11;
#         --HIDWORD(invType);
#     }
#     while ( HIDWORD(invType) );
#     CDataStore::PutInt8AtPos(&data, itemSubClass2, itemClass);
#     data.m_read = 0;
#     ClientServices::SendPacket_1(&data);

AuctionEnchantmentInfo = construct.Struct(
    "charges" / construct.Int32ul,
    "duration" / construct.Int32ul,
    "id" / construct.Int32ul,
)

AuctionInfo = construct.Struct(
    "id" / construct.Int32ul,
    "entry_id" / construct.Int32ul,
    "enchantments" / construct.Array(7, AuctionEnchantmentInfo),
    "random_property_id" / construct.Int32ul,
    "suffix_factor" / construct.Int32ul,
    "num_items" / construct.Int32ul,
    "spell_charges" / construct.Int32ul,
    construct.Padding(4),
    "owner" / GuidConstruct(Guid),
    "start_bid" / construct.Int32ul,
    "buyout" / construct.Int32ul,
    "time_left" / construct.Int32ul,
    "bidder" / GuidConstruct(Guid),
    "bid" / construct.Int32ul,
)

SMSG_AUCTION_LIST_RESULT = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_AUCTION_LIST_RESULT, 4 + 4 + 4),
    "count" / construct.Int32ul,
    "total_count" / construct.Int32ul,
    "cooldown" / construct.Int32ul,
    "auctions" / construct.Array(construct.this.count, AuctionInfo),
)

CMSG_AUCTION_LIST_OWNER_ITEMS = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_AUCTION_LIST_OWNER_ITEMS, 8 + 4),
    "auctioneer" / GuidConstruct(Guid),
    "list_start" / construct.Int32ul,
)

# Structure?:
# 'search_term' / construct.CString('utf8'),
# 'min_level' / construct.Default(construct.Byte, 0),
# 'max_level' / construct.Default(construct.Byte, 80),
# 'slot_id' / construct.Default(construct.Int32ul, 0),
# 'category' / construct.Default(construct.Int32ul, 0),
# 'subcategory' / construct.Default(construct.Int32ul, 0),
# 'rarity' / construct.Default(construct.Int32ul, 0),
# 'usable' / construct.Default(construct.Flag, False),
# 'is_full' / construct.Default(construct.Flag, True),
# construct.Padding(1)


def make_CMSG_AUCTION_LIST_OWNER_ITEMS(auctioneer, list_start: int = 0):
    if type(auctioneer) is int:
        auctioneer = Guid(value=auctioneer)

    data_size = 8 + 4

    return CMSG_AUCTION_LIST_OWNER_ITEMS.build(
        dict(
            header=dict(size=4 + data_size),
            auctioneer=auctioneer,
            list_start=list_start,
        )
    )


CMSG_AUCTION_LIST_PENDING_SALES = construct.Struct(
    "header" / ClientHeader(Opcode.CMSG_AUCTION_LIST_PENDING_SALES, 8),
    "auctioneer" / GuidConstruct(Guid),
)


def make_CMSG_AUCTION_LIST_PENDING_SALES(auctioneer):
    if type(auctioneer) is int:
        auctioneer = Guid(value=auctioneer)

    data_size = 8

    return CMSG_AUCTION_LIST_PENDING_SALES.build(
        dict(
            header=dict(size=4 + data_size),
            auctioneer=auctioneer,
        )
    )


PendingSale = construct.Struct(
    "info1" / construct.CString("utf8"),
    "info2" / construct.CString("utf8"),
    construct.Padding(8 + 4),
    "time_left" / construct.Float32l,
)

SMSG_AUCTION_LIST_PENDING_SALES = construct.Struct(
    "header" / ServerHeader(Opcode.SMSG_AUCTION_LIST_PENDING_SALES, 8),
    "sales" / construct.PrefixedArray(construct.Int32ul, PendingSale),
)

__all__ = [
    "SMSG_AUCTION_LIST_PENDING_SALES",
    "PendingSale",
    "CMSG_AUCTION_LIST_PENDING_SALES",
    "make_CMSG_AUCTION_LIST_PENDING_SALES",
    "make_CMSG_AUCTION_LIST_ITEMS",
    "make_CMSG_AUCTION_LIST_OWNER_ITEMS",
    "make_CMSG_AUCTION_PLACE_BID",
    "make_CMSG_AUCTION_SELL_ITEM",
    "CMSG_AUCTION_PLACE_BID",
    "CMSG_AUCTION_SELL_ITEM",
    "CMSG_AUCTION_LIST_ITEMS",
    "CMSG_AUCTION_HELLO",
    "CMSG_AUCTION_LIST_OWNER_ITEMS",
    "CMSG_AUCTION_REMOVE_ITEM",
    "SMSG_AUCTION_HELLO",
    "SMSG_AUCTION_LIST_RESULT",
    "SMSG_AUCTION_COMMAND_RESULT",
    "AuctionInfo",
    "AuctionEnchantmentInfo",
    "AuctionSellData",
    "MSG_AUCTION_HELLO",
]
