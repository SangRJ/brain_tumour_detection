import os
from cryptography.fernet import Fernet

KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "secret.key")

def get_cipher():
    """Retrieve the Fernet cipher, generating a new encryption key if one does not exist."""
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

cipher = get_cipher()

def encrypt_pii(text: str) -> str:
    """Encrypt a string. If empty or None, return as is."""
    if not text:
        return text
    return cipher.encrypt(text.encode('utf-8')).decode('utf-8')

def decrypt_pii(encrypted_text: str) -> str:
    """Decrypt a string. Gracefully handle unencrypted legacy data."""
    if not encrypted_text:
        return encrypted_text
    try:
        return cipher.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
    except Exception:
        # If decryption fails (InvalidToken), it is legacy plaintext data
        return encrypted_text
