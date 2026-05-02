# 🔐 SecureStegoVault
### AI-Driven Steganography for Verifiable Digital Asset Integrity

A steganography system that combines **AES-256 encryption**, **AI-based visual embedding**, and **Ethereum blockchain verification** to securely hide and verify secret messages inside images.

---

## ⚙️ How It Works
1. **Layer 1 - AES-256 Encryption:** Your secret message is encrypted with a password
2. **Layer 2 - AI Steganography:** The encrypted data is invisibly hidden inside a cover image using a trained neural network + LSB embedding
3. **Layer 3 - Blockchain:** The stego image is hashed and registered on the Ethereum Sepolia testnet as tamper-proof proof of ownership

---

## 💻 Installation - Choose One Option

### ✅ Option 1: Direct EXE (Recommended - No Python needed)
> Works on most Windows 10/11 machines

1. Go to [**Releases**](../../releases)
2. Download `SecureStegoVault_v1.1.zip`
3. Extract the zip
4. Double click `SecureStegoVault.exe`

> ⚠️ If Windows shows "Windows protected your PC":
> Click **More Info** → **Run Anyway**

> ⚠️ If the app doesn't open at all, try Option 2 below

---

### 🐍 Option 2: Python Script (Fallback - works on ALL machines)
> Use this if the EXE doesn't work on your machine

**Step 1:** Install **Python 3.10 only** from https://www.python.org/downloads/release/python-31011/

> ⚠️ **You must install Python 3.10 specifically - do NOT install Python 3.11, 3.12, 3.13 or 3.14.**
> TensorFlow (the AI library this app uses) does not support newer Python versions and the app will fail to launch.

> ⚠️ Make sure to tick **"Add Python to PATH"** during install, then restart your PC!

**Step 2:** Download the source code zip from [**Releases**](../../releases) and extract it

**Step 3:** Double click `install_and_run.bat`
> ⚠️ **Do NOT run the bat file as Administrator.** Running as Admin will install packages to a different location and the app will fail to open. Just double click it normally.
> First run takes 5-10 minutes to install packages. Every run after that is instant.

> ⏳ **The app may take up to 5 seconds to open after the install completes - this is normal. Don't panic or close the window!**

---

## 📱 How to Use

### Sending a Secret Message (Sender)
1. Open the app → **Sender Vault (Hide)** tab
2. Select a cover image (any JPG/PNG)
3. Type your secret message
4. Enter a password
5. Click **Execute Encryption & Blockchain Registry**
6. Once complete, the encrypted stego image `final_stego_output.png` will be saved in the **same folder where you extracted the app** - go there to find it and send it to the recipient
7. Send `final_stego_output.png` to the recipient **as a FILE** (not photo)
7. Share the password separately (in person, phone call, etc.)

> ⚠️ **Important:** When sending via WhatsApp, use the **paperclip → Document** option NOT the gallery/camera option. Sending as a photo compresses the image and destroys the hidden data.

### Receiving a Secret Message (Receiver)
1. Download the `.png` file sent to you
2. Open the app → **Receiver Extraction (Reveal)** tab
3. Select the downloaded `.png`
4. Enter the password the sender gave you
5. Click **Verify Integrity & Extract Secret**

---

## 📋 Requirements

| Option | Requirements |
|--------|-------------|
| EXE | Windows 10/11 64-bit, Internet connection |
| BAT | Windows 10/11, Python 3.10, Internet connection |

---

## 🛠️ Built With
- Python 3.10
- TensorFlow / Keras (AI Model)
- OpenCV (Image Processing)
- Flet (GUI Framework)
- Web3.py (Blockchain)
- PyCryptodome (AES-256)
- Ethereum Sepolia Testnet

---

## 📁 Project Structure
```
SecureStego_Project/
├── gui_app.py              # Main GUI application
├── master_app.py           # Core pipeline (encrypt, hide, blockchain, extract)
├── encryption_module.py    # AES-256 encryption
├── blockchain_hasher.py    # SHA-256 image hashing
├── evaluator.py            # PSNR/SSIM evaluation metrics
├── final_stego_model.h5    # Trained AI steganography model (DIV2K dataset)
├── contract_abi.json       # Ethereum smart contract ABI
├── install_and_run.bat     # Auto installer for Python fallback
└── ImageRegistry.sol       # Solidity smart contract source
```

---

## ⚠️ Known Limitations
- Stego image must be kept as PNG - JPEG compression destroys hidden data
- File must be sent as a document/file, not as a photo via messaging apps
- Blockchain registration requires an internet connection
- EXE may not work on some older machines with Intel integrated graphics - use Option 2 in that case
- Requires Windows 10/11 64-bit

---
