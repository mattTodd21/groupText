import tkinter as tk
from tkinter import scrolledtext, simpledialog
import socket
import threading

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.server_username = simpledialog.askstring("Username", "Enter your username:", parent=self.root)
        if not self.server_username:
            self.server_username = "Server"

        self.root.title(f"Chat Server ({self.server_username})")

        self.messages_area = scrolledtext.ScrolledText(root, state=tk.DISABLED)
        self.messages_area.pack(padx=20, pady=10)

        self.entry = tk.Entry(root)
        self.entry.pack(padx=20, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(padx=20, pady=5, side=tk.LEFT)

        self.exit_button = tk.Button(root, text="Exit", command=self.on_closing)
        self.exit_button.pack(padx=20, pady=5, side=tk.RIGHT)

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('', 8080))                        # input your ip address and socket you would like to use
        self.server_sock.listen()
        self.log_message("Server listening on port 8080...")

        self.client_socks = []
        self.running = True
        threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while self.running:
            try:
                client_sock, _ = self.server_sock.accept()
                if not self.running:
                    break
                self.client_socks.append(client_sock)
                threading.Thread(target=self.handle_client, args=(client_sock,)).start()
                self.log_message("New client connected.")
            except OSError:
                break

    def handle_client(self, client_sock):
        while True:
            try:
                data = client_sock.recv(1024)
                if not data:
                    break
                message = data.decode()
                self.log_message(message)
                self.broadcast_message(message, client_sock)
            except OSError:
                break
        self.client_socks.remove(client_sock)
        client_sock.close()

    def broadcast_message(self, message, sender_sock):
        for client_sock in self.client_socks:
            if client_sock != sender_sock:
                try:
                    client_sock.sendall(message.encode())
                except OSError:
                    pass

    def log_message(self, message):
        self.messages_area.config(state=tk.NORMAL)
        self.messages_area.insert(tk.END, message + "\n")
        self.messages_area.config(state=tk.DISABLED)

    def send_message(self, event=None):
        message = self.entry.get()
        formatted_message = f"{self.server_username}: {message}"
        self.log_message(formatted_message)
        self.broadcast_message(formatted_message, None)
        self.entry.delete(0, tk.END)

    def on_closing(self):
        self.running = False
        for sock in self.client_socks:
            sock.close()
        self.server_sock.close()
        self.root.destroy()

root = tk.Tk()
app = ServerApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
