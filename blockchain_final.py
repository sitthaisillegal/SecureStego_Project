import json
from web3 import Web3

# --- CONFIGURATION (FILL THESE IN) ---
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
CONTRACT_ADDRESS = "0x3aD9D03B72661b9aaD22249d7C050196754dD116"
MY_ADDRESS = "0x767257EAc29382191D4e8Ced3A763D376e689a26" # From your screenshot
PRIVATE_KEY = "37343ed5ef1f0ff6b08097ce4dd75de098660bab83fa81da583de4008e302819" 

# 1. Load the ABI you saved earlier
with open("contract_abi.json", "r") as f:
    contract_abi = json.load(f)

# 2. Connect to Blockchain
w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def register_image_on_blockchain(image_hash):
    print(f"Sending hash {image_hash} to Sepolia...")
    
    # Build the transaction
    nonce = w3.eth.get_transaction_count(MY_ADDRESS)
    txn = contract.functions.registerHash(image_hash).build_transaction({
        'chainId': 11155111, # Sepolia ID
        'gas': 200000,
        'gasPrice': w3.to_wei('50', 'gwei'),
        'nonce': nonce,
    })

    # Sign and Send
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"[+] Transaction Sent! Hash: {w3.to_hex(tx_hash)}")
    print("Waiting for confirmation...")
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("[+] SUCCESS! Your image is now verifiable on the Ethereum Blockchain.")

if __name__ == "__main__":
    # Use the hash generated in the previous step
    sample_stego_hash = "1a7f3d126dd235d69912a9c7e81d1e0c99e9adf362b397b18c361cf9e5e4c1f3"
    register_image_on_blockchain(sample_stego_hash)