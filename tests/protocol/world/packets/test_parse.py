from prowl.protocol.world.packets import SMSG_AUTH_RESPONSE, SMSG_ADDON_INFO, ServerSize, Opcode, ServerHeader, \
	AuthResponse, Expansion

def test_server_header_parsing():
	size = ServerSize().build(3)
	print(size)

	addon_size = 0x7FFF
	addon_data = bytes([1] * addon_size)
	addon_info_data = SMSG_ADDON_INFO.build(dict(
		header=dict(opcode=Opcode.SMSG_ADDON_INFO, size=addon_size + 2),
		data=addon_data
	))

	ServerHeader().parse(addon_info_data[:5])
	auth_response_packet = SMSG_AUTH_RESPONSE.build(dict(
		response=AuthResponse.ok,
		billing=dict(time_left=30),
		expansion=Expansion.tbc
	))

	ServerHeader().parse(auth_response_packet[:5])
