import tkinter as tk
from tkinter import scrolledtext, simpledialog
import socket
import threading

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.client_username = simpledialog.askstring("Username", "Enter your username:", parent=self.root)
        if not self.client_username:
            self.client_username = "Client"

        self.root.title(f"Chat Client ({self.client_username})")

        self.messages_area = scrolledtext.ScrolledText(root, state=tk.DISABLED)
        self.messages_area.pack(padx=20, pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(padx=20, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(padx=20, pady=5, side=tk.LEFT)

        self.exit_button = tk.Button(root, text="Exit", command=self.on_closing)
        self.exit_button.pack(padx=20, pady=5, side=tk.RIGHT)

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread(target=self.connect_to_server).start()

    def connect_to_server(self):
        self.client_sock.connect(('127.0.0.1', 8080))
        threading.Thread(target=self.receive_message).start()

    def log_message(self, message):
        self.messages_area.config(state=tk.NORMAL)
        self.messages_area.insert(tk.END, message + "\n")
        self.messages_area.config(state=tk.DISABLED)

    def receive_message(self):
        while True:
            try:
                data = self.client_sock.recv(1024)
                if not data:
                    break
                message = data.decode()
                self.log_message(message)
            except OSError:
                break

    def send_message(self, event=None):
        message = self.entry.get()
        formatted_message = f"{self.client_username}: {message}"
        self.log_message(formatted_message)
        self.client_sock.sendall(formatted_message.encode())
        self.entry.delete(0, tk.END)

    def on_closing(self):
        self.client_sock.close()
        self.root.destroy()

root = tk.Tk()
app = ClientApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
