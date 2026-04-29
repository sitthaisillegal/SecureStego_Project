import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def calculate_metrics(original_path, stego_path):
    print(f"[*] Loading images for Forensic Analysis...")
    
    # Load both images
    original = cv2.imread(original_path)
    stego = cv2.imread(stego_path)

    if original is None or stego is None:
        print("[-] ERROR: Could not find one or both images.")
        return

    # Resize original to match the 64x64 stego image so we can compare them
    original_resized = cv2.resize(original, (64, 64))

    print("\n--- FORENSIC RESULTS ---")
    
    # 1. Calculate PSNR (Peak Signal-to-Noise Ratio)
    # Higher is better. > 30dB means the human eye can't see the difference.
    psnr_value = cv2.PSNR(original_resized, stego)
    print(f"PSNR Score: {psnr_value:.2f} dB")

    # 2. Calculate SSIM (Structural Similarity Index)
    # 1.0 is a perfect match. 0.0 is completely different.
    # Note: SSIM usually wants grayscale images or specific channel handling
    # For a quick evaluation, we calculate it across all 3 color channels
    ssim_value, _ = ssim(original_resized, stego, channel_axis=2, full=True)
    print(f"SSIM Score: {ssim_value:.4f}")
    print("------------------------\n")
    
    print("[*] Add these numbers to your Evaluation Chapter!")

# Run the test
# Make sure these filenames match your actual files!
calculate_metrics("cover.jpg", "final_stego_output.png")