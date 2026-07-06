import tkinter as tk
from tkinter import messagebox
import subprocess
import audio_utils

root = tk.Tk()
root.title("Voice Sender")
root.geometry("400x250")


def record():

    try:
        audio_utils.record_audio(
            filename="voice.wav",
            duration=5
        )

        messagebox.showinfo(
            "Thông báo",
            "Đã ghi âm xong!"
        )

    except Exception as e:

        messagebox.showerror(
            "Lỗi",
            str(e)
        )


def send():

    try:

        subprocess.run(
            ["py", "sender.py"]
        )

    except Exception as e:

        messagebox.showerror(
            "Lỗi",
            str(e)
        )


tk.Label(
    root,
    text="Legacy Voice Encryption",
    font=("Arial",16)
).pack(pady=15)

tk.Button(
    root,
    text="🎤 Ghi âm",
    width=20,
    command=record
).pack(pady=10)

tk.Button(
    root,
    text="📤 Gửi",
    width=20,
    command=send
).pack(pady=10)

root.mainloop()