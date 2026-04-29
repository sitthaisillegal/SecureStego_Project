import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def calculate_fyp_metrics(cover_path, stego_path):
    print("[*] Loading images for academic evaluation...")
    cover = cv2.imread(cover_path)
    stego = cv2.imread(stego_path)

    if cover is None or stego is None:
        print("[-] ERROR: Could not load one or both images. Check file paths!")
        return

    # Ensure images are the exact same dimensions for a fair mathematical comparison
    if cover.shape != stego.shape:
        print("[*] Resizing images to match dimensions...")
        stego = cv2.resize(stego, (cover.shape[1], cover.shape[0]))

    print("[*] Calculating Peak Signal-to-Noise Ratio (PSNR)...")
    # PSNR measures absolute pixel distortion. Higher is better.
    psnr_value = cv2.PSNR(cover, stego)

    print("[*] Calculating Structural Similarity Index (SSIM)...")
    # SSIM measures how human eyes perceive structural changes. 1.0 is a perfect match.
    try:
        ssim_value, _ = ssim(cover, stego, full=True, channel_axis=-1)
    except TypeError:
        # Fallback for older versions of scikit-image
        ssim_value, _ = ssim(cover, stego, full=True, multichannel=True)

    print("\n=================================================")
    print("      FYP ACADEMIC EVALUATION METRICS            ")
    print("=================================================")
    print(f"[+] Cover Image : {cover_path}")
    print(f"[+] Stego Image : {stego_path}")
    print("-------------------------------------------------")
    print(f"[+] PSNR Score  : {psnr_value:.2f} dB")
    print(f"[+] SSIM Score  : {ssim_value:.4f}")
    print("=================================================\n")

# --- Run the Evaluation ---
# Replace 'cover.jpg' with whatever your original image is named
calculate_fyp_metrics("cover.jpg", "final_stego_output.png")