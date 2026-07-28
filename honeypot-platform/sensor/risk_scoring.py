"""
Simple heuristic risk scoring for honeypot events.
Returns a score between 0.0 (benign) and 1.0 (highly malicious).

This is intentionally rule-based and easy to explain in an interview:
"I score behavior based on known attacker patterns — recon commands,
privilege escalation attempts, payload downloads, and destructive commands
all raise the score."
"""

COMMON_WEAK_CREDS = {
    ("root", "root"), ("root", "toor"), ("admin", "admin"),
    ("root", "123456"), ("admin", "password"), ("root", "password"),
}

HIGH_RISK_PATTERNS = [
    "rm -rf", "wget ", "curl ", "chmod +x", "chmod 777",
    "base64 -d", "nc -e", "/etc/shadow", "python -c",
    "curl | bash", "wget | sh", ":(){ :|:& };:",  # fork bomb pattern
]

MEDIUM_RISK_PATTERNS = [
    "whoami", "cat /etc/passwd", "uname -a", "sudo ", "id",
    "ps aux", "ifconfig", "netstat", "history",
]


def score_login_attempt(username: str, password: str) -> float:
    if (username.lower(), password) in COMMON_WEAK_CREDS:
        return 0.6
    if username.lower() in ("root", "admin"):
        return 0.4
    return 0.2


def score_command(command: str) -> float:
    lowered = command.lower()

    for pattern in HIGH_RISK_PATTERNS:
        if pattern in lowered:
            return 0.9

    for pattern in MEDIUM_RISK_PATTERNS:
        if pattern in lowered:
            return 0.5

    return 0.25
