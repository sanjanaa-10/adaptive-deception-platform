"""
Quick test client - simulates an attacker connecting to the honeypot sensor.
Run this while honeypot_sensor.py is already running.
"""
import socket
import time

HOST = "localhost"
PORT = 2222

commands_to_try = ["whoami", "cat /etc/passwd", "rm -rf /", "exit"]

with socket.create_connection((HOST, PORT), timeout=5) as s:
    def recv():
        time.sleep(0.3)
        try:
            return s.recv(1024).decode(errors="ignore")
        except socket.timeout:
            return ""

    print(recv(), end="")  # banner

    s.sendall(b"root\n")
    print(recv(), end="")

    s.sendall(b"toor\n")
    print(recv(), end="")

    for cmd in commands_to_try:
        print(f"\n>>> sending command: {cmd}")
        s.sendall((cmd + "\n").encode())
        print(recv(), end="")

print("\n\n[test client] Done. Check /events and /alerts in your API docs.")