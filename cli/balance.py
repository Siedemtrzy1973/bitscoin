#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/*
 * Projekt BitsCoin 2025 - Balance Checker z Portfelem
 * Autorzy: Grupa Siedemtrzy
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */
"""

import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from wallet import BitsCoinWallet

def compute_balance(chain_file, address):
    """Oblicza saldo dla podanego adresu"""
    try:
        with open(chain_file) as f:
            chain = json.load(f)
    except FileNotFoundError:
        print(f"Chain file {chain_file} not found!")
        return 0
    
    balance = 0
    
    # Sprawdź nagrody za mining
    for blk in chain:
        data = blk.get("data", "")
        if f"Reward to {address}" in data:
            try:
                # Format: "Reward to address: 50 BSC"
                parts = data.split(":")
                if len(parts) > 1:
                    reward_part = parts[-1].strip()
                    reward = float(reward_part.split()[0])
                    balance += reward
            except:
                pass
        
        # Sprawdź transakcje (format: TX {'from': 'addr1', 'to': 'addr2', 'amount': 10})
        if "TX {" in data:
            try:
                # Wyciągnij część transakcji
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

def list_wallet_addresses():
    """Wyświetla wszystkie adresy z portfela"""
    wallet = BitsCoinWallet()
    addresses = wallet.get_addresses()
    
    if not addresses:
        print("No addresses in wallet. Create new address first!")
        return
    
    print("\n=== Your BitsCoin Addresses ===")
    for i, addr in enumerate(addresses, 1):
        print(f"{i}. {addr}")
    print()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Bez argumentów - pokaż wszystkie adresy z portfela
        list_wallet_addresses()
        sys.exit(0)
    
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--help":
            print("Usage:")
            print("  balance.py                    - List all wallet addresses")
            print("  balance.py <address>          - Check balance for address")
            print("  balance.py <chain.json> <address> - Check balance using specific chain file")
            sys.exit(0)
        else:
            # Jeden argument - sprawdź saldo dla adresu z domyślnym chain.json
            chain_file = "../core/chain.json"
            address = sys.argv[1]
    
    elif len(sys.argv) == 3:
        # Dwa argumenty - plik chain i adres
        chain_file, address = sys.argv[1], sys.argv[2]
    
    else:
        print("Usage: balance.py [chain.json] [address]")
        print("Run 'balance.py --help' for more info")
        sys.exit(1)
    
    bal = compute_balance(chain_file, address)
    print(f"Balance of {address}: {bal} BSC")
