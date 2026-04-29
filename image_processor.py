import cv2
import numpy as np

def load_image(image_path):
    """Loads an image and converts it into a numerical array."""
    # Read the image
    img = cv2.imread(image_path)
    
    if img is None:
        print("[-] Error: Could not find or load the image.")
        return None
    
    print(f"[+] Image Loaded Successfully! Size: {img.shape}")
    return img

def show_image_data(img):
    """Shows the 'raw data' that the AI will see."""
    # The AI sees an image as a 3D matrix of numbers (Blue, Green, Red)
    print("Top-left pixel (BGR values):", img[0, 0])
    
# --- TESTING OUR IMAGE HANDLER ---
if __name__ == "__main__":
    # Note: You need to put a sample image (like 'cover.jpg') in your project folder!
    sample_path = "cover.jpg" 
    image_array = load_image(sample_path)
    
    if image_array is not None:
        show_image_data(image_array)