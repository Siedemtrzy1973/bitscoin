#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/*
 * Projekt BitsCoin 2025
 * Autorzy: Grupa Siedemtrzy
 * Fork SHA-256 – niezależna sieć BitsCoin
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */
"""

import sys, os
# Dodaj katalog projektu (bitscoin2025) do ścieżki modułów Pythona
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..")))

import time
import threading
import json
from core.bitscoin import Blockchain

# Lista pracowników (miner IDs). Możesz tu dodać swoje identyfikatory.
workers = ["miner1", "miner2", "miner3"]

def pool_mine(bc):
    idx = 0
    while True:
        miner = workers[idx % len(workers)]
        blk, t = bc.add_block(miner)
        print(f"[Pool] {miner} wykopał blok #{blk.index} w {t}s, hash={blk.hash}")
        idx += 1
        time.sleep(0.1)  # krótka przerwa między zadaniami

if __name__ == "__main__":
    # Inicjalizacja łańcucha z difficulty=4, reward=50
    bc = Blockchain(difficulty=4, reward=50)
    print("Uruchamiam pool… Ctrl+C aby zatrzymać")
    # Start wątku miningowego
    threading.Thread(target=pool_mine, args=(bc,), daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPool zatrzymany.")
        # Zapisz finalny chain do core/chain.json
        chain_path = os.path.abspath(os.path.join(__file__, "..", "..", "core", "chain.json"))
        with open(chain_path, "w") as f:
            json.dump([b.__dict__ for b in bc.chain], f, indent=2)
        print(f"Chain zapisany do {chain_path}")
