from web3 import Web3

def test_connection():
    # 1. This is a public gateway to the Sepolia Testnet
    sepolia_rpc_url = "https://ethereum-sepolia-rpc.publicnode.com"
    
    # 2. Initialize the Web3 connection
    print("Attempting to connect to Ethereum Sepolia Testnet...")
    w3 = Web3(Web3.HTTPProvider(sepolia_rpc_url))
    
    # 3. Check if the connection is successful
    if w3.is_connected():
        print("\n[+] SUCCESS! Python is officially connected to the Blockchain!")
        
        # Let's fetch the current block number just to prove we are reading live data
        current_block = w3.eth.block_number
        print(f"[+] The latest block on Sepolia is: {current_block}")
    else:
        print("\n[-] Connection Failed. Please check your internet connection.")

if __name__ == "__main__":
    test_connection()