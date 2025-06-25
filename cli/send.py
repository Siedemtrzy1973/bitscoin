#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/*
 * Projekt BitsCoin 2025 - Secure Transaction Sender
 * Autorzy: Grupa Siedemtrzy
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */
"""

import json
import sys
import time
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from wallet import BitsCoinWallet

def get_balance(chain_file, address):
    """Pobiera aktuelle saldo adresu"""
    try:
        with open(chain_file) as f:
            chain = json.load(f)
    except FileNotFoundError:
        return 0
    
    balance = 0
    for blk in chain:
        data = blk.get("data", "")
        
        # Nagrody za mining
        if f"Reward to {address}" in data:
            try:
                parts = data.split(":")
                if len(parts) > 1:
                    reward = float(parts[-1].strip().split()[0])
                    balance += reward
            except:
                pass
        
        # Transakcje
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

def send_transaction(chain_file, from_addr, to_addr, amount):
    """Wysyła bezpieczną transakcję z weryfikacją"""
    
    # 1. Sprawdź czy portfel zawiera adres nadawcy
    wallet = BitsCoinWallet()
    if from_addr not in wallet.get_addresses():
        print(f"❌ Error: Address {from_addr} not found in your wallet!")
        return False
    
    # 2. Sprawdź saldo
    balance = get_balance(chain_file, from_addr)
    if balance < amount:
        print(f"❌ Insufficient funds!")
        print(f"   Balance: {balance} BSC")
        print(f"   Required: {amount} BSC")
        return False
    
    # 3. Utwórz transakcję
    tx_data = {
        "from": from_addr,
        "to": to_addr,
        "amount": float(amount),
        "timestamp": time.time()
    }
    
    # 4. Podpisz transakcję
    tx_message = f"{from_addr}->{to_addr}:{amount}"
    signature = wallet.sign_transaction(from_addr, tx_message)
    tx_data["signature"] = signature
    
    # 5. Dodaj do blockchain
    try:
        with open(chain_file) as f:
            chain = json.load(f)
        
        # Dodaj transakcję do ostatniego bloku
        if len(chain) > 0:
            current_data = chain[-1].get("data", "")
            chain[-1]["data"] = f"{current_data} | TX {tx_data}"
        
        # Zapisz zaktualizowany blockchain
        with open(chain_file, "w") as f:
            json.dump(chain, f, indent=2)
        
        print("✅ Transaction sent successfully!")
        print(f"   From: {from_addr}")
        print(f"   To: {to_addr}")
        print(f"   Amount: {amount} BSC")
        print(f"   New balance: {balance - amount} BSC")
        return True
        
    except Exception as e:
        print(f"❌ Error sending transaction: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: send.py <chain.json> <from_address> <to_address> <amount>")
        print("\nExample:")
        print("  send.py ../core/chain.json TccHgF... Tovd4e... 10.5")
        sys.exit(1)
    
    chain_file, from_addr, to_addr, amount_str = sys.argv[1:]
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("❌ Amount must be positive!")
            sys.exit(1)
    except ValueError:
        print("❌ Invalid amount format!")
        sys.exit(1)
    
    send_transaction(chain_file, from_addr, to_addr, amount)
