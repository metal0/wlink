from wlink.world.packets import AuthResponse, Expansion, make_SMSG_ADDON_INFO, make_SMSG_AUTH_RESPONSE, \
	ServerHeader, is_large_server_packet, Opcode

def test_server_header_parsing():
	addon_size = 0x7FFF + 1
	addon_data = bytes([1] * addon_size)
	addon_info_data = make_SMSG_ADDON_INFO(addon_data=addon_data)

	addon_header = ServerHeader().parse(addon_info_data[:5])
	assert addon_header.size == 3 + addon_size
	assert addon_header.opcode == Opcode.SMSG_ADDON_INFO
	print(addon_header)

	auth_response_packet = make_SMSG_AUTH_RESPONSE(
		response=AuthResponse.ok,
		billing=dict(time_left=30),
		expansion=Expansion.tbc
	)

	is_large = is_large_server_packet(auth_response_packet[:5])
	auth_header = ServerHeader().parse(auth_response_packet[:5])
	print(f'{is_large=}')
	print(auth_header)

	assert auth_header.size == 13
	assert auth_header.opcode == Opcode.SMSG_AUTH_RESPONSE
