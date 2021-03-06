#!/usr/bin/env python3
import time
import os
from decimal import *

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
from test_framework.test_helper import get_dumpwallet_otp

#Scenario:
#Generate 101 block
#Mint zerocoins of all denominations multiple 3
#generate 6 blocks
#spend zerocoin of all denominations
#generate one block
#getlistunspendzerocoins
#getlistspendzerocoins
#dumpwallet
#importwallet
#verify actual list unspendzerocoins
#verify actual list spend zerocoins

class WalletDumpZerocoinTest(BitcoinTestFramework):
    def __init__(self):
        super().__init__()
        self.num_nodes = 4
        self.setup_clean_chain = False

    def setup_nodes(self):
        # This test requires mocktime
        enable_mocktime()
        return start_nodes(self.num_nodes, self.options.tmpdir)

    def run_test(self):
        getcontext().prec = 6
        self.nodes[0].generate(101)
        self.sync_all()

        lava_denoms = [1, 10, 25, 50, 100]

        # make confirmed mints and spends
        for denom in lava_denoms:
            self.nodes[0].mintzerocoin(denom)
            self.nodes[0].mintzerocoin(denom)
            self.nodes[0].mintzerocoin(denom)

        self.nodes[0].generate(6)
        
        for denom in lava_denoms:
            self.nodes[0].spendzerocoin(denom)

        self.nodes[0].generate(1)

        #get list of unspent mints and spends, mints
        lava_mints = self.nodes[0].listmintzerocoins().sort(key=lambda x: x['id'], reverse=False)
        lava_unspentmints = self.nodes[0].listunspentmintzerocoins().sort(key=lambda x: x['txid'], reverse=False)
        lava_spendlavas = self.nodes[0].listspendzerocoins(100).sort(key=lambda x: x['txid'], reverse=False)
        tmpdir = self.options.tmpdir

        try:
            self.nodes[0].dumpwallet(tmpdir + "/node0/wallet.unencrypted.dump")
        except Exception as ex:
            key = get_dumpwallet_otp(ex.error['message'])
            self.nodes[0].dumpwallet(tmpdir + "/node0/wallet.unencrypted.dump", key)
        
        stop_node(self.nodes[0], 0)
        os.remove(self.options.tmpdir + "/node0/regtest/wallet.dat")
        start_node(0, self.options.tmpdir)

        self.nodes[0].importwallet(tmpdir + "/node0/wallet.unencrypted.dump")

        exp_lava_mints = self.nodes[0].listmintzerocoins().sort(key=lambda x: x['id'], reverse=False)
        exp_lava_unspentmints = self.nodes[0].listunspentmintzerocoins().sort(key=lambda x: x['txid'], reverse=False)
        exp_lava_spendlavas = self.nodes[0].listspendzerocoins(100).sort(key=lambda x: x['txid'], reverse=False)

        assert_equal(exp_lava_mints, lava_mints)
        assert_equal(exp_lava_unspentmints, lava_unspentmints)
        assert_equal(exp_lava_spendlavas, lava_spendlavas)

if __name__ == '__main__':
    WalletDumpZerocoinTest().main()
