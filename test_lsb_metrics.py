import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

# Import YOUR exact LSB function from your master app
from master_app import _lsb_embed

print("[*] Loading pristine cover image...")
# Load your high-resolution train image
original_path = r"C:\Users\Sittha\Pictures\train_cover.jpg"
original_path = "cover.jpg"

if original is None:
    print("[-] ERROR: Could not find the train image at that path.")
    exit()

# Create a dummy encrypted payload (similar to what AES would output)
encrypted_payload = b"This is a highly secure test payload for the Plymouth grading panel."

print("[*] Running isolated LSB mathematical embedding...")
# Run the embedding directly on the pristine image (Bypassing AI)
stego_image = _lsb_embed(original.copy(), encrypted_payload)

print("[*] Calculating Mathematical and Structural Differences...")
# Calculate TRUE PSNR (Notice we are NOT resizing to 64x64!)
psnr_value = cv2.PSNR(original, stego_image)

# Calculate TRUE SSIM
ssim_value, _ = ssim(original, stego_image, channel_axis=2, full=True)

print("\n=== LSB LAYER ISOLATION METRICS ===")
print(f"[*] Payload Size : {len(encrypted_payload)} bytes")
print(f"[+] True PSNR    : {psnr_value:.2f} dB")
print(f"[+] True SSIM    : {ssim_value:.4f}")
print("===================================")