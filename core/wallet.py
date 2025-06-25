#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/*
 * Projekt BitsCoin 2025 - System Portfeli
 * Autorzy: Grupa Siedemtrzy
 * Fork SHA-256 – niezależna sieć BitsCoin
 * © 2025 Grupa Siedemtrzy. Wszelkie prawa zastrzeżone.
 */
"""

import hashlib
import secrets
import json
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base58

class BitsCoinWallet:
    def __init__(self, wallet_dir="~/.bitscoin"):
        self.wallet_dir = os.path.expanduser(wallet_dir)
        os.makedirs(self.wallet_dir, exist_ok=True)
        self.wallet_file = os.path.join(self.wallet_dir, "bitscoin.dat")
        self.keys = {}
        self.load_wallet()
    
    def generate_keypair(self):
        """Generuje parę kluczy RSA"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    def create_address(self, public_key):
        """Tworzy adres BitsCoin z klucza publicznego"""
        # Serializuj klucz publiczny
        pub_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # SHA-256 hash
        sha256_hash = hashlib.sha256(pub_bytes).digest()
        
        # RIPEMD-160 hash (symulacja - używamy SHA-256 ponownie)
        ripemd_hash = hashlib.sha256(sha256_hash).digest()[:20]
        
        # Dodaj prefix dla BitsCoin (0x42 = 'B')
        versioned = b'\x42' + ripemd_hash
        
        # Podwójny SHA-256 dla checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
        
        # Pełny adres
        full_address = versioned + checksum
        
        # Kodowanie Base58
        return base58.b58encode(full_address).decode('utf-8')
    
    def create_new_address(self, label=""):
        """Tworzy nowy adres w portfelu"""
        private_key, public_key = self.generate_keypair()
        address = self.create_address(public_key)
        
        # Zapisz klucze
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        self.keys[address] = {
            "private_key": private_pem,
            "public_key": public_pem,
            "label": label,
            "created": int(time.time())
        }
        
        self.save_wallet()
        return address
    
    def sign_transaction(self, address, message):
        """Podpisuje transakcję kluczem prywatnym"""
        if address not in self.keys:
            raise ValueError(f"Address {address} not found in wallet")
        
        # Załaduj klucz prywatny
        private_key = serialization.load_pem_private_key(
            self.keys[address]["private_key"].encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # Podpisz wiadomość
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base58.b58encode(signature).decode('utf-8')
    
    def verify_signature(self, address, message, signature):
        """Weryfikuje podpis transakcji"""
        try:
            if address not in self.keys:
                return False
            
            # Załaduj klucz publiczny
            public_key = serialization.load_pem_public_key(
                self.keys[address]["public_key"].encode('utf-8'),
                backend=default_backend()
            )
            
            # Zweryfikuj podpis
            sig_bytes = base58.b58decode(signature)
            public_key.verify(
                sig_bytes,
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False
    
    def get_addresses(self):
        """Zwraca listę adresów w portfelu"""
        return list(self.keys.keys())
    
    def save_wallet(self):
        """Zapisuje portfel do pliku bitscoin.dat"""
        wallet_data = {
            "version": "BitsCoin 2025 v1.0",
            "addresses": self.keys
        }
        
        with open(self.wallet_file, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        
        print(f"Wallet saved to {self.wallet_file}")
    
    def load_wallet(self):
        """Ładuje portfel z pliku"""
        if os.path.exists(self.wallet_file):
            try:
                with open(self.wallet_file, 'r') as f:
                    wallet_data = json.load(f)
                self.keys = wallet_data.get("addresses", {})
                print(f"Wallet loaded from {self.wallet_file}")
            except:
                print("Error loading wallet, creating new one")
                self.keys = {}
        else:
            print("No wallet found, creating new one")
            self.keys = {}

# Test functionality
if __name__ == "__main__":
    import time
    
    print("=== BitsCoin Wallet System Test ===")
    
    # Stwórz portfel
    wallet = BitsCoinWallet()
    
    # Stwórz pierwszy adres
    addr1 = wallet.create_new_address("Main Address")
    print(f"Created address: {addr1}")
    
    # Stwórz drugi adres  
    addr2 = wallet.create_new_address("Secondary Address")
    print(f"Created address: {addr2}")
    
    # Wyświetl wszystkie adresy
    print(f"All addresses: {wallet.get_addresses()}")
    
    # Test podpisu
    message = "Test transaction: send 10 BSC"
    signature = wallet.sign_transaction(addr1, message)
    print(f"Signature: {signature[:50]}...")
    
    # Test weryfikacji
    valid = wallet.verify_signature(addr1, message, signature)
    print(f"Signature valid: {valid}")
