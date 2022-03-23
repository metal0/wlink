import construct

from .headers import ServerHeader, ClientHeader
from .opcode import Opcode

SMSG_WARDEN_DATA = construct.Struct(
	'header' / ServerHeader(Opcode.SMSG_WARDEN_DATA, body_size=39),
	'encrypted' / construct.GreedyBytes
)

def make_SMSG_WARDEN_DATA(command=51, module_id=0, module_key=0, size=100):
	raise NotImplemented()
	# return SMSG_WARDEN_DATA.build(dict(
	# 	command=command,
	# 	module_id=module_id,
	# 	module_key=module_key,
	# 	size=size
	# ))

CMSG_WARDEN_DATA = construct.Struct(
	'header' / ClientHeader(Opcode.CMSG_WARDEN_DATA),
	'encrypted' / construct.GreedyBytes,
)

def make_CMSG_WARDEN_DATA(encrypted: bytes):
	return CMSG_WARDEN_DATA.build(dict(
		header=dict(size=4 + len(encrypted)),
		encrypted=encrypted
	))

__all__ = [
	'make_CMSG_WARDEN_DATA', 'make_SMSG_WARDEN_DATA', 'CMSG_WARDEN_DATA', 'SMSG_WARDEN_DATA'
]