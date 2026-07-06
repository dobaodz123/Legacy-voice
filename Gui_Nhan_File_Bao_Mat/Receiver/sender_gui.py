import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import audio_utils

# =============================
# Hàm ghi âm
# =============================
def record_audio():

    try:
        audio_utils.record_audio(
            filename="voice.wav",
            duration=5
        )

        lbl_status.config(
            text="Đã ghi âm xong!"
        )

        messagebox.showinfo(
            "Thông báo",
            "Đã lưu voice.wav"
        )

    except Exception as e:

        messagebox.showerror(
            "Lỗi",
            str(e)
        )


# =============================
# Hàm gửi
# =============================
def send_audio():

    if not os.path.exists("voice.wav"):

        messagebox.showwarning(
            "Thông báo",
            "Hãy ghi âm trước!"
        )

        return

    lbl_status.config(
        text="Đang gửi..."
    )

    try:

        subprocess.run(
            ["py", "sender.py"]
        )

        lbl_status.config(
            text="Đã gửi thành công"
        )

    except Exception as e:

        messagebox.showerror(
            "Lỗi",
            str(e)
        )


# =============================
# Không để GUI bị treo
# =============================
def send_thread():

    threading.Thread(
        target=send_audio
    ).start()


# =============================
# Giao diện
# =============================

root = tk.Tk()

root.title("Legacy Voice Sender")

root.geometry("450x300")

root.resizable(False, False)

title = tk.Label(
    root,
    text="Legacy Voice Encryption",
    font=("Arial",18,"bold")
)

title.pack(pady=20)


btn_record = tk.Button(

    root,

    text="🎤 Ghi âm",

    width=25,

    height=2,

    command=record_audio

)

btn_record.pack(pady=10)


btn_send = tk.Button(

    root,

    text="📤 Gửi",

    width=25,

    height=2,

    command=send_thread

)

btn_send.pack(pady=10)


lbl_status = tk.Label(

    root,

    text="Sẵn sàng",

    fg="blue"

)

lbl_status.pack(pady=20)


root.mainloop()