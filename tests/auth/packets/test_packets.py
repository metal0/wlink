from wlink.auth.packets import (
    Opcode,
    Response,
    ChallengeRequest,
    ChallengeResponse,
    ProofResponse,
    ProofRequest,
    RealmlistResponse,
)
from wlink.auth.realm import RealmType, RealmStatus, RealmFlags
from wlink.utility.string import bytes_to_int


def test_challenge_request_packet1():
    packet = bytes.fromhex(
        "00082300576f57000303053430363878006e69570053556e65d4feffff0ab3cd730541444d494e"
    )
    challenge_request = ChallengeRequest.parse(packet)

    assert challenge_request.header.opcode == Opcode.login_challenge
    assert challenge_request.header.response == Response.db_busy
    assert challenge_request.game == "WoW"
    assert challenge_request.version == "3.3.5"
    assert challenge_request.build == 12340
    assert challenge_request.architecture == "x86"
    assert challenge_request.os == "Win"
    assert str(challenge_request.ip) == "10.179.205.115"
    assert challenge_request.country == "enUS"
    assert challenge_request.timezone_bias == -300
    assert challenge_request.account_name == "ADMIN"
    assert ChallengeRequest.build(challenge_request) == packet


def test_challenge_request_packet2():
    packet = bytes.fromhex(
        "00002800576f57000303053430363878006e69570053556e65d4feffff000000000a4c4f4e474d414e594553"
    )
    challenge_request = ChallengeRequest.parse(packet)

    assert challenge_request.header.opcode == Opcode.login_challenge
    assert challenge_request.header.response == Response.success
    assert challenge_request.game == "WoW"
    assert challenge_request.version == "3.3.5"
    assert challenge_request.build == 12340
    assert challenge_request.architecture == "x86"
    assert challenge_request.os == "Win"
    assert challenge_request.country == "enUS"
    assert challenge_request.timezone_bias == -300
    assert challenge_request.account_name == "LONGMANYES"
    assert ChallengeRequest.build(challenge_request) == packet

    szn_data = b"\x00\x08&\x00WoW\x00\x03\x03\x054068x\x00XSO\x00SUne\xd4\xfe\xff\xff\xa0'\x84\\\x08CHEESEMO"
    szn_challenge = ChallengeRequest.parse(szn_data)
    print(szn_challenge)

    warmane_bug_data = b"\x00\x08'\x00WoW\x00\x03\x03\x054068x\x00XSO\x00SUne\xd4\xfe\xff\xffh\xfe\tp\tFLOWERMOM"
    print(ChallengeRequest.parse(warmane_bug_data))
    # print(szn_challenge)


def test_challenge_request_named_args():
    packet = ChallengeRequest.build(
        {"game": "WoW", "os": "Win", "country": "enUS", "account_name": "ADMIN"}
    )


def test_challenge_response_packet1():
    packet = bytes.fromhex(
        "0000006f168b46a9cd26b0adb481c59d92ba2f8e5432918abb90f0805677cc085d6a07010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89fb348ce3fd604ea01f910e12b900588375197e0172df0ae9df5fac2e22227ea6c5a970407fe7d52276c97e13e71695d300"
    )
    challenge_response = ChallengeResponse.parse(packet)
    assert challenge_response.header.response == Response.success
    assert (
        challenge_response.rc4.server_public
        == 3354117828571998584191894319144934700250845415608995089404241538219888023151
    )
    assert challenge_response.rc4.generator_length == 1
    assert challenge_response.rc4.generator == 7
    assert challenge_response.rc4.prime_length == 32
    assert (
        challenge_response.rc4.prime
        == 62100066509156017342069496140902949863249758336000796928566441170293728648119
    )
    assert (
        challenge_response.rc4.salt
        == 75306791175913550635130350707151637678476193135459206924908206791041802319099
    )
    assert ChallengeResponse.build(challenge_response) == packet

    szn_data = bytes.fromhex(
        "000000675f54d1e65a382bc343730cac11dcaa4c0204a1a45a3e87c4b31bed6933eb55010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b8979604517f018fa18b3b99bb764cbcb33bed1e3db2ccc17bac1a2cb062e86cdd40166742b495c252c46876a1a3e7d18e200"
    )
    print(ChallengeResponse.parse(szn_data))

    warmane_bug_data = bytes.fromhex(
        "000000153ce50a2a341987445c88a85e650599a684a84b7f43c5c57921bd183f1db105010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89ed5be899b7acc1a3514d8c93d997329fd6756f744b1be29c0a51a2c995b7cae5baa31e99a00b2157fc373fb369cdd2f100"
    )
    print(ChallengeResponse.parse(warmane_bug_data))

    acore_banned_data = bytearray(b"\x00\x00\x0c")
    response = ChallengeResponse.parse(acore_banned_data)

    assert response.header.opcode == Opcode.login_challenge
    assert response.response == Response.suspended
    assert response.rc4 is None


def test_challenge_response_packet2():
    packet = bytes.fromhex(
        "0000009ef68afffcd1328866b564d4bb0b12249a8df90e07bcd6064845ab64b482e11c010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b89319782ba4be5e9fc8e11cf9d7261f450ee7344aee4e402f6a3d0319c7ac425eabaa31e99a00b2157fc373fb369cdd2f100"
    )
    challenge_response = ChallengeResponse.parse(packet)
    print(challenge_response)

    assert challenge_response.header.opcode == Opcode.login_challenge
    assert challenge_response.header.response == Response.success
    assert challenge_response.rc4.server_public == int.from_bytes(
        packet[3:35], byteorder="little", signed=False
    )
    assert challenge_response.rc4.generator_length == 1
    assert challenge_response.rc4.generator == 7
    assert challenge_response.rc4.prime_length == 32
    assert (
        challenge_response.rc4.prime
        == 62100066509156017342069496140902949863249758336000796928566441170293728648119
    )
    assert challenge_response.rc4.salt == int.from_bytes(
        packet[70:102], "little", signed=False
    )
    assert ChallengeResponse.build(challenge_response) == packet


def test_challenge_response_named_args():
    packet = ChallengeResponse.build(
        dict(
            rc4=dict(
                server_public=37573892888418226681312157480058717812018111076215085243857638337566340538151,
                gen_len=1,
                generator=7,
                prime_len=32,
                prime=62100066509156017342069496140902949863249758336000796928566441170293728648119,
                salt=105907935957727809645867901940389592363084317324947500788246621423699503519537,
                checksum=0,
                security_flag=0,
            )
        )
    )

    challenge_response = ChallengeResponse.parse(packet)
    assert challenge_response.header.opcode == Opcode.login_challenge
    assert challenge_response.response == Response.success
    assert (
        challenge_response.rc4.server_public
        == 37573892888418226681312157480058717812018111076215085243857638337566340538151
    )
    assert challenge_response.rc4.generator_length == 1
    assert challenge_response.rc4.generator == 7
    assert challenge_response.rc4.prime_length == 32
    assert (
        challenge_response.rc4.prime
        == 62100066509156017342069496140902949863249758336000796928566441170293728648119
    )
    assert (
        challenge_response.rc4.salt
        == 105907935957727809645867901940389592363084317324947500788246621423699503519537
    )

    assert ChallengeResponse.build(challenge_response) == packet

    data = bytes.fromhex(
        "000000675f54d1e65a382bc343730cac11dcaa4c0204a1a45a3e87c4b31bed6933eb55010720b79b3e2a87823cab8f5ebfbf8eb10108535006298b5badbd5b53e1895e644b8979604517f018fa18b3b99bb764cbcb33bed1e3db2ccc17bac1a2cb062e86cdd40166742b495c252c46876a1a3e7d18e200"
    )
    szn_response = ChallengeResponse.parse(data)
    print(szn_response)


def test_proof_request_packet1():
    packet = bytes.fromhex(
        "01aab3826c0963de7881f5741733d7b8c2fb98b6f14bf33a790e6d376793895a06f122681f01b74c8b4100f5856fbcc03d80da65f378f6fd38b5843abf6884d7ca207b4187b84ec6d10000"
    )
    proof_request = ProofRequest.parse(packet)

    assert proof_request.opcode == Opcode.login_proof
    assert proof_request.client_public == bytes_to_int(packet[1:33])
    assert proof_request.session_proof == bytes_to_int(packet[33:53])
    assert proof_request.checksum == bytes_to_int(packet[53:73])
    assert proof_request.num_keys == 0

    assert proof_request.security_flags == 0
    assert ProofRequest.build(proof_request) == packet

    szn_data = bytes.fromhex(
        "01c37ba092fdd5896322660a26247140e03691b2a3176228bc907a3809340bf124734b27330d66a2b2a63c79418743b139de9e1ef6deb96d9392a937bef78f0c38ed8754edcf53ce000000"
    )
    print(ProofRequest.parse(szn_data))

    warmane_bug_data = bytes.fromhex(
        "01b4a0084c3e0260a8c32fe49c363ec6078a6fa1c30abf02d6278bc89bee6c7e534419fc8c94bc9609cf870e9a05069515f716df542183affc8ca868831d2afed8df801855eb64174c0000"
    )
    print(ProofRequest.parse(warmane_bug_data))

    warmane_bug_data = bytes.fromhex(
        "01ea44fac86a0b894ca2b75a8f8054e4eae6f5ae342dc3431670c6954045f2b86ed243118a0c1d66baeecb4235b639272bf8436b44939342b73292c7b7b8f4a3dbe87656b4729d50f40000"
    )
    print(ProofRequest.parse(warmane_bug_data))


def test_proof_request_packet2():
    packet = ProofRequest.build(
        {
            "client_public": 77210350023438834003517310668311813995313295286472098864964747603624128502278,
            "session_proof": 1376634071334066614958602446639008698865859323379,
            "checksum": 690586934523129401082830062357295166614403991249,
        }
    )

    proof_request = ProofRequest.parse(packet)
    assert (
        proof_request.client_public
        == 77210350023438834003517310668311813995313295286472098864964747603624128502278
    )
    assert (
        proof_request.session_proof == 1376634071334066614958602446639008698865859323379
    )
    assert proof_request.checksum == 690586934523129401082830062357295166614403991249

    assert ProofRequest.build(proof_request) == packet


def test_proof_response_packet1():
    packet = bytes.fromhex(
        "0100503e596c7ffe437f1d87506014552473877fc2ff00008000000000000000"
    )
    proof_response = ProofResponse.parse(packet)
    assert proof_response.header.opcode == Opcode.login_proof
    assert proof_response.header.response == Response.success
    assert proof_response.session_proof_hash == bytes_to_int(packet[2:22])
    assert proof_response.account_flags == 32768
    assert proof_response.survey_id == 0
    assert proof_response.login_flags == 0

    assert ProofResponse.build(proof_response) == packet


def test_proof_response_packet2():
    packet = ProofResponse.build(
        dict(session_proof_hash=1460130100480076755268286359902044858927415901776)
    )

    proof_response = ProofResponse.parse(packet)
    print(f"{proof_response=}")
    assert (
        proof_response.session_proof_hash
        == 1460130100480076755268286359902044858927415901776
    )
    assert proof_response.header.opcode == Opcode.login_proof
    assert proof_response.header.response == Response.success
    assert proof_response.login_flags == 0
    assert proof_response.survey_id == 0
    assert proof_response.account_flags == 32768
    assert ProofResponse.build(proof_response) == packet


def test_realmlist_response_decode_encode():
    data = b"\x10\x87\x00\x00\x00\x00\x00\x03\x00\x01\x00\x00Blackrock [PvP only]\x0054.36.105.147:8086\x00\x00\x00\x00\x00\x08\x08\n\x01\x00\x00Icecrown\x0054.36.105.148:8085\x00\x00\x00@@\n\x08\x07\x01\x00\x00Lordaeron\x0054.36.105.146:9427\x00\x00\x00\x00@\x03\x08\x06"
    realmlist_response = RealmlistResponse.parse(data)
    assert len(realmlist_response.realms) == 3

    calculated_size = 8
    for realm in realmlist_response.realms:
        calculated_size += (
            3 + len(realm.name) + 1 + len(":".join(map(str, realm.address))) + 1 + 4 + 3
        )
        if (realm.flags & RealmFlags.specify_build) == RealmFlags.specify_build.value:
            calculated_size += 5

    assert realmlist_response.size == calculated_size
    assert realmlist_response.realms[0].name == "Blackrock [PvP only]"
    assert realmlist_response.realms[0].type == RealmType.pvp
    assert realmlist_response.realms[0].status == RealmStatus.online
    # assert realmlist_response.realms[0].population == RealmPopulation.low
    assert realmlist_response.realms[0].flags == RealmFlags.none
    assert realmlist_response.realms[0].address == ("54.36.105.147", 8086)
    assert realmlist_response.realms[0].num_characters == 8
    assert realmlist_response.realms[0].timezone == 8

    assert realmlist_response.realms[1].name == "Icecrown"
    assert realmlist_response.realms[1].type == RealmType.pvp
    assert realmlist_response.realms[1].status == RealmStatus.online
    # assert realmlist_response.realms[1].population == RealmPopulation.high
    assert realmlist_response.realms[1].flags == RealmFlags.none
    assert realmlist_response.realms[1].address == ("54.36.105.148", 8085)
    assert realmlist_response.realms[1].num_characters == 10
    assert realmlist_response.realms[1].timezone == 8

    assert realmlist_response.realms[2].name == "Lordaeron"
    assert realmlist_response.realms[2].type == RealmType.pvp
    assert realmlist_response.realms[2].status == RealmStatus.online
    # assert realmlist_response.realms[2].population == RealmPopulation.medium
    assert realmlist_response.realms[2].flags == RealmFlags.none
    assert realmlist_response.realms[2].address == ("54.36.105.146", 9427)
    assert realmlist_response.realms[2].num_characters == 3
    assert realmlist_response.realms[2].timezone == 8
    assert RealmlistResponse.build(realmlist_response) == data

    # With build info specified
    data2 = b"\x10g\x00\x00\x00\x00\x00\x02\x00\x01\x00\x04Frosthold\x0051.91.152.139:19090\x00\x00\x00\x00\x00\x01\x05\x04\x03\x03\x0540\x01\x00\x04Frosthold Proxy\x0046.29.17.245:47212\x00\x00\x00\x00\x00\x00\x05\n\x03\x03\x0540\x10\x00"
    response2 = RealmlistResponse.parse(data2)

    assert response2.realms[0].type == RealmType.pvp
    assert response2.realms[0].status == RealmStatus.online
    assert response2.realms[0].flags == RealmFlags.specify_build
    assert response2.realms[0].address == ("51.91.152.139", 19090)
    assert response2.realms[0].name == "Frosthold"
    assert response2.realms[0].num_characters == 1
    assert response2.realms[0].timezone == 5
    assert response2.realms[0].id == 4
    assert response2.realms[0].build_info.major == 3
    assert response2.realms[0].build_info.minor == 3
    assert response2.realms[0].build_info.bugfix == 5
    assert response2.realms[0].build_info.build == 12340

    assert response2.realms[1].type == RealmType.pvp
    assert response2.realms[1].status == RealmStatus.online
    assert response2.realms[1].flags == RealmFlags.specify_build
    assert response2.realms[1].address == ("46.29.17.245", 47212)
    assert response2.realms[1].name == "Frosthold Proxy"
    assert response2.realms[1].num_characters == 0
    assert response2.realms[1].timezone == 5
    assert response2.realms[1].id == 10
    assert response2.realms[1].build_info.major == 3
    assert response2.realms[1].build_info.minor == 3
    assert response2.realms[1].build_info.bugfix == 5
    assert response2.realms[1].build_info.build == 12340
