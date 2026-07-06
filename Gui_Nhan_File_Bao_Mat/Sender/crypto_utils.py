"""
crypto_utils.py
================
Dùng chung cho Sender GUI và Receiver GUI.
Đồng bộ đúng scheme mật mã với bản CLI (sender.py/receiver.py) đã migrate:
  - Mã hoá đối xứng: AES-256-CBC (khoá phiên 32 byte, IV 16 byte)
  - Trao khoá phiên: RSA-2048 OAEP
  - Chữ ký số: PKCS#1 v1.5 trên SHA-512
  - Metadata = "filename|timestamp|hash_cipher" -> chữ ký bảo vệ luôn
    tính toàn vẹn dữ liệu, không chỉ tên file/thời gian.
"""

import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

AES_KEY_SIZE = 32   # AES-256
RSA_KEY_SIZE = 2048


def generate_rsa_keypair(name: str, folder: str = "."):
    priv_path = os.path.join(folder, f"{name}_private.pem")
    pub_path = os.path.join(folder, f"{name}_public.pem")
    if os.path.exists(priv_path) and os.path.exists(pub_path):
        return priv_path, pub_path
    key = RSA.generate(RSA_KEY_SIZE)
    with open(priv_path, "wb") as f:
        f.write(key.export_key())
    with open(pub_path, "wb") as f:
        f.write(key.publickey().export_key())
    return priv_path, pub_path


def load_key_from_file(path: str) -> RSA.RsaKey:
    with open(path, "rb") as f:
        return RSA.import_key(f.read())


def load_key_from_pem(pem_text: str) -> RSA.RsaKey:
    return RSA.import_key(pem_text)


def generate_session_key() -> bytes:
    return get_random_bytes(AES_KEY_SIZE)


def rsa_encrypt(session_key: bytes, pub_key: RSA.RsaKey) -> bytes:
    return PKCS1_OAEP.new(pub_key).encrypt(session_key)


def rsa_decrypt(enc_key: bytes, priv_key: RSA.RsaKey) -> bytes:
    return PKCS1_OAEP.new(priv_key).decrypt(enc_key)


def aes_encrypt(data: bytes, key: bytes):
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data, AES.block_size))
    return iv, ct


def aes_decrypt(ct: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES.block_size)


def sign_metadata(metadata: bytes, priv_key: RSA.RsaKey) -> bytes:
    h = SHA512.new(metadata)
    return pkcs1_15.new(priv_key).sign(h)


def verify_signature(metadata: bytes, signature: bytes, pub_key: RSA.RsaKey) -> bool:
    h = SHA512.new(metadata)
    try:
        pkcs1_15.new(pub_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False


def sha512_hex(data: bytes) -> str:
    return SHA512.new(data).hexdigest()
