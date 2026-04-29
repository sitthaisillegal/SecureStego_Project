import cv2
import numpy as np
from encryption_module import encrypt_message, generate_key

def data_to_binary(data):
    """Converts our encrypted bytes into a string of 1s and 0s."""
    if type(data) == str:
        return ''.join(format(ord(i), '08b') for i in data)
    elif type(data) == bytes:
        return ''.join(format(i, '08b') for i in data)

def embed_data(image_path, secret_message, output_path="stego_image.png"):
    # 1. Read the image
    img = cv2.imread(image_path)
    if img is None:
        print("[-] Error: Image not found.")
        return
    
    # 2. Convert message to binary and add a "STOP" signal at the end
    # The '1111111111111110' tells the extractor when to stop reading
    binary_data = data_to_binary(secret_message) + '1111111111111110'
    data_index = 0
    data_len = len(binary_data)
    
    # 3. Modify the pixels!
    for row in img:
        for pixel in row:
            for color_channel in range(3): # B, G, R
                if data_index < data_len:
                    # Replace the last bit of the pixel's color with our message bit
                    pixel[color_channel] = int(bin(pixel[color_channel])[2:-1] + binary_data[data_index], 2)
                    data_index += 1
                else:
                    break
    
    # 4. Save the new Stego Image (MUST be saved as .png to avoid compression loss)
    cv2.imwrite(output_path, img)
    print(f"[+] Success! Encrypted data hidden inside '{output_path}'")

if __name__ == "__main__":
    print("--- Starting Steganography Embedder ---")
    
    # Step A: Encrypt your secret text
    my_secret = "This is the hidden payload for my final year project!"
    print("Encrypting data...")
    encrypted_payload = encrypt_message(my_secret)
    
    # Step B: Hide the encrypted text in the image
    print("Hiding data in image...")
    embed_data("cover.jpg", encrypted_payload, "stego_image.png")