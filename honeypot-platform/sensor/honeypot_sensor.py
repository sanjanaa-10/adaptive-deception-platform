"""
Adaptive honeypot sensor.

Simulates a fake SSH-like login shell. Any connection is logged; any
credentials tried and any commands typed are scored and reported to the
backend as events. High-risk events auto-trigger alerts in the backend,
and automatically switch the decoy into a higher-interaction mode.

Run this AFTER the backend (uvicorn) is already running.

Usage:
    python sensor/honeypot_sensor.py
"""
import socketserver
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sensor.risk_scoring import score_login_attempt, score_command

BACKEND_URL = "http://localhost:8000"
DECOY_NAME = "fake-ssh-server-clean-test"
DECOY_HOST = "0.0.0.0"
DECOY_PORT = 2222  # the fake service listens here (not real port 22, safer for local testing)

FAKE_BANNER = b"SSH-2.0-OpenSSH_7.4\r\n"
FAKE_PROMPT = b"$ "

ADAPT_THRESHOLD = 0.7  # matches the backend's alert threshold

# Richer fake responses shown only once a decoy has "adapted" into
# high-interaction mode. This is what makes the adaptation visible/demoable:
# an attacker who trips the risk threshold suddenly starts seeing convincing
# (fake) sensitive data, which keeps them engaged so we can log more.
HIGH_INTERACTION_RESPONSES = {
    "ls": "backup.sql  config.yaml  id_rsa  notes.txt",
    "cat /etc/passwd": (
        "root:x:0:0:root:/root:/bin/bash\r\n"
        "admin:x:1000:1000::/home/admin:/bin/bash\r\n"
        "svc_backup:x:1001:1001::/home/svc_backup:/bin/false"
    ),
    "cat config.yaml": "db_host: 10.0.0.14\r\ndb_user: svc_backup\r\ndb_pass: [REDACTED_FAKE_CREDENTIAL]",
    "cat id_rsa": "-----BEGIN OPENSSH PRIVATE KEY-----\r\n[FAKE KEY - NOT A REAL CREDENTIAL]\r\n-----END OPENSSH PRIVATE KEY-----",
}


def get_or_create_decoy() -> int:
    """Registers this honeypot as a 'decoy' in the backend, or reuses it if it already exists."""
    resp = requests.get(f"{BACKEND_URL}/decoys/")
    resp.raise_for_status()
    for decoy in resp.json():
        if decoy["name"] == DECOY_NAME:
            print(f"[+] Reusing existing decoy id={decoy['id']}")
            return decoy["id"]

    resp = requests.post(
        f"{BACKEND_URL}/decoys/",
        json={
            "name": DECOY_NAME,
            "service_type": "SSH",
            "ip": DECOY_HOST,
            "port": DECOY_PORT,
            "adaptive_profile": {"mode": "low-interaction"},
        },
    )
    resp.raise_for_status()
    decoy = resp.json()
    print(f"[+] Registered new decoy id={decoy['id']}")
    return decoy["id"]


def report_event(decoy_id: int, attacker_ip: str, event_type: str, payload: str, risk_score: float):
    try:
        requests.post(
            f"{BACKEND_URL}/events",
            json={
                "decoy_id": decoy_id,
                "attacker_ip": attacker_ip,
                "event_type": event_type,
                "payload": payload,
                "risk_score": risk_score,
            },
            timeout=3,
        )
    except requests.RequestException as e:
        print(f"[!] Failed to report event to backend: {e}")
        return

    # Adaptive deception: once behavior looks serious, tell the backend to
    # switch this decoy into a higher-interaction mode.
    if risk_score >= ADAPT_THRESHOLD:
        try:
            requests.post(f"{BACKEND_URL}/decoys/{decoy_id}/adapt", timeout=3)
            print(f"[!] Risk {risk_score} crossed threshold — decoy {decoy_id} adapting")
        except requests.RequestException as e:
            print(f"[!] Failed to trigger adaptation: {e}")


def get_decoy_mode(decoy_id: int) -> str:
    """Checks the decoy's current adaptive_profile to decide how to behave."""
    try:
        resp = requests.get(f"{BACKEND_URL}/decoys/", timeout=3)
        resp.raise_for_status()
        for decoy in resp.json():
            if decoy["id"] == decoy_id:
                profile = decoy.get("adaptive_profile", {})
                return "high-interaction" if profile.get("last_adaptation") == "triggered" else "low-interaction"
    except requests.RequestException:
        pass
    return "low-interaction"


class HoneypotHandler(socketserver.BaseRequestHandler):
    decoy_id = None  # set once at server start

    def handle(self):
        attacker_ip = self.client_address[0]
        print(f"[>] Connection from {attacker_ip}")

        try:
            self.request.sendall(FAKE_BANNER)

            # --- Fake login prompt ---
            self.request.sendall(b"login: ")
            username = self._read_line()
            self.request.sendall(b"password: ")
            password = self._read_line()

            login_risk = score_login_attempt(username, password)
            report_event(
                self.decoy_id, attacker_ip, "login_attempt",
                f"username={username} password={password}", login_risk,
            )

            # Always "succeed" so the attacker keeps interacting (this is the deception part)
            self.request.sendall(b"\r\nLast login: Mon Jul 27 10:00:00 2026\r\n")

            # --- Fake shell loop ---
            while True:
                self.request.sendall(FAKE_PROMPT)
                command = self._read_line()
                if not command:
                    break
                if command.strip().lower() in ("exit", "logout", "quit"):
                    break

                cmd_risk = score_command(command)
                report_event(self.decoy_id, attacker_ip, "command_exec", command, cmd_risk)

                mode = get_decoy_mode(self.decoy_id)
                if mode == "high-interaction" and command.strip() in HIGH_INTERACTION_RESPONSES:
                    reply = HIGH_INTERACTION_RESPONSES[command.strip()] + "\r\n"
                    self.request.sendall(reply.encode())
                else:
                    # low-interaction mode: fake generic response
                    self.request.sendall(b"\r\n")

        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass
        finally:
            print(f"[<] Connection closed from {attacker_ip}")

    def _read_line(self, max_bytes=1024) -> str:
        data = self.request.recv(max_bytes)
        return data.decode(errors="ignore").strip()


class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def main():
    decoy_id = get_or_create_decoy()
    HoneypotHandler.decoy_id = decoy_id

    server = ThreadingTCPServer((DECOY_HOST, DECOY_PORT), HoneypotHandler)
    print(f"[+] Honeypot listening on {DECOY_HOST}:{DECOY_PORT} (decoy_id={decoy_id})")
    print("[+] Test it from another terminal with: python sensor/test_attacker.py")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[+] Shutting down honeypot.")
        server.shutdown()


if __name__ == "__main__":
    main()