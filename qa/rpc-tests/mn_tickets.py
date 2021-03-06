#!/usr/bin/env python2
# Copyright (c) 2018-19 The Pastel developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
from __future__ import print_function

from test_framework.util import assert_equal, assert_greater_than, \
    assert_true, initialize_chain_clean
from mn_common import MasterNodeCommon
from test_framework.authproxy import JSONRPCException
import json
import time
import base64

from decimal import getcontext
getcontext().prec = 16

# 12 Master Nodes
private_keys_list = ["91sY9h4AQ62bAhNk1aJ7uJeSnQzSFtz7QmW5imrKmiACm7QJLXe",  # 0
                     "923JtwGJqK6mwmzVkLiG6mbLkhk1ofKE1addiM8CYpCHFdHDNGo",  # 1
                     "91wLgtFJxdSRLJGTtbzns5YQYFtyYLwHhqgj19qnrLCa1j5Hp5Z",  # 2
                     "92XctTrjQbRwEAAMNEwKqbiSAJsBNuiR2B8vhkzDX4ZWQXrckZv",  # 3
                     "923JCnYet1pNehN6Dy4Ddta1cXnmpSiZSLbtB9sMRM1r85TWym6",  # 4
                     "93BdbmxmGp6EtxFEX17FNqs2rQfLD5FMPWoN1W58KEQR24p8A6j",  # 5
                     "92av9uhRBgwv5ugeNDrioyDJ6TADrM6SP7xoEqGMnRPn25nzviq",  # 6
                     "91oHXFR2NVpUtBiJk37i8oBMChaQRbGjhnzWjN9KQ8LeAW7JBdN",  # 7
                     "92MwGh67mKTcPPTCMpBA6tPkEE5AK3ydd87VPn8rNxtzCmYf9Yb",  # 8
                     "92VSXXnFgArfsiQwuzxSAjSRuDkuirE1Vf7KvSX7JE51dExXtrc",  # 9
                     "91hruvJfyRFjo7JMKnAPqCXAMiJqecSfzn9vKWBck2bKJ9CCRuo",  # 10
                     "92sYv5JQHzn3UDU6sYe5kWdoSWEc6B98nyY5JN7FnTTreP8UNrq",  # 11
                     "92pfBHQaf5K2XBnFjhLaALjhCqV8Age3qUgJ8j8oDB5eESFErsM"   # 12
                     ]


class MasterNodeTicketsTest(MasterNodeCommon):
    number_of_master_nodes = len(private_keys_list)
    number_of_simple_nodes = 3
    total_number_of_nodes = number_of_master_nodes+number_of_simple_nodes

    non_active_mn = number_of_master_nodes-1

    non_mn1 = number_of_master_nodes        # mining node - will have coins #13
    non_mn2 = number_of_master_nodes+1      # hot node - will have collateral for all active MN #14
    non_mn3 = number_of_master_nodes+2      # will not have coins by default #15

    mining_node_num = number_of_master_nodes    # same as non_mn1
    hot_node_num = number_of_master_nodes+1     # same as non_mn2

    def __init__(self):
        self.errorString = ""
        self.is_network_split = False
        self.nodes = []
        self.storage_fee = 100
        self.storage_fee90percent = self.storage_fee*9/10
        self.mn0_pastelid1 = None
        self.mn0_pastelid2 = None
        self.non_active_mn_pastelid1 = None
        self.nonmn1_pastelid2 = None
        self.nonmn3_pastelid1 = None
        self.mn0_ticket1_txid = None
        self.nonmn3_address1 = None
        self.artist_pastelid1 = None
        self.artist_ticket_height = None
        self.ticket_signature_artist = None
        self.art_ticket1_txid = None
        self.top_mns_index0 = None
        self.top_mns_index1 = None
        self.top_mns_index2 = None
        self.top_mn_pastelid0 = None
        self.top_mn_pastelid1 = None
        self.top_mn_pastelid2 = None
        self.top_mn_ticket_signature0 = None
        self.top_mn_ticket_signature1 = None
        self.top_mn_ticket_signature2 = None

    def setup_chain(self):
        print("Initializing test directory "+self.options.tmpdir)
        initialize_chain_clean(self.options.tmpdir, self.total_number_of_nodes)

    def setup_network(self, split=False):
        self.setup_masternodes_network(private_keys_list, self.number_of_simple_nodes)

    def run_test(self):

        self.mining_enough(self.mining_node_num, self.number_of_master_nodes)
        cold_nodes = {k: v for k, v in enumerate(private_keys_list[:-1])}  # all but last!!!
        _, _, _ = self.start_mn(self.mining_node_num, self.hot_node_num, cold_nodes, self.total_number_of_nodes)

        self.reconnect_nodes(0, self.number_of_master_nodes)
        self.sync_all()

        self.pastelid_tests()
        self.pastelid_ticket_tests()
        self.artreg_ticket_tests()
        self.artact_ticket_tests()
        self.arttrade_ticket_tests()
        self.takedown_ticket_tests()
        self.storage_fee_tests()

    # ===============================================================================================================
    def pastelid_tests(self):
        print("== Pastelid test ==")
        # 1. pastelid tests
        # a. Generate new PastelID and associated keys (EdDSA448). Return PastelID base58-encoded
        # a.a - generate with no errors two keys at MN and non-MN

        self.mn0_pastelid1 = self.nodes[0].pastelid("newkey", "passphrase")["pastelid"]
        assert_true(self.mn0_pastelid1, "No Pastelid was created")
        self.mn0_pastelid2 = self.nodes[0].pastelid("newkey", "passphrase")["pastelid"]
        assert_true(self.mn0_pastelid2, "No Pastelid was created")

        # for non active MN
        self.non_active_mn_pastelid1 = self.nodes[self.non_active_mn].pastelid("newkey", "passphrase")["pastelid"]
        assert_true(self.non_active_mn_pastelid1, "No Pastelid was created")

        nonmn1_pastelid1 = self.nodes[self.non_mn1].pastelid("newkey", "passphrase")["pastelid"]
        assert_true(nonmn1_pastelid1, "No Pastelid was created")
        self.nonmn1_pastelid2 = self.nodes[self.non_mn1].pastelid("newkey", "passphrase")["pastelid"]
        assert_true(self.nonmn1_pastelid2, "No Pastelid was created")

        # for node without coins
        self.nonmn3_pastelid1 = self.nodes[self.non_mn3].pastelid("newkey", "passphrase")["pastelid"]
        assert_true(self.nonmn3_pastelid1, "No Pastelid was created")

        # a.b - fail if empty passphrase
        try:
            self.nodes[self.non_mn1].pastelid("newkey", "")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("passphrase for new key cannot be empty" in self.errorString, True)

        # b. Import private "key" (EdDSA448) as PKCS8 encrypted string in PEM format. Return PastelID base58-encoded
        # NOT IMPLEMENTED

        # c. List all internally stored PastelID and keys
        id_list = self.nodes[0].pastelid("list")
        id_list = dict((key+str(i), val) for i, k in enumerate(id_list) for key, val in k.items())
        assert_true(self.mn0_pastelid1 in id_list.values(), "PastelID " + self.mn0_pastelid1 + " not in the list")
        assert_true(self.mn0_pastelid2 in id_list.values(), "PastelID " + self.mn0_pastelid2 + " not in the list")

        id_list = self.nodes[self.non_mn1].pastelid("list")
        id_list = dict((key+str(i), val) for i, k in enumerate(id_list) for key, val in k.items())
        assert_true(nonmn1_pastelid1 in id_list.values(), "PastelID " + nonmn1_pastelid1 + " not in the list")
        assert_true(self.nonmn1_pastelid2 in id_list.values(), "PastelID " + self.nonmn1_pastelid2 + " not in the list")

        print("Pastelid test: 2 PastelID's each generate at node0 (MN ) and node" + str(self.non_mn1) + "(non-MN)")

        # d. Sign "text" with the internally stored private key associated with the PastelID
        # d.a - sign with no errors using key from 1.a.a
        mn0_signature1 = self.nodes[0].pastelid("sign", "1234567890", self.mn0_pastelid1, "passphrase")["signature"]
        assert_true(mn0_signature1, "No signature was created")
        assert_equal(len(base64.b64decode(mn0_signature1)), 114)

        # e. Sign "text" with the private "key" (EdDSA448) as PKCS8 encrypted string in PEM format
        # NOT IMPLEMENTED

        # f. Verify "text"'s "signature" with the PastelID
        # f.a - verify with no errors using key from 1.a.a
        result = self.nodes[0].pastelid("verify", "1234567890", mn0_signature1, self.mn0_pastelid1)["verification"]
        assert_equal(result, "OK")
        # f.b - fail to verify with the different key from 1.a.a
        result = self.nodes[0].pastelid("verify", "1234567890", mn0_signature1, self.mn0_pastelid2)["verification"]
        assert_equal(result, "Failed")
        # f.c - fail to verify modified text
        result = self.nodes[0].pastelid("verify", "1234567890AAA", mn0_signature1, self.mn0_pastelid1)["verification"]
        assert_equal(result, "Failed")

        print("Pastelid test: Message signed and verified")

    # ===============================================================================================================
    def pastelid_ticket_tests(self):
        print("== Masternode PastelID Tickets test ==")
        # 2. tickets tests
        # a. PastelID ticket
        #   a.a register MN PastelID
        #       a.a.1 fail if not MN
        try:
            self.nodes[self.non_mn1].tickets("register", "mnid", self.nonmn1_pastelid2, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("This is not an active masternode" in self.errorString, True)

        #       a.a.2 fail if not active MN
        try:
            self.nodes[self.non_active_mn].tickets("register", "mnid", self.non_active_mn_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("This is not an active masternode" in self.errorString, True)

        #       a.a.3 fail if active MN, but wrong PastelID
        try:
            self.nodes[0].tickets("register", "mnid", self.nonmn1_pastelid2, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot open file to read key from" in self.errorString, True)  # TODO: provide better error for unknown PastelID

        #       a.a.4 fail if active MN, but wrong passphrase
        try:
            self.nodes[0].tickets("register", "mnid", self.mn0_pastelid1, "wrong")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot read key from string" in self.errorString, True)  # TODO: provide better error for wrong passphrase

        #       a.a.5 fail if active MN, but not enough coins - ~11PSL
        try:
            self.nodes[0].tickets("register", "mnid", self.mn0_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("No unspent transaction found" in self.errorString, True)

        #       a.a.6 register without errors from active MN with enough coins
        mn0_address1 = self.nodes[0].getnewaddress()
        self.nodes[self.mining_node_num].sendtoaddress(mn0_address1, 100, "", "", False)
        time.sleep(2)
        self.sync_all()
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all()

        coins_before = self.nodes[0].getbalance()
        # print(coins_before)

        self.mn0_ticket1_txid = self.nodes[0].tickets("register", "mnid", self.mn0_pastelid1, "passphrase")["txid"]
        assert_true(self.mn0_ticket1_txid, "No ticket was created")
        time.sleep(2)
        self.sync_all()
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all()

        #       a.a.7 check correct amount of change
        coins_after = self.nodes[0].getbalance()
        # print(coins_after)
        assert_equal(coins_after, coins_before - 10)  # no fee yet

        #       a.a.8 from another node - get ticket transaction and check
        #           - there are P2MS outputs with non-zero amounts
        #           - amounts is totaling 10PSL
        mn0_ticket1_tx_hash = self.nodes[self.non_mn3].getrawtransaction(self.mn0_ticket1_txid)
        mn0_ticket1_tx = self.nodes[self.non_mn3].decoderawtransaction(mn0_ticket1_tx_hash)
        amount = 0
        for v in mn0_ticket1_tx["vout"]:
            assert_greater_than(v["value"], 0)
            if v["scriptPubKey"]["type"] == "multisig":
                amount += v["value"]
        assert_equal(amount, 10)

        #       a.a.9.1 fail if PastelID is already registered
        try:
            self.nodes[0].tickets("register", "mnid", self.mn0_pastelid1, "passphrase")["txid"]
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("This PastelID is already registered in blockchain" in self.errorString, True)

        #       a.a.9.2 fail if outpoint is already registered
        try:
            self.nodes[0].tickets("register", "mnid", self.mn0_pastelid2, "passphrase")["txid"]
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Ticket (pastelid) is invalid - Masternode's outpoint" in self.errorString, True)

        #   a.b find MN PastelID ticket
        #       a.b.1 by PastelID
        mn0_ticket1_1 = json.loads(self.nodes[self.non_mn3].tickets("find", "id", self.mn0_pastelid1))
        assert_equal(mn0_ticket1_1["ticket"]["pastelID"], self.mn0_pastelid1)
        assert_equal(mn0_ticket1_1['ticket']['type'], "pastelid")
        assert_equal(mn0_ticket1_1['ticket']['id_type'], "masternode")

        #       a.b.2 by Collateral output, compare to ticket from a.b.1
        mn0_outpoint = self.nodes[0].masternode("status")["outpoint"]
        mn0_ticket1_2 = json.loads(self.nodes[self.non_mn3].tickets("find", "id", mn0_outpoint))
        assert_equal(mn0_ticket1_1["ticket"]["signature"], mn0_ticket1_2["ticket"]["signature"])
        assert_equal(mn0_ticket1_1["ticket"]["outpoint"], mn0_outpoint)

        #   a.c get the same ticket by txid from a.a.3 and compare with ticket from a.b.1
        mn0_ticket1_3 = json.loads(self.nodes[self.non_mn3].tickets("get", self.mn0_ticket1_txid))
        assert_equal(mn0_ticket1_1["ticket"]["signature"], mn0_ticket1_3["ticket"]["signature"])

        #   a.d list all id tickets, check PastelIDs
        tickets_list = self.nodes[self.non_mn3].tickets("list", "id")
        assert_true(self.mn0_pastelid1 in tickets_list)
        assert_true(mn0_outpoint in tickets_list)

        print("MN PastelID tickets tested")

        # ===============================================================================================================
        print("== Personal PastelID Tickets test ==")
        # b. personal PastelID ticket
        self.nonmn3_address1 = self.nodes[self.non_mn3].getnewaddress()

        #   b.a register personal PastelID
        #       b.a.1 fail if wrong PastelID
        try:
            self.nodes[self.non_mn3].tickets("register", "id", self.nonmn1_pastelid2, "passphrase", self.nonmn3_address1)
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot open file to read key from" in self.errorString, True)  # TODO Pastel: provide better error for unknown PastelID

        #       b.a.2 fail if wrong passphrase
        try:
            self.nodes[self.non_mn3].tickets("register", "id", self.nonmn3_pastelid1, "wrong", self.nonmn3_address1)
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot read key from string" in self.errorString, True)  # TODO Pastel: provide better error for wrong passphrase

        #       b.a.3 fail if not enough coins - ~11PSL
        try:
            self.nodes[self.non_mn3].tickets("register", "id", self.nonmn3_pastelid1, "passphrase", self.nonmn3_address1)
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("No unspent transaction found" in self.errorString, True)

        #       b.a.4 register without errors from non MN with enough coins
        self.nodes[self.mining_node_num].sendtoaddress(self.nonmn3_address1, 100, "", "", False)
        time.sleep(2)
        self.sync_all()
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all()

        coins_before = self.nodes[self.non_mn3].getbalance()
        # print(coins_before)

        nonmn3_ticket1_txid = self.nodes[self.non_mn3].tickets("register", "id", self.nonmn3_pastelid1, "passphrase", self.nonmn3_address1)["txid"]
        assert_true(nonmn3_ticket1_txid, "No ticket was created")
        time.sleep(2)
        self.sync_all()
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all()

        #       a.a.5 check correct amount of change
        coins_after = self.nodes[self.non_mn3].getbalance()
        # print(coins_after)
        assert_equal(coins_after, coins_before - 10)  # no fee yet

        #       b.a.6 from another node - get ticket transaction and check
        #           - there are P2MS outputs with non-zero amounts
        #           - amounts is totaling 10PSL
        nonmn3_ticket1_tx_hash = self.nodes[0].getrawtransaction(nonmn3_ticket1_txid)
        nonmn3_ticket1_tx = self.nodes[0].decoderawtransaction(nonmn3_ticket1_tx_hash)
        amount = 0
        for v in nonmn3_ticket1_tx["vout"]:
            assert_greater_than(v["value"], 0)
            if v["scriptPubKey"]["type"] == "multisig":
                amount += v["value"]
        assert_equal(amount, 10)

        #       b.a.7 fail if already registered
        try:
            self.nodes[self.non_mn3].tickets("register", "id", self.nonmn3_pastelid1, "passphrase", self.nonmn3_address1)
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("This PastelID is already registered in blockchain" in self.errorString, True)

        #   b.b find personal PastelID
        #       b.b.1 by PastelID
        nonmn3_ticket1_1 = json.loads(self.nodes[0].tickets("find", "id", self.nonmn3_pastelid1))
        assert_equal(nonmn3_ticket1_1["ticket"]["pastelID"], self.nonmn3_pastelid1)
        assert_equal(nonmn3_ticket1_1['ticket']['type'], "pastelid")
        assert_equal(nonmn3_ticket1_1['ticket']['id_type'], "personal")

        #       b.b.2 by Address
        nonmn3_ticket1_2 = json.loads(self.nodes[0].tickets("find", "id", self.nonmn3_address1))
        assert_equal(nonmn3_ticket1_1["ticket"]["signature"], nonmn3_ticket1_2["ticket"]["signature"])

        #   b.c get the ticket by txid from b.a.3 and compare with ticket from b.b.1
        nonmn3_ticket1_3 = json.loads(self.nodes[self.non_mn3].tickets("get", nonmn3_ticket1_txid))
        assert_equal(nonmn3_ticket1_1["ticket"]["signature"], nonmn3_ticket1_3["ticket"]["signature"])

        #   b.d list all id tickets, check PastelIDs
        tickets_list = self.nodes[0].tickets("list", "id")
        assert_true(self.nonmn3_pastelid1 in tickets_list)
        assert_true(self.nonmn3_address1 in tickets_list)

        print("Personal PastelID tickets tested")

    # ===============================================================================================================
    def artreg_ticket_tests(self):
        print("== Art registration Tickets test ==")
        # c. art registration ticket

        self.nodes[self.mining_node_num].generate(10)

        mn_addresses = {}
        mn_pastelids = {}
        mn_outpoints = {}
        mn_ticket_signatures = {}

        # generate pastelIDs
        self.artist_pastelid1 = self.nodes[self.non_mn3].pastelid("newkey", "passphrase")["pastelid"]
        non_registered_personal_pastelid1 = self.nodes[self.non_mn3].pastelid("newkey", "passphrase")["pastelid"]
        non_registered_mn_pastelid1 = self.nodes[2].pastelid("newkey", "passphrase")["pastelid"]
        for n in range(0, 12):
            mn_addresses[n] = self.nodes[n].getnewaddress()
            self.nodes[self.mining_node_num].sendtoaddress(mn_addresses[n], 100, "", "", False)
            if n == 0:
                mn_pastelids[n] = self.mn0_pastelid1  # mn0 has its PastelID registered already
            else:
                mn_pastelids[n] = self.nodes[n].pastelid("newkey", "passphrase")["pastelid"]
            mn_outpoints[self.nodes[n].masternode("status")["outpoint"]] = n

        time.sleep(2)
        self.sync_all()
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all()

        # register pastelIDs
        self.nodes[self.non_mn3].tickets("register", "id", self.artist_pastelid1, "passphrase", self.nonmn3_address1)
        for n in range(1, 12):  # mn0 has its PastelID registered already
            self.nodes[n].tickets("register", "mnid", mn_pastelids[n], "passphrase")

        time.sleep(2)
        self.sync_all()
        self.nodes[self.mining_node_num].generate(5)
        self.sync_all()

        # create ticket signature
        self.ticket_signature_artist = self.nodes[self.non_mn3].pastelid("sign", "12345", self.artist_pastelid1, "passphrase")["signature"]
        for n in range(0, 12):
            mn_ticket_signatures[n] = self.nodes[n].pastelid("sign", "12345", mn_pastelids[n], "passphrase")["signature"]

        # Get current top MNs at Node 0
        self.artist_ticket_height = self.nodes[0].getinfo()["blocks"]
        top_masternodes = self.nodes[0].masternode("top")[str(self.artist_ticket_height)]

        # print(mn_addresses)
        # print(mn_pastelids)
        # print(mn_outpoints)
        # print(mn_ticket_signatures)
        # print(self.artist_ticket_height)
        # print(top_MNs)

        top_mns_indexes = set()
        for mn in top_masternodes:
            index = mn_outpoints[mn["outpoint"]]
            top_mns_indexes.add(index)
        not_top_mns_indexes = set(mn_outpoints.values()) ^ top_mns_indexes

        # print(top_mns_indexes)
        # print(not_top_mns_indexes)

        self.top_mns_index0 = list(top_mns_indexes)[0]
        self.top_mns_index1 = list(top_mns_indexes)[1]
        self.top_mns_index2 = list(top_mns_indexes)[2]
        self.top_mn_pastelid0 = mn_pastelids[self.top_mns_index0]
        self.top_mn_pastelid1 = mn_pastelids[self.top_mns_index1]
        self.top_mn_pastelid2 = mn_pastelids[self.top_mns_index2]
        self.top_mn_ticket_signature0 = mn_ticket_signatures[self.top_mns_index0]
        self.top_mn_ticket_signature1 = mn_ticket_signatures[self.top_mns_index1]
        self.top_mn_ticket_signature2 = mn_ticket_signatures[self.top_mns_index2]

        signatures_dict = dict(
            {
                "artist": {self.artist_pastelid1: self.ticket_signature_artist},
                "mn2": {self.top_mn_pastelid1: self.top_mn_ticket_signature1},
                "mn3": {self.top_mn_pastelid2: self.top_mn_ticket_signature2},
            }
        )

        same_mns_signatures_dict = dict(
            {
                "artist": {self.artist_pastelid1: self.ticket_signature_artist},
                "mn2": {self.top_mn_pastelid0: self.top_mn_ticket_signature0},
                "mn3": {self.top_mn_pastelid0: self.top_mn_ticket_signature0},
            }
        )

    # print(signatures_dict)

        not_top_mns_index1 = list(not_top_mns_indexes)[0]
        not_top_mns_index2 = list(not_top_mns_indexes)[1]
        not_top_mn_pastelid1 = mn_pastelids[not_top_mns_index1]
        not_top_mn_pastelid2 = mn_pastelids[not_top_mns_index2]
        not_top_mn_ticket_signature1 = mn_ticket_signatures[not_top_mns_index1]
        not_top_mn_ticket_signature2 = mn_ticket_signatures[not_top_mns_index2]

        not_top_mns_signatures_dict = dict(
            {
                "artist": {self.artist_pastelid1: self.ticket_signature_artist},
                "mn2": {not_top_mn_pastelid1: not_top_mn_ticket_signature1},
                "mn3": {not_top_mn_pastelid2: not_top_mn_ticket_signature2},
            }
        )
        # print(not_top_signatures_dict)

        # print(json.dumps(not_top_signatures_dict))
        # print("artist: " + str(self.nodes[self.non_mn3].tickets("find", "id", self.nonmn3_address1)))
        # print("mn1: " + str(self.nodes[self.non_mn3].tickets("find", "id", self.mn0_pastelid1)))
        # print("mn2: " + str(self.nodes[self.non_mn3].tickets("find", "id", self.top_mn_pastelid1)))
        # print("mn3: " + str(self.nodes[self.non_mn3].tickets("find", "id", self.top_mn_pastelid2)))

        #   c.a register art registration ticket
        #       c.a.1 fail if not MN
        try:
            self.nodes[self.non_mn1].tickets("register", "art", "12345", json.dumps(signatures_dict),
                                             self.nonmn1_pastelid2, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("This is not an active masternode" in self.errorString, True)

        #       c.a.2 fail if not active MN
        try:
            self.nodes[self.non_active_mn].tickets("register", "art", "12345", json.dumps(signatures_dict),
                                                   self.non_active_mn_pastelid1, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("This is not an active masternode" in self.errorString, True)

        #       c.a.3 fail if active MN, but wrong PastelID
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.nonmn1_pastelid2, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot open file to read key from" in self.errorString, True)  # TODO: provide better error for unknown PastelID

        #       c.a.4 fail if active MN, but wrong passphrase
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "wrong", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot read key from string" in self.errorString, True)  # TODO: provide better error for wrong passphrase

        #       c.a.5 fail if artist's signature is not matching
        signatures_dict["artist"][self.artist_pastelid1] = self.top_mn_ticket_signature1
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Artist signature is invalid" in self.errorString, True)
        signatures_dict["artist"][self.artist_pastelid1] = self.ticket_signature_artist

        #       c.a.6 fail if MN2 and MN3 signatures are not matching
        signatures_dict["mn2"][self.top_mn_pastelid1] = self.top_mn_ticket_signature2
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("MN2 signature is invalid" in self.errorString, True)
        signatures_dict["mn2"][self.top_mn_pastelid1] = self.top_mn_ticket_signature1

        signatures_dict["mn3"][self.top_mn_pastelid2] = self.top_mn_ticket_signature1
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("MN3 signature is invalid" in self.errorString, True)
        signatures_dict["mn3"][self.top_mn_pastelid2] = self.top_mn_ticket_signature2

        #       c.a.7 fail if artist's PastelID is not registered
        signatures_dict["artist"][non_registered_personal_pastelid1] = self.ticket_signature_artist
        del signatures_dict["artist"][self.artist_pastelid1]
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Artist PastelID is not registered" in self.errorString, True)
        signatures_dict["artist"][self.artist_pastelid1] = self.ticket_signature_artist
        del signatures_dict["artist"][non_registered_personal_pastelid1]

        #       c.a.8 fail if artist's PastelID is not personal

        signatures_dict["artist"][self.top_mn_pastelid1] = self.top_mn_ticket_signature1
        del signatures_dict["artist"][self.artist_pastelid1]
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Artist PastelID is NOT personal PastelID" in self.errorString, True)
        signatures_dict["artist"][self.artist_pastelid1] = self.ticket_signature_artist
        del signatures_dict["artist"][self.top_mn_pastelid1]

        #       c.a.9 fail if MN PastelID is not registered
        signatures_dict["mn2"][non_registered_mn_pastelid1] = self.top_mn_ticket_signature1
        del signatures_dict["mn2"][self.top_mn_pastelid1]
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("MN2 PastelID is not registered" in self.errorString, True)
        signatures_dict["mn2"][self.top_mn_pastelid1] = self.top_mn_ticket_signature1
        del signatures_dict["mn2"][non_registered_mn_pastelid1]

        #       c.a.10 fail if MN PastelID is personal
        signatures_dict["mn2"][self.artist_pastelid1] = self.top_mn_ticket_signature1
        del signatures_dict["mn2"][self.top_mn_pastelid1]
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("MN2 PastelID is NOT masternode PastelID" in self.errorString, True)
        signatures_dict["mn2"][self.top_mn_pastelid1] = self.top_mn_ticket_signature1
        del signatures_dict["mn2"][self.artist_pastelid1]

        #       c.a.8 fail if MN1, MN2 and MN3 are not from top 10 list at the ticket's blocknum
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(not_top_mns_signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("was NOT in the top masternodes list for block" in self.errorString, True)

        #       c.a.9 fail if MN1, MN2 and MN3 are the same
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(same_mns_signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("MNs PastelIDs can not be the same" in self.errorString, True)

        #       c.a.6 register without errors, if enough coins for tnx fee
        coins_before = self.nodes[self.top_mns_index0].getbalance()
        # print(coins_before)

        self.art_ticket1_txid = self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "key2", str(self.artist_ticket_height), str(self.storage_fee))["txid"]
        assert_true(self.art_ticket1_txid, "No ticket was created")
        time.sleep(2)
        self.sync_all(30, 4)
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all(30, 4)

        #       c.a.7 check correct amount of change and correct amount spent
        coins_after = self.nodes[self.top_mns_index0].getbalance()
        # print(coins_after)
        assert_equal(coins_after, coins_before-10)  # no fee yet, but ticket cost 10 PSL

        #       c.a.8 fail if already registered
        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "key1", "newkey", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("The art with this key - [key1] is already registered in blockchain" in self.errorString, True)

        try:
            self.nodes[self.top_mns_index0].tickets("register", "art", "12345", json.dumps(signatures_dict), self.top_mn_pastelid0, "passphrase", "newkey", "key2", str(self.artist_ticket_height), str(self.storage_fee))
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("The art with this secondary key - [key2] is already registered in blockchain" in self.errorString, True)

        #   c.b find registration ticket
        #       c.b.1 by artists PastelID (this is MultiValue key)
        # TODO Pastel:

        #       c.b.2 by hash (key1 for now)
        art_ticket1_1 = json.loads(self.nodes[self.non_mn3].tickets("find", "art", "key1"))
        assert_equal(art_ticket1_1['ticket']['type'], "art-reg")
        assert_equal(art_ticket1_1['ticket']['art_ticket'], "12345")
        assert_equal(art_ticket1_1["ticket"]["key1"], "key1")
        assert_equal(art_ticket1_1["ticket"]["key2"], "key2")
        assert_equal(art_ticket1_1["ticket"]["artist_height"], self.artist_ticket_height)
        assert_equal(art_ticket1_1["ticket"]["storage_fee"], self.storage_fee)
        assert_equal(art_ticket1_1["ticket"]["signatures"]["artist"][self.artist_pastelid1], self.ticket_signature_artist)
        assert_equal(art_ticket1_1["ticket"]["signatures"]["mn2"][self.top_mn_pastelid1], self.top_mn_ticket_signature1)
        assert_equal(art_ticket1_1["ticket"]["signatures"]["mn3"][self.top_mn_pastelid2], self.top_mn_ticket_signature2)

        #       c.b.3 by fingerprints, compare to ticket from c.b.2 (key2 for now)
        art_ticket1_2 = json.loads(self.nodes[self.non_mn3].tickets("find", "art", "key2"))
        assert_equal(art_ticket1_2['ticket']['type'], "art-reg")
        assert_equal(art_ticket1_2['ticket']['art_ticket'], "12345")
        assert_equal(art_ticket1_2["ticket"]["key1"], "key1")
        assert_equal(art_ticket1_2["ticket"]["key2"], "key2")
        assert_equal(art_ticket1_2["ticket"]["artist_height"], self.artist_ticket_height)
        assert_equal(art_ticket1_2["ticket"]["storage_fee"], self.storage_fee)
        assert_equal(art_ticket1_2["ticket"]["signatures"]["artist"][self.artist_pastelid1], art_ticket1_1["ticket"]["signatures"]["artist"][self.artist_pastelid1])

        #   c.c get the same ticket by txid from c.a.6 and compare with ticket from c.b.2
        art_ticket1_3 = json.loads(self.nodes[self.non_mn3].tickets("get", self.art_ticket1_txid))
        assert_equal(art_ticket1_3["ticket"]["signatures"]["artist"][self.artist_pastelid1], art_ticket1_1["ticket"]["signatures"]["artist"][self.artist_pastelid1])

        #   c.d list all art registration tickets, check PastelIDs
        art_tickets_list = self.nodes[self.top_mns_index0].tickets("list", "art")
        assert_true("key1" in art_tickets_list)
        assert_true("key2" in art_tickets_list)

        art_tickets_by_pid = self.nodes[self.top_mns_index0].tickets("find", "art", self.artist_pastelid1)
        print(self.top_mn_pastelid0)
        print(art_tickets_by_pid)

        print("Art registration tickets tested")

    # ===============================================================================================================
    def artact_ticket_tests(self):
        print("== Art activation Tickets test ==")
        # d. art activation ticket
        #   d.a register art activation ticket (self.art_ticket1_txid; self.storage_fee; self.artist_ticket_height)
        #       d.a.1 fail if wrong PastelID
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, str(self.artist_ticket_height), str(self.storage_fee), self.top_mn_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot open file to read key from" in self.errorString, True)  # TODO Pastel: provide better error for unknown PastelID

        #       d.a.2 fail if wrong passphrase
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, str(self.artist_ticket_height), str(self.storage_fee), self.artist_pastelid1, "wrong")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("Cannot read key from string" in self.errorString, True)  # TODO Pastel: provide better error for wrong passphrase

        #       d.a.3 fail if there is not ArtTicket with this txid
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.mn0_ticket1_txid, str(self.artist_ticket_height), str(self.storage_fee), self.artist_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("The art ticket with this txid ["+self.mn0_ticket1_txid+"] is not in the blockchain" in self.errorString, True)

        #       d.a.4 fail if artist's PastelID in the activation ticket is not matching artist's PastelID in the registration ticket
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, str(self.artist_ticket_height), str(self.storage_fee), self.nonmn3_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("is not matching the Artist's PastelID" in self.errorString, True)

        #       d.a.5 fail if wrong artist ticket height
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, "55", str(self.storage_fee), self.artist_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("is not matching the artistHeight" in self.errorString, True)

        #       d.a.6 fail if wrong storage fee
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, str(self.artist_ticket_height), "55", self.artist_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("is not matching the storage fee" in self.errorString, True)

        #       d.a.7 fail if not enough coins to pay 90% of registration price (from artReg ticket) + tnx fee
        # print(self.nodes[self.non_mn3].getbalance())
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, str(self.artist_ticket_height), str(self.storage_fee), self.artist_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("No unspent transaction found" in self.errorString, True)

        #       d.a.8 register without errors, if enough coins for tnx fee
        self.nodes[self.mining_node_num].sendtoaddress(self.nonmn3_address1, 1000, "", "", False)
        time.sleep(2)
        self.sync_all(10, 30)
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all(10, 30)

        #
        mn0_collateral_address = self.nodes[self.top_mns_index0].masternode("status")["payee"]
        mn1_collateral_address = self.nodes[self.top_mns_index1].masternode("status")["payee"]
        mn2_collateral_address = self.nodes[self.top_mns_index2].masternode("status")["payee"]

        # MN's collateral addresses belong to hot_node - non_mn2
        mn0_coins_before = self.nodes[self.hot_node_num].getreceivedbyaddress(mn0_collateral_address)
        mn1_coins_before = self.nodes[self.hot_node_num].getreceivedbyaddress(mn1_collateral_address)
        mn2_coins_before = self.nodes[self.hot_node_num].getreceivedbyaddress(mn2_collateral_address)

        coins_before = self.nodes[self.non_mn3].getbalance()
        # print(coins_before)

        art_ticket1_act_ticket_txid = self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, str(self.artist_ticket_height), str(self.storage_fee), self.artist_pastelid1, "passphrase")["txid"]
        assert_true(art_ticket1_act_ticket_txid, "No ticket was created")

        time.sleep(2)
        self.sync_all(10, 30)
        self.nodes[self.mining_node_num].generate(1)
        self.sync_all(10, 30)

        #       d.a.9 check correct amount of change and correct amount spent and correct amount of fee paid
        main_mn_fee = self.storage_fee90percent*3/5
        other_mn_fee = self.storage_fee90percent/5

        coins_after = self.nodes[self.non_mn3].getbalance()
        # print(coins_after)
        assert_equal(coins_after, coins_before-self.storage_fee90percent-10)  # no fee yet, but ticket cost 10 PSL

        # MN's collateral addresses belong to hot_node - non_mn2
        mn0_coins_after = self.nodes[self.hot_node_num].getreceivedbyaddress(mn0_collateral_address)
        mn1_coins_after = self.nodes[self.hot_node_num].getreceivedbyaddress(mn1_collateral_address)
        mn2_coins_after = self.nodes[self.hot_node_num].getreceivedbyaddress(mn2_collateral_address)

        # print("mn0: before="+str(mn0_coins_before)+"; after="+str(mn0_coins_after)+". fee should be="+str(mainMN_fee))
        # print("mn1: before="+str(mn1_coins_before)+"; after="+str(mn1_coins_after)+". fee should be="+str(otherMN_fee))
        # print("mn1: before="+str(mn2_coins_before)+"; after="+str(mn2_coins_after)+". fee should be="+str(otherMN_fee))
        assert_equal(mn0_coins_after-mn0_coins_before, main_mn_fee)
        assert_equal(mn1_coins_after-mn1_coins_before, other_mn_fee)
        assert_equal(mn2_coins_after-mn2_coins_before, other_mn_fee)

        #       d.a.10 fail if already registered - Registration Ticket is already activated
        try:
            self.nodes[self.non_mn3].tickets("register", "act", self.art_ticket1_txid, str(self.artist_ticket_height), str(self.storage_fee), self.artist_pastelid1, "passphrase")
        except JSONRPCException, e:
            self.errorString = e.error['message']
            print(self.errorString)
        assert_equal("The art ticket with this txid ["+self.art_ticket1_txid+"] is already activated" in self.errorString, True)

        #       d.a.11 from another node - get ticket transaction and check
        #           - there are 3 outputs to MN1, MN2 and MN3 with correct amounts (MN1: 60%; MN2, MN3: 20% each, of registration price)
        #           - amounts is totaling 10PSL
        art_ticket1_act_ticket_hash = self.nodes[self.non_mn3].getrawtransaction(art_ticket1_act_ticket_txid)
        art_ticket1_act_ticket_tx = self.nodes[self.non_mn3].decoderawtransaction(art_ticket1_act_ticket_hash)
        amount = 0
        fee_amount = 0

        for v in art_ticket1_act_ticket_tx["vout"]:
            if v["scriptPubKey"]["type"] == "multisig":
                fee_amount += v["value"]
            if v["scriptPubKey"]["type"] == "pubkeyhash":
                if v["scriptPubKey"]["addresses"][0] == mn0_collateral_address:
                    assert_equal(v["value"], main_mn_fee)
                    amount += v["value"]
                if v["scriptPubKey"]["addresses"][0] in [mn1_collateral_address, mn2_collateral_address]:
                    assert_equal(v["value"], other_mn_fee)
                    amount += v["value"]
        assert_equal(amount, self.storage_fee90percent)
        assert_equal(fee_amount, 10)

        #   d.b find activation ticket
        #       d.b.1 by artists PastelID (this is MultiValue key)
        #       TODO Pastel: find activation ticket by artists PastelID (this is MultiValue key)

        #       d.b.3 by Registration height - artist_height from registration ticket (this is MultiValue key)
        #       TODO Pastel: find activation ticket by Registration height - artist_height from registration ticket (this is MultiValue key)

        #       d.b.2 by Registration txid - reg_txid from registration ticket, compare to ticket from d.b.2
        art_ticket1_act_ticket_1 = json.loads(self.nodes[self.non_mn1].tickets("find", "act", self.art_ticket1_txid))
        assert_equal(art_ticket1_act_ticket_1['ticket']['type'], "art-act")
        assert_equal(art_ticket1_act_ticket_1['ticket']['pastelID'], self.artist_pastelid1)
        assert_equal(art_ticket1_act_ticket_1['ticket']['reg_txid'], self.art_ticket1_txid)
        assert_equal(art_ticket1_act_ticket_1['ticket']['artist_height'], self.artist_ticket_height)
        assert_equal(art_ticket1_act_ticket_1['ticket']['storage_fee'], self.storage_fee)
        assert_equal(art_ticket1_act_ticket_1['txid'], art_ticket1_act_ticket_txid)

        #   d.c get the same ticket by txid from d.a.8 and compare with ticket from d.b.2
        art_ticket1_act_ticket_2 = json.loads(self.nodes[self.non_mn1].tickets("get", art_ticket1_act_ticket_txid))
        assert_equal(art_ticket1_act_ticket_2["ticket"]["signature"], art_ticket1_act_ticket_1["ticket"]["signature"])

        #   d.d list all art registration tickets, check PastelIDs
        act_tickets_list = self.nodes[0].tickets("list", "act")
        assert_true(self.art_ticket1_txid in act_tickets_list)

        art_tickets_by_pid = self.nodes[self.top_mns_index0].tickets("find", "act", self.artist_pastelid1)
        print(self.top_mn_pastelid0)
        print(art_tickets_by_pid)
        art_tickets_by_height = self.nodes[self.top_mns_index0].tickets("find", "act", str(self.artist_ticket_height))
        print(self.artist_ticket_height)
        print(art_tickets_by_height)

        print("Art activation tickets tested")

    # ===============================================================================================================
    def arttrade_ticket_tests(self):
        print("== Art trade Tickets test ==")
        # ...
        print("Art trade tickets tested")

    # ===============================================================================================================
    def takedown_ticket_tests(self):
        print("== Take down Tickets test ==")
        # ...
        print("Take down tickets tested")

    # ===============================================================================================================
    def storage_fee_tests(self):
        print("== Storage fee test ==")
        # 4. storagefee tests
        # a. Get Network median storage fee
        #   a.1 from non-MN without errors
        #   a.2 from MN without errors
        #   a.3 compare a.1 and a.2

        # b. Get local masternode storage fee
        #   b.1 fail from non-MN
        #   b.2 from MN without errors
        #   b.3 compare b.2 and a.1

        # c. Set storage fee for MN
        #   c.1 fail on non-MN
        #   c.2 on MN without errors
        #   c.3 get local MN storage fee and compare it with c.2
        print("Storage fee tested")


if __name__ == '__main__':
    MasterNodeTicketsTest().main()
