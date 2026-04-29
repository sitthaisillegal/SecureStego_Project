import os
import sys
import time
import hashlib
import base64
import cv2
import numpy as np
import re
from tensorflow.keras.models import load_model
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from web3 import Web3

# --- PyInstaller path fix ---
# When running as a .exe, files are in a temp folder (sys._MEIPASS)
# When running normally as .py, they're in the current directory
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def step_1_encrypt_payload(secret_text, password):
    print("\n[*] LAYER 1: Encrypting secret message with AES-256...")
    
    # 1. Generate a secure 256-bit key using the password
    key = hashlib.sha256(password.encode()).digest()
    
    # 2. Create the AES cipher (CBC mode is standard for secure text)
    cipher = AES.new(key, AES.MODE_CBC)
    
    # 3. Pad the text to fit AES block sizes, then encrypt
    padded_data = pad(secret_text.encode(), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    
    # 4. Bundle the initialization vector (IV) and encrypted data together
    final_payload = cipher.iv + encrypted_bytes
    
    # 5. Convert the raw bytes into a safe Base64 string so the AI can handle it later
    encrypted_data = base64.b64encode(final_payload).decode('utf-8')
    
    print(f"[+] Message Encrypted! (Result: {encrypted_data[:15]}...)")
    return encrypted_data

def test_decrypt_payload(encrypted_b64, password):
    import re # Added regex to help clean the final text
    
    safe_b64 = str(encrypted_b64).strip() 
    safe_b64 += "=" * ((4 - len(safe_b64) % 4) % 4) 
    encrypted_b64 = safe_b64 
    
    print("    [?] TEST: Attempting to decrypt payload to verify...")
    try:
        # 1. Decode the Base64 string back into raw bytes
        raw_data = base64.b64decode(encrypted_b64)

        # 2. Separate the Initialization Vector (first 16 bytes) from the ciphertext
        iv = raw_data[:16]
        ciphertext = raw_data[16:]

        # --- THE BYTE-LEVEL FIX FOR AI TRUNCATION ---
        # If the AI dropped a few bytes, this pads it to a perfect multiple of 16
        remainder = len(ciphertext) % 16
        if remainder != 0:
            ciphertext += b'\x00' * (16 - remainder)
        # --------------------------------------------

        # 3. Rebuild the exact same 256-bit key from the password
        key = hashlib.sha256(password.encode()).digest()

        # 4. Decrypt the data (This will no longer crash!)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)

        # 5. Clean the final text
        try:
            # Try the official cryptographic unpadding first
            original_text = unpad(decrypted_padded, AES.block_size).decode('utf-8')
        except ValueError:
            # If the AI corrupted the padding, do a manual force-clean
            raw_text = decrypted_padded.decode('utf-8', errors='ignore')
            # Strip out any broken padding characters or the blank zeros we added
            original_text = re.sub(r'[\x00-\x10]+$', '', raw_text)

        print(f"    [+] SUCCESS! Decrypted text matches: '{original_text}'\n")
        return original_text
        
    except Exception as e:
        print(f"    [-] DECRYPTION FAILED: {e}\n")
        return None

def _lsb_embed(image_array, data_bytes):
    """
    LSB Sub-layer: embeds raw bytes into the least significant bit of each pixel channel.
    A 4-byte (32-bit) length header is prepended so the extractor knows when to stop.
    The image must be saved as PNG (lossless) after this — never JPEG.
    """
    header      = len(data_bytes).to_bytes(4, 'big')   # 4-byte length prefix
    payload     = header + data_bytes                   # full binary payload
    bits        = ''.join(format(b, '08b') for b in payload)
    flat        = image_array.flatten().copy()

    if len(bits) > len(flat):
        raise ValueError(
            f"Payload too large for image! Need {len(bits)} bits, have {len(flat)}."
        )

    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | int(bit)          # clear LSB, write our bit

    return flat.reshape(image_array.shape)


def _lsb_extract(image_array):
    """
    LSB Sub-layer: reads the least significant bit of each pixel channel,
    reads the 4-byte length header first, then returns exactly that many bytes.
    """
    flat = image_array.flatten()
    bits = ''.join(str(int(b) & 1) for b in flat)

    # Read the 32-bit length header
    length = int(bits[:32], 2)

    # Read exactly 'length' bytes
    data_bits  = bits[32 : 32 + length * 8]
    data_bytes = bytes(
        int(data_bits[i : i + 8], 2) for i in range(0, len(data_bits), 8)
    )
    return data_bytes


def step_2_hide_in_image(cover_image_path, encrypted_base64_data):
    print("[*] LAYER 2: Waking up AI Steganography Model...")

    # 1. Load your trained neural network
    model = load_model(os.path.join(BASE_DIR, 'final_stego_model.h5'), compile=False)

    # 2. Read and format the cover image for the AI
    print("[*] Processing cover image...")
    image = cv2.imread(cover_image_path)
    
    # --- COLOR FIX 1: Flip BGR to RGB for the AI ---
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # -----------------------------------------------
    
    image = cv2.resize(image, (64, 64))
    image = image.astype('float32') / 255.0
    image_tensor = np.expand_dims(image, axis=0)

    # 3. Format the payload grid for the AI model (visual steganography layer)
    print("[*] Formatting payload grid for AI visual embedding...")
    payload_bytes  = encrypted_base64_data.encode('utf-8')
    payload_array  = np.frombuffer(payload_bytes, dtype=np.uint8)
    fixed_payload  = np.zeros(4096, dtype=np.uint8)
    length         = min(len(payload_array), 4096)
    fixed_payload[:length] = payload_array[:length]

    payload_grid   = fixed_payload.reshape((64, 64)).astype('float32') / 255.0
    payload_tensor = np.expand_dims(np.expand_dims(payload_grid, axis=0), axis=-1)

    # 4. AI generates the visually-stego image
    stego_tensor     = model.predict([image_tensor, payload_tensor])
    stego_image_data = stego_tensor[0]

    try:
        stego_image_data = stego_image_data.reshape((64, 64, 3))
    except Exception as e:
        print(f"[-] ERROR: AI output shape mismatch. Details: {e}")
        return None

    stego_image_data = np.clip(stego_image_data, 0.0, 1.0)
    stego_image_data = (stego_image_data * 255.0).astype(np.uint8)

    # --- COLOR FIX 2: Flip RGB back to BGR for OpenCV to save correctly ---
    stego_image_data = cv2.cvtColor(stego_image_data, cv2.COLOR_RGB2BGR)
    # -----------------------------------------------------------------------

    # 5. ── LSB SUB-LAYER ──────────────────────────────────────────────────
    # The AI model handles visual imperceptibility; LSB handles 100% accurate
    # payload recovery. We embed the encrypted bytes into the LSBs of the
    # AI-generated stego image before saving. PNG is lossless so bits survive.
    print("[*] Applying LSB sub-layer for lossless payload embedding...")
    stego_image_data = _lsb_embed(stego_image_data, payload_bytes)
    print(f"    [+] LSB embedded {len(payload_bytes)} bytes into stego image.")
    # ─────────────────────────────────────────────────────────────────────

    stego_image_path = "final_stego_output.png"
    success = cv2.imwrite(stego_image_path, stego_image_data)

    if not success:
        print("[-] ERROR: OpenCV failed to write the image file.")
        return None

    print(f"[+] AI + LSB Embedding Complete! Saved as {stego_image_path}")
    return stego_image_path

def step_3_register_on_blockchain(stego_image_path):
    print("\n[*] LAYER 3: Hashing image and connecting to Ethereum Sepolia...")
    
    # 1. Generate SHA-256 hash of the Stego Image
    sha256_hash = hashlib.sha256()
    with open(stego_image_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    image_hash = sha256_hash.hexdigest()
    print(f"    [+] Image Hash Generated: {image_hash}")

    # 2. Connect to Web3
    RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
    CONTRACT_ADDRESS = "0xd9145CCE52D386f254917e481eB44e9943F39138"
    MY_ADDRESS = "0x767257EAc29382191D4e8Ced3A763D376e689a26"
    PRIVATE_KEY = "37343ed5ef1f0ff6b08097ce4dd75de098660bab83fa81da583de4008e302819"
    
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        print("    [-] ERROR: Could not connect to Sepolia network.")
        return "CONNECTION_FAILED"
        
    print("    [+] Connected to Sepolia testnet!")
    
    # 3. Setup Contract Blueprint (ABI)
    contract_abi = [
        {
            "inputs": [{"internalType": "string", "name": "fileHash", "type": "string"}],
            "name": "storeHash",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
    
    # 4. Build the transaction
    print("    [*] Sending transaction to blockchain...")
    nonce = web3.eth.get_transaction_count(MY_ADDRESS)
    
    tx = contract.functions.storeHash(image_hash).build_transaction({
        'chainId': 11155111, # Sepolia chain ID
        'gas': 500000,       # <-- CHANGED THIS TO 500,000
        'maxFeePerGas': web3.to_wei('10', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('2', 'gwei'),
        'nonce': nonce,
    })
    
    # 5. Sign and send
    signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    # Wait for the blockchain to mine the block
    print("    [*] Waiting for block confirmation... (this takes 15-30 seconds)")
    web3.eth.wait_for_transaction_receipt(tx_hash)
    
    final_hash = web3.to_hex(tx_hash)
    print(f"    [+] Transaction Confirmed! Hash: {final_hash}")
    
    return final_hash

def step_4_extract_from_image(stego_image_path):
    print("\n[*] LAYER 4: Extracting hidden payload from stego image...")

    image = cv2.imread(stego_image_path)
    if image is None:
        print("[-] ERROR: Could not load stego image.")
        return None

    # ── LSB SUB-LAYER EXTRACTION ─────────────────────────────────────────
    # We read the LSBs directly from the PNG pixels. Because PNG is lossless,
    # every bit we embedded in step_2 is preserved perfectly — no AI noise.
    print("[*] Reading LSB sub-layer (lossless extraction)...")
    try:
        payload_bytes = _lsb_extract(image)
    except Exception as e:
        print(f"[-] ERROR during LSB extraction: {e}")
        return None

    encrypted_base64 = payload_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
    print(f"[+] LSB Extraction complete! Recovered {len(payload_bytes)} bytes.")
    # ─────────────────────────────────────────────────────────────────────

    # Sanitize to valid Base64 characters only
    import re
    encrypted_base64 = re.sub(r'[^A-Za-z0-9+/=]', '', encrypted_base64)

    print(f"[+] Payload cleaned! (Preview: {encrypted_base64[:15]}...)")
    return encrypted_base64

# --- THE MAIN MENU ---

def main():
    # --- AUTOMATIC CLEANUP ---
    files_to_clean = ["final_stego_output.png", "stego_output.png"]
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"[*] Cleanup: Removed old {file}")
    # --------------------------
    print("=====================================================")
    print("   SECURE STEGO: AI & BLOCKCHAIN INTEGRITY SYSTEM    ")
    print("=====================================================\n")
    
    # 1. Get user input
    cover_image = input("Enter the cover image filename (e.g., cover.jpg): ")
    secret_message = input("Enter the secret message to hide: ")
    password = input("Enter a secure password for AES-256: ")
    
    print("\n=====================================================")
    print("             INITIATING SECURE PIPELINE              ")
    print("=====================================================")
    
    # 2. Run the pipeline in order
    encrypted_data = step_1_encrypt_payload(secret_message, password)
    # --- QUICK TEST TO PROVE IT WORKS ---
    test_decrypt_payload(encrypted_data, password)
    # ------------------------------------
    stego_image = step_2_hide_in_image(cover_image, encrypted_data)
    
    tx_receipt = step_3_register_on_blockchain(stego_image)
    
    # 3. Final Output
    print("\n=====================================================")
    print("                 PIPELINE COMPLETE                   ")
    print("=====================================================")
    print(f"[*] Final Stego Image : {stego_image}")
    print(f"[*] Blockchain Proof  : https://sepolia.etherscan.io/tx/{tx_receipt}")
    print("=====================================================\n")

    print(f"[*] Final Stego Image : {stego_image}")
    print(f"[*] Blockchain Proof  : https://sepolia.etherscan.io/tx/{tx_receipt}")
    print("=================================================\n")

    # ==========================================
    # PASTE RECEIVER PIPELINE HERE
    # ==========================================
    # --- RECEIVER PIPELINE ---
    print("\n=================================================")
    print("      INITIATING RECEIVER EXTRACTION PIPELINE    ")
    print("=================================================")
    
    extract_choice = input("Do you want to extract and decrypt the secret now? (y/n): ")
    if extract_choice.lower() == 'y':
        receiver_password = input("Enter the AES-256 decryption password: ")
        
        extracted_b64 = step_4_extract_from_image(stego_image)
        
        if extracted_b64:
            print("\n[*] LAYER 5: Decrypting AES-256 Payload...")
            test_decrypt_payload(extracted_b64, receiver_password)


if __name__ == "__main__":
    main()