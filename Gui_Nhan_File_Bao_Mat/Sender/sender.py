
import os
import sys
import socket
import base64
import json
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import tkinter as tk
from tkinter import messagebox

import record_audio_util

print(record_audio_util)
print(record_audio_util.__file__)
print(hasattr(record_audio_util, "record_audio"))
# Địa chỉ và cổng kết nối đến Receiver
# Có thể truyền IP của Receiver qua tham số dòng lệnh: python3 sender.py <IP_Receiver>
HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = 65432

# File âm thanh cần gửi
# File âm thanh cần gửi
import record_audio_util

import os

FILE_NAME = "voice.wav.wav"

choice = input("Bạn có muốn ghi âm mới không? (y/n): ").strip().lower()

if choice == "y":
    FILE_NAME = "voice.wav"
    print("Đang ghi âm 5 giây...")
    record_audio_util.record_audio(FILE_NAME, 5)
    print("Đã ghi âm xong.")

elif choice == "n":
    if not os.path.exists(FILE_NAME):
        print(f"Không tìm thấy file {FILE_NAME}")
        exit()
    print("Sử dụng file ghi âm có sẵn:", FILE_NAME)

else:
    print("Vui lòng nhập y hoặc n.")
    exit()
# ==========================
# Tạo khóa RSA cho Sender
# ==========================
if not os.path.exists('sender_private.pem'):
    key = RSA.generate(2048)

    with open('sender_private.pem', 'wb') as f:
        f.write(key.export_key())

    with open('sender_public.pem', 'wb') as f:
        f.write(key.publickey().export_key())

    print("Sender: Đã tạo cặp khóa RSA.")
    time.sleep(2)

# ==========================
# Kết nối Receiver
# ==========================
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((HOST, PORT))

    print(f"Sender: Đã kết nối tới {HOST}:{PORT}")
    time.sleep(2)

    # -----------------------
    # BƯỚC 1: HANDSHAKE
    # -----------------------

    print("Sender: Đang thực hiện BƯỚC 1 - Handshake...")

    s.sendall(b"HELLO")

    print("Sender: Gửi HELLO")
    time.sleep(2)

    data = s.recv(5)

    if data == b"READY":

        print("Sender: Nhận READY từ Receiver")
        time.sleep(2)

    else:

        print("Sender: Handshake thất bại")
        exit()

    # -----------------------
    # Nhận Public Key Receiver
    # -----------------------

    print("Sender: Đang nhận PublicKey...")

    size = int.from_bytes(s.recv(4), "big")

    pub_R_data = s.recv(size)

    with open("receiver_public.pem", "wb") as f:
        f.write(pub_R_data)

    print("Sender: Đã nhận PublicKey Receiver")
    time.sleep(2)

    # Load khóa

    pub_R = RSA.import_key(pub_R_data)

    priv_S = RSA.import_key(
        open("sender_private.pem", "rb").read()
    )

    # -----------------------
    # Tạo Session Key AES-256
    # (Nâng cấp từ DES 8-byte/56-bit lên AES-256 theo đúng yêu cầu đề tài)
    # -----------------------

    session_key = get_random_bytes(32)

    encrypted_session_key = PKCS1_OAEP.new(pub_R).encrypt(session_key)

    print("Sender: SessionKey AES-256 tạo thành công")

    time.sleep(2)

    # -----------------------
    # Đọc file âm thanh
    # -----------------------

    if not os.path.exists(FILE_NAME):

        print(f"Lỗi: Không tìm thấy {FILE_NAME}")

        exit()

    with open(FILE_NAME, "rb") as f:

        plaintext = f.read()

    print(f"Sender: Đọc {len(plaintext)} bytes")

    time.sleep(2)

    # -----------------------
    # AES-256-CBC Encrypt
    # -----------------------

    iv = get_random_bytes(16)

    cipher = AES.new(
        session_key,
        AES.MODE_CBC,
        iv
    ).encrypt(
        pad(
            plaintext,
            AES.block_size
        )
    )

    print("Sender: AES Encrypt thành công")

    time.sleep(2)

    # -----------------------
    # SHA512 Hash của ciphertext
    # -----------------------

    hash_cipher = SHA512.new(cipher).hexdigest()

    print("Sender: Hash =", hash_cipher)

    time.sleep(2)

    # -----------------------
    # Metadata + Ký (metadata gồm cả hash của
    # ciphertext để chữ ký cũng bảo vệ luôn tính
    # toàn vẹn dữ liệu, tránh bị thay cả cipher lẫn
    # hash cùng lúc mà không bị phát hiện)
    # -----------------------

    timestamp = int(time.time())

    metadata = f"{FILE_NAME}|{timestamp}|{hash_cipher}"

    print("Sender: Metadata =", metadata)

    h_meta = SHA512.new(metadata.encode())

    signature = pkcs1_15.new(priv_S).sign(h_meta)

    # -----------------------
    # Đóng gói JSON
    # -----------------------

    packet = {

        "esk": base64.b64encode(
            encrypted_session_key
        ).decode(),

        "sig": base64.b64encode(
            signature
        ).decode(),

        "metadata": metadata,

        "iv": base64.b64encode(
            iv
        ).decode(),

        "cipher": base64.b64encode(
            cipher
        ).decode(),

    }

    packet = json.dumps(packet).encode()

    # -----------------------
    # Gửi dữ liệu
    # -----------------------

    print("Sender: Đang gửi dữ liệu...")

    s.sendall(

        len(packet).to_bytes(4, "big")

        + packet

    )

    print("Sender: Đã gửi thành công")

    time.sleep(2)

    # -----------------------
    # Nhận ACK
    # -----------------------

    response = s.recv(4)

    if response == b"ACK":

        print("===================================")
        print("Sender: Receiver xác nhận thành công")
        print("===================================")

    elif response == b"NACK":

        print("===================================")
        print("Sender: Receiver từ chối dữ liệu")
        print("===================================")

    else:

        print("Sender: Phản hồi không xác định")

    time.sleep(2)

print("\nSender kết thúc.")
