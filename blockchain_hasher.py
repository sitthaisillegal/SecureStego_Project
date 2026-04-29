import hashlib

def generate_file_hash(file_path):
    """Generates a SHA-256 hash of a file to act as its digital fingerprint."""
    sha256_hash = hashlib.sha256()
    
    try:
        # Open the file in binary mode ('rb') to read the raw bytes
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large images efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    except FileNotFoundError:
        print(f"[-] Error: Could not find the file '{file_path}'.")
        return None

if __name__ == "__main__":
    print("--- Starting Blockchain Integrity Layer ---")
    
    # 1. Let's hash the original cover image first
    print("\nHashing original image...")
    cover_hash = generate_file_hash("cover.jpg")
    print(f"Cover Image Hash:\n{cover_hash}")
    
    # 2. Now let's hash the Stego Image (The one carrying your payload!)
    print("\nHashing Stego image...")
    stego_hash = generate_file_hash("stego_image.png")
    print(f"[+] STEGO IMAGE HASH (Digital Fingerprint):\n>> {stego_hash} <<")
    
    if cover_hash and stego_hash:
        if cover_hash == stego_hash:
            print("\n[-] The hashes match. (This shouldn't happen if data was hidden!)")
        else:
            print("\n[+] Success! The hashes are different. The hidden data changed the fingerprint.")
            print("[+] The Stego Image Hash is ready to be sent to the Ethereum Smart Contract!")