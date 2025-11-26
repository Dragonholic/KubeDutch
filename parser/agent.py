import time
import re
import os
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

# 환경 변수 로드 (.env)
load_dotenv()

# 설정
INFURA_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
LOG_FILE_PATH = "/logs/logs/latest.log"  # K8s 마운트 경로
COST_PER_SECOND = 1000000000000  # 예: 초당 비용 (wei)

# ABI (스마트 컨트랙트 인터페이스)
CONTRACT_ABI = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"string","name":"username","type":"string"},{"indexed":false,"internalType":"uint256","name":"duration","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"cost","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"UsageLogged","type":"event"},{"inputs":[{"internalType":"string","name":"_username","type":"string"},{"internalType":"uint256","name":"_duration","type":"uint256"},{"internalType":"uint256","name":"_cost","type":"uint256"}],"name":"logUsage","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

def connect_web3():
    if not INFURA_URL:
        print("❌ Error: RPC_URL is missing in env")
        return None
        
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    try:
        if w3.is_connected():
            print(f"✅ Connected to Blockchain: Chain ID {w3.eth.chain_id}")
            return w3
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    return None

def send_transaction(w3, contract, username, duration):
    if not PRIVATE_KEY:
        print("❌ Error: PRIVATE_KEY is missing")
        return

    cost = duration * COST_PER_SECOND
    account = w3.eth.account.from_key(PRIVATE_KEY)
    
    print(f"🚀 Sending Tx for {username}: {duration}s / {cost} wei")
    
    try:
        tx = contract.functions.logUsage(username, duration, cost).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"⏳ Waiting for receipt... Tx Hash: {w3.to_hex(tx_hash)}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print(f"✅ Transaction Confirmed! Block: {receipt.blockNumber}")
        else:
            print("❌ Transaction Failed")
            
    except Exception as e:
        print(f"⚠️ Transaction Error: {e}")

def tail_log_file(path):
    while not os.path.exists(path):
        print(f"Waiting for log file at {path}...")
        time.sleep(5)
    
    print(f"Found log file! Tailing...")
    with open(path, "r", encoding="utf-8", errors='ignore') as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

def main():
    w3 = connect_web3()
    if not w3:
        return

    if not CONTRACT_ADDRESS:
        print("❌ Error: CONTRACT_ADDRESS is missing")
        return

    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=json.loads(CONTRACT_ABI))
    active_sessions = {}
    
    join_pattern = re.compile(r": (\w+) joined the game")
    left_pattern = re.compile(r": (\w+) left the game")

    print("🕵️ Starting Log Parser Agent...")

    for line in tail_log_file(LOG_FILE_PATH):
        join_match = join_pattern.search(line)
        if join_match:
            username = join_match.group(1)
            active_sessions[username] = time.time()
            print(f"🟢 User Joined: {username}")
            
        left_match = left_pattern.search(line)
        if left_match:
            username = left_match.group(1)
            if username in active_sessions:
                start_time = active_sessions.pop(username)
                duration = int(time.time() - start_time)
                print(f"🔴 User Left: {username} (Duration: {duration}s)")
                
                if duration > 0:
                    send_transaction(w3, contract, username, duration)

if __name__ == "__main__":
    main()

