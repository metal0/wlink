import construct
from construct import singleton, Construct, stream_read, integertypes, IntegerError, stream_write

from .opcode import Opcode
from ....utility.construct import PackEnum, int8

def _is_large_mask(context):
	return is_large_server_packet(bytes([context.mask]))

@singleton
class ServerSize(Construct):
	def _parse(self, stream, context, path):
		mask = stream_read(stream, 1, path)

		is_large = is_large_server_packet(mask)
		size_bytes = stream_read(stream, 2 if is_large else 1, path)
		size = 0

		if is_large:
			size |= int8(~0x80 & mask[0]) << 16
		else:
			size_bytes = [mask[0], size_bytes[0]]

		size |= int8(size_bytes[0]) << 8
		size |= int8(size_bytes[1])
		return size

	def _build(self, obj: int, stream, context, path):
		if not isinstance(obj, integertypes):
			raise IntegerError(f"value {obj} is not an integer", path=path)
		if obj < 0:
			raise IntegerError(f"StreamSize cannot build from negative number {obj}", path=path)
		result = bytearray()

		if is_large_server_packet(obj):
			result.append(0x80 | int8(obj >> 16))
		result.append(int8(obj >> 8))
		result.append(int8(obj))

		stream_write(stream, bytes(result), len(result), path)
		return obj

	def _emitprimitivetype(self, ksy, bitwise):
		return "vlq_base24_le"

def is_large_server_packet(data) -> bool:
	if type(data) is bytes:
		return (0x80 & int8(data[0])) == 0x80
	elif type(data) is int:
		return data > 0x7FFF
	elif type(data) is dict:
		return is_large_server_packet(data['size'])
	else:
		return is_large_server_packet(data.size)

# size >= 4 && size < 10240;
def ClientHeader(opcode=None, body_size=0):
	assert 0 <= body_size < 10236
	if opcode is None:
		opcode_con = PackEnum(Opcode, construct.Int32ul)
	else:
		opcode_con = construct.Default(construct.Const(opcode, PackEnum(Opcode, construct.Int32ul)), opcode)

	return construct.Struct(
		'size' / construct.Default(construct.Int16ub, body_size + 4),
		'opcode' / opcode_con
	)

def ServerHeader(opcode=None, body_size=0, is_large=False):
	if opcode is None:
		opcode_con = construct.ByteSwapped(PackEnum(Opcode, construct.Short))
	else:
		opcode_con = construct.ByteSwapped(construct.Default(construct.Const(opcode, PackEnum(Opcode, construct.Short)), opcode))

	return construct.Struct(
		'size' / construct.Default(ServerSize, (3 if is_large else 2) + body_size),
		'opcode' / opcode_con
	)

__all__ = [
	'ServerHeader', 'ServerSize', 'ClientHeader', 'is_large_server_packet'
]