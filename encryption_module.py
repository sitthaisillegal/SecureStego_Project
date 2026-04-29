from cryptography.fernet import Fernet

def generate_key():
    """Generates a secret key for AES encryption and saves it to a file."""
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    print("[+] New Secret Key Generated and Saved!")

def load_key():
    """Loads the secret key from the current directory."""
    return open("secret.key", "rb").read()

def encrypt_message(message):
    """Encrypts a string message."""
    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message):
    """Decrypts an encrypted message."""
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message

# --- TESTING OUR CODE ---
if __name__ == "__main__":
    print("--- Starting Security Layer Test ---")
    
    # 1. Generate a key (run this once to create the secret.key file)
    generate_key()
    
    # 2. The secret message we want to hide later
    original_message = "This is a top-secret message for my final year project!"
    print(f"Original: {original_message}")
    
    # 3. Encrypt it
    encrypted = encrypt_message(original_message)
    print(f"Encrypted (Scrambled): {encrypted}")
    
    # 4. Decrypt it back
    decrypted = decrypt_message(encrypted)
    print(f"Decrypted (Restored): {decrypted}")