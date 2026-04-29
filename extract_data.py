import cv2
import numpy as np
from encryption_module import decrypt_message

def extract_data(image_path="stego_image.png"):
    # 1. Read the stego image
    img = cv2.imread(image_path)
    if img is None:
        print("[-] Error: Stego image not found.")
        return None
    
    binary_data = ""
    
    # 2. Extract the least significant bit (LSB) from each pixel
    for row in img:
        for pixel in row:
            for color_channel in range(3):
                # Get the binary value of the color and extract the last bit
                binary_data += bin(pixel[color_channel])[-1]
    
    # 3. Split the giant string of 1s and 0s into 8-bit bytes
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    
    extracted_bits = ""
    for byte in all_bytes:
        extracted_bits += byte
        # Check for our 16-bit stop signal ('1111111111111110')
        if extracted_bits[-16:] == '1111111111111110':
            break
            
    # 4. Remove the stop signal to get the clean encrypted payload
    clean_binary = extracted_bits[:-16]
    
    # Convert the binary string back to actual bytes
    byte_data = bytearray(int(clean_binary[i: i+8], 2) for i in range(0, len(clean_binary), 8))
    
    return bytes(byte_data)

if __name__ == "__main__":
    print("--- Starting Steganography Extractor ---")
    print("Extracting hidden data from image...")
    
    # Step A: Pull the 1s and 0s out of the image pixels
    extracted_encrypted_payload = extract_data("stego_image.png")
    
    if extracted_encrypted_payload:
        print(f"\n[+] Extracted Scrambled Payload: {extracted_encrypted_payload}")
        
        # Step B: Pass the scrambled payload to our decryption module
        print("\nDecrypting data...")
        try:
            decrypted_message = decrypt_message(extracted_encrypted_payload)
            print(f"\n[+] SUCCESS! The hidden message is:\n>> {decrypted_message} <<\n")
        except Exception as e:
            print(f"[-] Error during decryption: {e}")
            print("Make sure you are using the same secret.key that was used to encrypt it!")