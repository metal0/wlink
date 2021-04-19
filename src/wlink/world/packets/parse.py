
import construct
from typing import Dict, Optional

from .whois_packets import SMSG_WHO, SMSG_WHOIS
from .auction_packets import CMSG_AUCTION_SELL_ITEM, CMSG_AUCTION_PLACE_BID, CMSG_AUCTION_LIST_ITEMS, \
	CMSG_AUCTION_LIST_PENDING_SALES, CMSG_AUCTION_LIST_OWNER_ITEMS, MSG_AUCTION_HELLO, SMSG_AUCTION_LIST_RESULT
from .auth_packets import SMSG_AUTH_RESPONSE, SMSG_AUTH_CHALLENGE
from .bind_point import SMSG_BIND_POINT_UPDATE
from .character_enum_packets import SMSG_CHAR_ENUM, CMSG_CHAR_RENAME, SMSG_CHAR_RENAME, CMSG_CHAR_CREATE, \
	SMSG_CHAR_CREATE
from .chat_packets import SMSG_MESSAGECHAT, SMSG_GM_MESSAGECHAT
from .duel_packets import SMSG_DUEL_REQUESTED
from .group_packets import SMSG_GROUP_INVITE
from .guild_packets import SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_ROSTER, SMSG_GUILD_INVITE, SMSG_GUILD_EVENT, \
	CMSG_GUILD_INFO_TEXT, CMSG_GUILD_ROSTER, CMSG_GUILD_INFO, CMSG_GUILD_MOTD, CMSG_GUILD_ACCEPT, CMSG_GUILD_CREATE
from .headers import ServerHeader
from .login_packets import SMSG_LOGOUT_RESPONSE, SMSG_LOGOUT_CANCEL_ACK, SMSG_LOGOUT_COMPLETE, SMSG_LOGIN_VERIFY_WORLD
from .mail_packets import CMSG_GET_MAIL_LIST, SMSG_MAIL_LIST_RESULT, CMSG_SEND_MAIL
from .misc_packets import SMSG_CLIENTCACHE_VERSION, SMSG_INIT_WORLD_STATES, SMSG_ADDON_INFO
from .name_query import SMSG_NAME_QUERY_RESPONSE
from .ping import SMSG_PONG, CMSG_PING
from .server_message import SMSG_SERVER_MESSAGE, SMSG_NOTIFICATION, SMSG_MOTD
from .time_packets import SMSG_TIME_SYNC_REQ, SMSG_QUERY_TIME_RESPONSE
from .tutorial_flags import SMSG_TUTORIAL_FLAGS
from .update_packets import SMSG_COMPRESSED_UPDATE_OBJECT, SMSG_UPDATE_OBJECT
from .warden_packets import SMSG_WARDEN_DATA
from wlink.world.opcode import Opcode


class WorldPacketParser:
	def __init__(self):
		self._parsers: Dict[Opcode, Optional[construct.Construct]] = {}

	def set_parser(self, opcode: Opcode, parser: construct.Construct):
		self._parsers[opcode] = parser

	def parse_header(self, data: bytes) -> ServerHeader:
		raise NotImplemented()

	def parse(self, data: bytes, header):
		raise NotImplemented

	def parser(self, opcode):
		return self._parsers[opcode]

class WorldServerPacketParser(WorldPacketParser):
	def __init__(self):
		super().__init__()
		parsers = [
			(Opcode.SMSG_ADDON_INFO, SMSG_ADDON_INFO),
			(Opcode.SMSG_AUTH_RESPONSE, SMSG_AUTH_RESPONSE),
			(Opcode.SMSG_AUTH_CHALLENGE, SMSG_AUTH_CHALLENGE),
			(Opcode.SMSG_BIND_POINT_UPDATE, SMSG_BIND_POINT_UPDATE),
			(Opcode.SMSG_CHAR_ENUM, SMSG_CHAR_ENUM),
			(Opcode.SMSG_CHAR_CREATE, SMSG_CHAR_CREATE),
			(Opcode.SMSG_CHAR_RENAME, SMSG_CHAR_RENAME),
			(Opcode.SMSG_CLIENTCACHE_VERSION, SMSG_CLIENTCACHE_VERSION),
			(Opcode.SMSG_GUILD_QUERY_RESPONSE, SMSG_GUILD_QUERY_RESPONSE),
			(Opcode.SMSG_GUILD_ROSTER, SMSG_GUILD_ROSTER),
			(Opcode.SMSG_GUILD_INVITE, SMSG_GUILD_INVITE),
			(Opcode.SMSG_GUILD_EVENT, SMSG_GUILD_EVENT),
			(Opcode.SMSG_TIME_SYNC_REQ, SMSG_TIME_SYNC_REQ),
			(Opcode.SMSG_MESSAGECHAT, SMSG_MESSAGECHAT),
			(Opcode.SMSG_GM_MESSAGECHAT, SMSG_GM_MESSAGECHAT),
			(Opcode.SMSG_LOGIN_VERIFY_WORLD, SMSG_LOGIN_VERIFY_WORLD),
			(Opcode.SMSG_MOTD, SMSG_MOTD),
			(Opcode.SMSG_NAME_QUERY_RESPONSE, SMSG_NAME_QUERY_RESPONSE),
			(Opcode.SMSG_PONG, SMSG_PONG),
			(Opcode.SMSG_QUERY_TIME_RESPONSE, SMSG_QUERY_TIME_RESPONSE),
			(Opcode.SMSG_TUTORIAL_FLAGS, SMSG_TUTORIAL_FLAGS),
			(Opcode.SMSG_WARDEN_DATA, SMSG_WARDEN_DATA),
			(Opcode.SMSG_INIT_WORLD_STATES, SMSG_INIT_WORLD_STATES),
			(Opcode.SMSG_LOGOUT_RESPONSE, SMSG_LOGOUT_RESPONSE),
			(Opcode.SMSG_LOGOUT_CANCEL_ACK, SMSG_LOGOUT_CANCEL_ACK),
			(Opcode.SMSG_LOGOUT_COMPLETE, SMSG_LOGOUT_COMPLETE),
			(Opcode.SMSG_GROUP_INVITE, SMSG_GROUP_INVITE),
			(Opcode.SMSG_GUILD_INVITE, SMSG_GUILD_INVITE),
			(Opcode.SMSG_GM_MESSAGECHAT, SMSG_GM_MESSAGECHAT),
			(Opcode.SMSG_MESSAGECHAT, SMSG_MESSAGECHAT),
			(Opcode.SMSG_SERVER_MESSAGE, SMSG_SERVER_MESSAGE),
			(Opcode.SMSG_NOTIFICATION, SMSG_NOTIFICATION),
			(Opcode.SMSG_DUEL_REQUESTED, SMSG_DUEL_REQUESTED),
			(Opcode.SMSG_UPDATE_OBJECT, SMSG_UPDATE_OBJECT),
			(Opcode.SMSG_COMPRESSED_UPDATE_OBJECT, SMSG_COMPRESSED_UPDATE_OBJECT),
			(Opcode.SMSG_MAIL_LIST_RESULT, SMSG_MAIL_LIST_RESULT),
			(Opcode.SMSG_WHOIS, SMSG_WHOIS),
			(Opcode.SMSG_AUCTION_LIST_RESULT, SMSG_AUCTION_LIST_RESULT),
			(Opcode.SMSG_WHO, SMSG_WHO),
		]

		for opcode, parser in parsers:
			self.set_parser(opcode, parser)

	def parse(self, data: bytes, header):
		return self._parsers[header.opcode].parse(data)

class WorldClientPacketParser(WorldPacketParser):
	def __init__(self):
		super().__init__()
		parsers = [
			(Opcode.CMSG_PING, CMSG_PING),
			(Opcode.CMSG_GET_MAIL_LIST, CMSG_GET_MAIL_LIST),
			(Opcode.CMSG_SEND_MAIL, CMSG_SEND_MAIL),
			(Opcode.MSG_AUCTION_HELLO, MSG_AUCTION_HELLO(server=False)),
			# (Opcode.CMSG_AUCTION_LIST_BIDDER_ITEMS, CMSG_AUCTION_LIST_BIDDER_ITEMS),
			(Opcode.CMSG_AUCTION_LIST_OWNER_ITEMS, CMSG_AUCTION_LIST_OWNER_ITEMS),
			(Opcode.CMSG_AUCTION_LIST_PENDING_SALES, CMSG_AUCTION_LIST_PENDING_SALES),
			(Opcode.CMSG_AUCTION_LIST_ITEMS, CMSG_AUCTION_LIST_ITEMS),
			(Opcode.CMSG_AUCTION_PLACE_BID, CMSG_AUCTION_PLACE_BID),
			(Opcode.CMSG_AUCTION_SELL_ITEM, CMSG_AUCTION_SELL_ITEM),
			(Opcode.CMSG_GUILD_INFO_TEXT, CMSG_GUILD_INFO_TEXT),
			(Opcode.CMSG_GUILD_ROSTER, CMSG_GUILD_ROSTER),
			(Opcode.CMSG_GUILD_INFO, CMSG_GUILD_INFO),
			(Opcode.CMSG_GUILD_MOTD, CMSG_GUILD_MOTD),
			(Opcode.CMSG_GUILD_ACCEPT, CMSG_GUILD_ACCEPT),
			(Opcode.CMSG_GUILD_CREATE, CMSG_GUILD_CREATE),
			(Opcode.CMSG_CHAR_RENAME, CMSG_CHAR_RENAME),
			(Opcode.CMSG_CHAR_CREATE, CMSG_CHAR_CREATE),
		]

		for opcode, parser in parsers:
			self.set_parser(opcode, parser)

	def parse(self, data: bytes, header, large=False):
		return self._parsers[header.opcode].parse(data)
