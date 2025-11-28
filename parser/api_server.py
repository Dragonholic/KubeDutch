from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="KubeDutch Ledger API")

INFURA_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
COST_PER_SECOND = 1000000000000

w3 = None
contract = None

CONTRACT_ABI = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"string","name":"username","type":"string"},{"indexed":false,"internalType":"uint256","name":"duration","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"cost","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"timestamp","type":"uint256"}],"name":"UsageLogged","type":"event"},{"inputs":[{"internalType":"string","name":"_username","type":"string"},{"internalType":"uint256","name":"_duration","type":"uint256"},{"internalType":"uint256","name":"_cost","type":"uint256"}],"name":"logUsage","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

class UsageData(BaseModel):
    username: str
    duration: int

@app.on_event("startup")
async def startup_event():
    global w3, contract
    if not INFURA_URL:
        print("❌ Error: RPC_URL is missing")
        return
        
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    try:
        if w3.is_connected():
            print(f"✅ Blockchain Connected: Chain ID {w3.eth.chain_id}")
            contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=json.loads(CONTRACT_ABI))
        else:
            print("❌ Blockchain Connection Failed")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

@app.post("/log")
async def log_usage(data: UsageData):
    if data.duration <= 0:
        return {"status": "ignored"}
    
    if not contract:
        raise HTTPException(status_code=503, detail="Blockchain not connected")

    print(f"📩 Received Log: User {data.username}, Duration {data.duration}s")
    
    try:
        cost = data.duration * COST_PER_SECOND
        account = w3.eth.account.from_key(PRIVATE_KEY)
        
        tx = contract.functions.logUsage(data.username, data.duration, cost).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"🚀 Tx Sent: {w3.to_hex(tx_hash)}")
        return {"status": "success", "tx_hash": w3.to_hex(tx_hash)}
        
    except Exception as e:
        print(f"⚠️ Tx Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

