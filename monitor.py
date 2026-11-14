
import subprocess
import re

def check_device(ip):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "1000", ip],
        capture_output=True,
        text=True
    )

    output = result.stdout

    if result.returncode == 0:
        match = re.search(
            r"(?:time[=<]\s*)(\d+)\s*ms",
            output,
            re.IGNORECASE
        )

        latency = int(match.group(1)) if match else None

        return {
            "ip": ip,
            "status": "Online",
            "latency": latency
        }

    return {
        "ip": ip,
        "status": "Unreachable",
        "latency": None
    }


if __name__ == "__main__":
    devices = ["8.8.8.8", "1.1.1.1", "192.0.2.1"]

    for device in devices:
        print(check_device(device))
