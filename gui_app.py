import flet as ft
import traceback

# --- PYINSTALLER WINDOWED MODE FIX ---
# Gives TensorFlow a dummy console to write to since the real one is hidden
import sys
import io
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()
# -------------------------------------

# --- IMPORTING YOUR FULL BACKEND PIPELINE ---
from master_app import (
    step_1_encrypt_payload,
    step_2_hide_in_image,
    step_3_register_on_blockchain,
    step_4_extract_from_image,
    test_decrypt_payload
)

def main(page: ft.Page):
    try:
        # 1. Window Config
        page.title = "Secure Steganography Vault"
        page.theme_mode = "dark"
        page.padding = 20
        page.window_width = 1280
        page.window_height = 620
        page.window_min_width = 1280
        page.window_min_height = 620

        header = ft.Text("Secure Stego: AI & Blockchain", size=24, weight="bold")
        
        # ==========================================
        # SENDER TAB (HIDE DATA)
        # ==========================================
        tx_file_path_text = ft.TextField(label="Cover Image Path", read_only=True, expand=True)
        tx_file_picker = ft.FilePicker(on_result=lambda e: update_path(e, tx_file_path_text))
        page.overlay.append(tx_file_picker)
        tx_pick_file_btn = ft.FilledButton("Select Image", on_click=lambda _: tx_file_picker.pick_files()) 
        tx_file_row = ft.Row([tx_file_path_text, tx_pick_file_btn])

        secret_input = ft.TextField(label="Secret Message", multiline=True, min_lines=2)
        tx_password_input = ft.TextField(label="AES-256 Password", password=True, can_reveal_password=True)

        tx_log_terminal = ft.TextField(
            label="System Output Logs", multiline=True, read_only=True,
            min_lines=5, max_lines=5,
            text_style=ft.TextStyle(font_family="Consolas", color="#4ade80")
        )

        # --- ETHERSCAN BUTTON (hidden until pipeline completes) ---
        etherscan_url_store = {"url": None}   # simple dict to hold the URL across closures

        def open_etherscan(e):
            if etherscan_url_store["url"]:
                page.launch_url(etherscan_url_store["url"])

        etherscan_btn = ft.ElevatedButton(
            text="🔗  View Blockchain Proof on Etherscan",
            on_click=open_etherscan,
            disabled=True,   # enabled once a tx hash is ready
            style=ft.ButtonStyle(
                bgcolor={"": "#1a56db"},
                color={"": "#ffffff"},
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
        )
        # ----------------------------------------------------------

        def run_sender_pipeline(e):
            tx_run_btn.disabled = True
            etherscan_btn.disabled = True          # grey out while running
            etherscan_url_store["url"] = None
            tx_log_terminal.value = "[*] INITIATING SECURE SENDER PIPELINE...\n"
            page.update()

            if not tx_file_path_text.value or not secret_input.value or not tx_password_input.value:
                tx_log_terminal.value += "[-] ERROR: Please fill in all fields!\n"
                tx_run_btn.disabled = False
                page.update()
                return

            try:
                tx_log_terminal.value += "\n[*] LAYER 1: Encrypting Payload with AES-256...\n"
                page.update()
                encrypted_data = step_1_encrypt_payload(secret_input.value, tx_password_input.value)

                tx_log_terminal.value += "[*] LAYER 2: Waking up AI Model & Hiding Data...\n"
                page.update()
                stego_image = step_2_hide_in_image(tx_file_path_text.value, encrypted_data)
                
                tx_log_terminal.value += "[*] LAYER 3: Registering on Ethereum Sepolia Testnet...\n"
                tx_log_terminal.value += "[*] Awaiting blockchain confirmation (10-15 seconds)...\n"
                page.update()
                tx_receipt = step_3_register_on_blockchain(stego_image)

                # Build the full Etherscan URL and store it
                full_url = f"https://sepolia.etherscan.io/tx/{tx_receipt}"
                etherscan_url_store["url"] = full_url

                tx_log_terminal.value += "\n[+] ==================================================\n"
                tx_log_terminal.value += "[+] PIPELINE COMPLETE!\n"
                tx_log_terminal.value += f"[+] Final Output Image : {stego_image}\n"
                tx_log_terminal.value += f"[+] Blockchain Proof   : {full_url}\n"
                tx_log_terminal.value += "[+] ==================================================\n"

                # Enable the Etherscan button now that we have a URL
                etherscan_btn.disabled = False

            except Exception as err:
                tx_log_terminal.value += f"\n[-] BACKEND ERROR: {str(err)}\n"

            tx_run_btn.disabled = False
            page.update()

        tx_run_btn = ft.FilledButton(
            "Execute Encryption & Blockchain Registry",
            on_click=run_sender_pipeline
        )

        sender_tab = ft.Column(
            [
                ft.Container(height=4),
                tx_file_row,
                secret_input,
                tx_password_input,
                tx_run_btn,
                tx_log_terminal,
                etherscan_btn,
            ],
            spacing=6,
            scroll=ft.ScrollMode.HIDDEN,
        )

        # ==========================================
        # RECEIVER TAB (EXTRACT DATA)
        # ==========================================
        rx_file_path_text = ft.TextField(label="Stego Image Path (The downloaded file)", read_only=True, expand=True)
        rx_file_picker = ft.FilePicker(on_result=lambda e: update_path(e, rx_file_path_text))
        page.overlay.append(rx_file_picker)
        rx_pick_file_btn = ft.FilledButton("Select Stego Image", on_click=lambda _: rx_file_picker.pick_files()) 
        rx_file_row = ft.Row([rx_file_path_text, rx_pick_file_btn])

        rx_password_input = ft.TextField(label="AES-256 Decryption Password", password=True, can_reveal_password=True)

        rx_log_terminal = ft.TextField(
            label="Extraction Logs", multiline=True, read_only=True,
            min_lines=5, max_lines=5,
            text_style=ft.TextStyle(font_family="Consolas", color="#4ade80")
        )

        def run_receiver_pipeline(e):
            rx_run_btn.disabled = True
            rx_log_terminal.value = "[*] INITIATING RECEIVER EXTRACTION PIPELINE...\n"
            page.update()

            if not rx_file_path_text.value or not rx_password_input.value:
                rx_log_terminal.value += "[-] ERROR: Please select the Stego Image and enter the Password!\n"
                rx_run_btn.disabled = False
                page.update()
                return

            try:
                rx_log_terminal.value += f"[*] TARGET FILE: {rx_file_path_text.value}\n"
                rx_log_terminal.value += "[*] LAYER 1: Extracting Encrypted Data via AI Model...\n"
                page.update()
                
                extracted_b64 = step_4_extract_from_image(rx_file_path_text.value)
                
                if extracted_b64:
                    rx_log_terminal.value += "[*] LAYER 2: Decrypting Payload with AES-256...\n"
                    page.update()
                    
                    decrypted_message = test_decrypt_payload(extracted_b64, rx_password_input.value)
                    
                    rx_log_terminal.value += "\n[+] ==================================================\n"
                    rx_log_terminal.value += "[+] EXTRACTION SUCCESSFUL!\n"
                    rx_log_terminal.value += f"[+] Secret Message: {decrypted_message}\n"
                    rx_log_terminal.value += "[+] ==================================================\n"
                else:
                    rx_log_terminal.value += "\n[-] EXTRACTION FAILED: No hidden data found.\n"
                
            except Exception as err:
                rx_log_terminal.value += f"\n[-] BACKEND ERROR: {str(err)}\n"

            rx_run_btn.disabled = False
            page.update()

        rx_run_btn = ft.FilledButton("Verify Integrity & Extract Secret", on_click=run_receiver_pipeline)

        receiver_tab = ft.Column(
            [
                ft.Container(height=4),
                rx_file_row, rx_password_input, rx_run_btn, rx_log_terminal
            ],
            spacing=6,
        )

        # ==========================================
        # SHARED HELPER FUNCTION
        # ==========================================
        def update_path(e: ft.FilePickerResultEvent, text_field: ft.TextField):
            if e.files:
                text_field.value = e.files[0].path
                page.update()

        # ==========================================
        # ASSEMBLE THE UI TABS
        # ==========================================
        ui_tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Sender Vault (Hide)", content=sender_tab),
                ft.Tab(text="Receiver Extraction (Reveal)", content=receiver_tab),
            ],
            expand=1,
        )

        page.add(header, ft.Divider(height=10), ui_tabs)

    except Exception as e:
        print("🚨 CRASH DETECTED 🚨")
        traceback.print_exc()

if __name__ == "__main__":
    ft.app(target=main)