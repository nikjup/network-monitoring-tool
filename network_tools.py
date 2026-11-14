
import subprocess
import re


def run_ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-n", "4", ip],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout

        # Extract packet statistics
        match = re.search(
            r"Sent = (\d+), Received = (\d+), Lost = (\d+)",
            output
        )

        if match:
            sent = int(match.group(1))
            received = int(match.group(2))
            lost = int(match.group(3))

            packet_loss = (lost / sent) * 100 if sent else 0

            output += "\n\n--- Packet Loss Analysis ---\n"
            output += f"Packets Sent: {sent}\n"
            output += f"Packets Received: {received}\n"
            output += f"Packets Lost: {lost}\n"
            output += f"Packet Loss: {packet_loss:.2f}%"

        else:
            output += "\n\nPacket statistics could not be extracted."

        return output

    except subprocess.TimeoutExpired:
        return "Ping request timed out."

    except Exception as e:
        return f"Error: {str(e)}"




def run_traceroute(ip):
    try:
        result = subprocess.run(
            ["tracert", "-d", "-h", "12", "-w", "700", ip],
            capture_output=True,
            text=True,
            timeout=35
        )

        output = result.stdout.strip()

        if result.stderr.strip():
            output += "\n" + result.stderr.strip()

        if not output:
            output = "Traceroute returned no output."

        return output

    except subprocess.TimeoutExpired:
        return "Traceroute timed out. The destination may be unreachable."

    except FileNotFoundError:
        return "Windows tracert command was not found."

    except Exception as e:
        return f"Error: {str(e)}"

