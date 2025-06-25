#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/*
 * Projekt BitsCoin 2025 - Zaktualizowany z Portfelem
 * Autorzy: Grupa Siedemtrzy
 * Fork SHA-256 – niezależna sieć BitsCoin
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */
"""

import hashlib, time, json, threading
from wallet import BitsCoinWallet

class Block:
    def __init__(self, index, prev_hash, timestamp, data, nonce=0):
        self.index = index
        self.previous_hash = prev_hash
        self.timestamp = timestamp
        self.data = data
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        s = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(s).hexdigest()

class Blockchain:
    def __init__(self, difficulty=4, reward=50):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.reward = reward
        self.wallet = BitsCoinWallet()

    def create_genesis_block(self):
        # Genesis block z premine
        genesis = Block(0, "0", time.time(), "Genesis Block: BitsCoin 2025 Launch", 0)
        genesis.hash = genesis.compute_hash()
        return genesis

    def last_block(self): 
        return self.chain[-1]

    def proof_of_work(self, block):
        target = "0" * self.difficulty
        start = time.time()
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.compute_hash()
        return time.time() - start

    def add_block(self, miner_address=""):
        """Dodaje nowy blok z nagrodą dla prawdziwego adresu"""
        prev = self.last_block()
        
        # Jeśli nie podano adresu, użyj pierwszego z portfela
        if not miner_address:
            addresses = self.wallet.get_addresses()
            if addresses:
                miner_address = addresses[0]
            else:
                miner_address = "unknown_miner"
        
        blk = Block(prev.index+1, prev.hash, time.time(),
                    f"Reward to {miner_address}: {self.reward} BSC")
        t = self.proof_of_work(blk)
        self.chain.append(blk)
        return blk, round(t, 2)

    def start_mining(self, miner_address=""):
        """Uruchamia mining na określony adres"""
        def mine():
            while True:
                blk, t = self.add_block(miner_address)
                print(f"⛏️  Mined block #{blk.index} in {t}s")
                print(f"   Reward: {self.reward} BSC -> {miner_address}")
                print(f"   Hash: {blk.hash}")
                print()
        threading.Thread(target=mine, daemon=True).start()

    def get_balance(self, address):
        """Oblicza saldo dla adresu"""
        balance = 0
        for blk in self.chain[1:]:  # Pomiń genesis
            data = blk.data
            if f"Reward to {address}" in data:
                balance += self.reward
            # Dodaj obsługę transakcji
            if "TX {" in data:
                try:
                    tx_start = data.find("TX {")
                    tx_part = data[tx_start+3:]
                    tx_dict = eval(tx_part.split("}")[0] + "}")
                    
                    if tx_dict.get("to") == address:
                        balance += float(tx_dict.get("amount", 0))
                    elif tx_dict.get("from") == address:
                        balance -= float(tx_dict.get("amount", 0))
                except:
                    pass
        return balance

    def show_status(self):
        """Pokaż status blockchain i sald"""
        print(f"\n=== BitsCoin Blockchain Status ===")
        print(f"Blocks: {len(self.chain)}")
        print(f"Difficulty: {self.difficulty}")
        print(f"Block Reward: {self.reward} BSC")
        
        print(f"\n=== Wallet Balances ===")
        for addr in self.wallet.get_addresses():
            balance = self.get_balance(addr)
            print(f"{addr}: {balance} BSC")

if __name__=="__main__":
    bc = Blockchain(difficulty=4)
    
    # Sprawdź czy mamy adresy w portfelu
    if not bc.wallet.get_addresses():
        print("No addresses in wallet! Creating new address...")
        addr = bc.wallet.create_new_address("Mining Address")
        print(f"Created mining address: {addr}")
    
    mining_addr = bc.wallet.get_addresses()[0]
    print(f"Starting mining to address: {mining_addr}")
    print("Mining BitsCoin... Ctrl+C to stop")
    
    bc.start_mining(mining_addr)
    
    try:
        while True:
            time.sleep(5)
            bc.show_status()
    except KeyboardInterrupt:
        print(f"\nMining stopped!")
        bc.show_status()
        
        # Zapisz blockchain
        with open("chain.json","w") as f:
            json.dump([b.__dict__ for b in bc.chain], f, indent=2)
        print("Blockchain saved to chain.json")
