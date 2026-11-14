
from flask import Flask, render_template, redirect, url_for, request, session
from monitor import check_device
from network_tools import run_ping, run_traceroute
import ipaddress

from database import (
    initialize_database,
    create_incident,
    get_incidents,
    acknowledge_incident,
    resolve_incident
)

app = Flask(__name__)
app.secret_key = "network-monitoring-dev-key"

# Devices to monitor
devices = [
    {"name": "Google DNS", "ip": "8.8.8.8"},
    {"name": "Cloudflare DNS", "ip": "1.1.1.1"},
    {"name": "Test Server", "ip": "192.0.2.1"}
]

# Initialize database
initialize_database()


@app.route("/")
def dashboard():

    results = []

    # Monitor all devices
    for device in devices:

        result = check_device(device["ip"])

        status = result["status"]
        latency = result["latency"]

        # Generate incidents
        if status != "Online":

            create_incident(
                device["name"],
                device["ip"],
                "Device unreachable",
                "P2"
            )

        elif latency is not None and latency >= 200:

            create_incident(
                device["name"],
                device["ip"],
                "High network latency",
                "P3"
            )

        else:
            resolve_incident(device["ip"])

        results.append({
            "name": device["name"],
            "ip": device["ip"],
            "status": status,
            "latency": latency
        })

    # Device statistics
    online = sum(
        1 for d in results
        if d["status"] == "Online"
    )

    offline = len(results) - online

    # Retrieve incidents
    incidents = get_incidents()

    # Incident statistics
    incident_stats = {
        "open": sum(
            1 for i in incidents
            if i["status"] == "Open"
        ),
        "acknowledged": sum(
            1 for i in incidents
            if i["status"] == "Acknowledged"
        ),
        "resolved": sum(
            1 for i in incidents
            if i["status"] == "Resolved"
        )
    }

    # Latency chart data
    latency_labels = [
        d["name"] for d in results
    ]

    latency_values = [
        d["latency"] for d in results
    ]

    # Retrieve troubleshooting result
    troubleshooting_result = session.pop(
        "troubleshooting_result", None
    )

    return render_template(
        "dashboard.html",
        devices=results,
        total=len(results),
        online=online,
        offline=offline,
        incidents=incidents,
        incident_stats=incident_stats,
        latency_labels=latency_labels,
        latency_values=latency_values,
        troubleshooting_result=troubleshooting_result
    )


# Network troubleshooting route
@app.route("/troubleshoot", methods=["POST"])
def troubleshoot():

    target = request.form.get("target", "").strip()
    action = request.form.get("action", "").strip()

    try:
        # Accept valid IP addresses only
        ipaddress.ip_address(target)

        if action == "ping":
            output = run_ping(target)

        elif action == "traceroute":
            output = run_traceroute(target)

        else:
            output = "Invalid troubleshooting action."

    except ValueError:
        output = "Invalid IP address. Please enter a valid IP address."

    session["troubleshooting_result"] = {
        "target": target,
        "action": action,
        "output": output
    }

    return redirect(url_for("dashboard"))


# Acknowledge incident
@app.route(
    "/acknowledge/<int:incident_id>",
    methods=["POST"]
)
def acknowledge(incident_id):

    acknowledge_incident(incident_id)

    return redirect(url_for("dashboard"))


if __name__ == "__main__":

    app.run(debug=True)



