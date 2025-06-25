#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BitsCoin 2025 - Modern Web API
Flask REST API for BitsCoin blockchain
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
import sys
import os
import json
import time
import threading

# Dodaj ścieżkę do core
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from wallet import BitsCoinWallet
from bitscoin import Blockchain

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bitscoin-2025-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Globalne zmienne
blockchain = None
wallet = None
mining_active = False
mining_thread = None

def init_bitscoin():
    """Inicjalizacja BitsCoin"""
    global blockchain, wallet
    blockchain = Blockchain(difficulty=4, reward=50)
    wallet = BitsCoinWallet()
    
    # Załaduj istniejący blockchain jeśli istnieje
    try:
        with open('../core/chain.json', 'r') as f:
            chain_data = json.load(f)
        print(f"Loaded existing blockchain with {len(chain_data)} blocks")
    except:
        print("No existing blockchain found, using fresh chain")

@app.route('/api/status')
def api_status():
    """Status API i blockchain"""
    return jsonify({
        'status': 'online',
        'blockchain': {
            'blocks': len(blockchain.chain) if blockchain else 0,
            'difficulty': blockchain.difficulty if blockchain else 0,
            'reward': blockchain.reward if blockchain else 0
        },
        'wallet': {
            'addresses': len(wallet.get_addresses()) if wallet else 0
        },
        'mining': mining_active
    })

@app.route('/api/wallet/addresses')
def api_wallet_addresses():
    """Lista adresów portfela"""
    if not wallet:
        return jsonify({'error': 'Wallet not initialized'}), 500
    
    addresses = []
    for addr in wallet.get_addresses():
        balance = blockchain.get_balance(addr) if blockchain else 0
        addresses.append({
            'address': addr,
            'balance': balance,
            'label': wallet.keys[addr].get('label', ''),
            'created': wallet.keys[addr].get('created', 0)
        })
    
    return jsonify({'addresses': addresses})

@app.route('/api/wallet/create', methods=['POST'])
def api_create_address():
    """Stwórz nowy adres"""
    if not wallet:
        return jsonify({'error': 'Wallet not initialized'}), 500
    
    data = request.get_json()
    label = data.get('label', f'Address {len(wallet.get_addresses()) + 1}')
    
    try:
        new_address = wallet.create_new_address(label)
        socketio.emit('new_address', {
            'address': new_address,
            'label': label,
            'balance': 0
        })
        
        return jsonify({
            'success': True,
            'address': new_address,
            'label': label
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/balance/<address>')
def api_balance(address):
    """Sprawdź saldo adresu"""
    if not blockchain:
        return jsonify({'error': 'Blockchain not initialized'}), 500
    
    balance = blockchain.get_balance(address)
    return jsonify({
        'address': address,
        'balance': balance
    })

@app.route('/api/send', methods=['POST'])
def api_send_transaction():
    """Wyślij transakcję"""
    if not blockchain or not wallet:
        return jsonify({'error': 'System not initialized'}), 500
    
    data = request.get_json()
    from_addr = data.get('from')
    to_addr = data.get('to')
    amount = float(data.get('amount', 0))
    
    # Walidacja
    if from_addr not in wallet.get_addresses():
        return jsonify({'error': 'Address not in wallet'}), 400
    
    balance = blockchain.get_balance(from_addr)
    if balance < amount:
        return jsonify({'error': 'Insufficient funds'}), 400
    
    try:
        # Symulacja wysłania transakcji (dodamy do blockchain)
        tx_data = {
            "from": from_addr,
            "to": to_addr,
            "amount": amount,
            "timestamp": time.time()
        }
        
        # Podpis transakcji
        tx_message = f"{from_addr}->{to_addr}:{amount}"
        signature = wallet.sign_transaction(from_addr, tx_message)
        tx_data["signature"] = signature
        
        # Dodaj do ostatniego bloku
        if len(blockchain.chain) > 0:
            current_data = blockchain.chain[-1].data
            blockchain.chain[-1].data = f"{current_data} | TX {tx_data}"
        
        # Zapisz blockchain
        with open("../core/chain.json", "w") as f:
            json.dump([b.__dict__ for b in blockchain.chain], f, indent=2)
        
        # Wyślij update przez WebSocket
        socketio.emit('transaction', {
            'from': from_addr,
            'to': to_addr,
            'amount': amount,
            'timestamp': tx_data['timestamp']
        })
        
        return jsonify({
            'success': True,
            'transaction': tx_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain')
def api_blockchain():
    """Pobierz dane blockchain"""
    if not blockchain:
        return jsonify({'error': 'Blockchain not initialized'}), 500
    
    blocks = []
    for block in blockchain.chain:
        blocks.append({
            'index': block.index,
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'timestamp': block.timestamp,
            'data': block.data,
            'nonce': block.nonce
        })
    
    return jsonify({'blocks': blocks})

@app.route('/api/mining/start', methods=['POST'])
def api_start_mining():
    """Uruchom mining"""
    global mining_active, mining_thread
    
    if mining_active:
        return jsonify({'error': 'Mining already active'}), 400
    
    data = request.get_json()
    miner_address = data.get('address')
    
    if miner_address not in wallet.get_addresses():
        return jsonify({'error': 'Invalid miner address'}), 400
    
    def mine():
        global mining_active
        mining_active = True
        while mining_active:
            try:
                block, mining_time = blockchain.add_block(miner_address)
                
                # Wyślij update przez WebSocket
                socketio.emit('new_block', {
                    'index': block.index,
                    'hash': block.hash,
                    'reward': blockchain.reward,
                    'miner': miner_address,
                    'time': mining_time
                })
                
                # Zapisz blockchain
                with open("../core/chain.json", "w") as f:
                    json.dump([b.__dict__ for b in blockchain.chain], f, indent=2)
                
            except Exception as e:
                print(f"Mining error: {e}")
                break
    
    mining_thread = threading.Thread(target=mine, daemon=True)
    mining_thread.start()
    
    return jsonify({'success': True, 'mining': True})

@app.route('/api/mining/stop', methods=['POST'])
def api_stop_mining():
    """Zatrzymaj mining"""
    global mining_active
    mining_active = False
    return jsonify({'success': True, 'mining': False})

@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html')

if __name__ == '__main__':
    init_bitscoin()
    print("🚀 BitsCoin API Server starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔗 API: http://localhost:5000/api/status")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
