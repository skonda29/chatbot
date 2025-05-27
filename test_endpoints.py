import requests
import json
import time
from datetime import datetime
import asyncio
import sys
from typing import Dict, Any
from metrics_logger import MetricsLogger

def format_metrics_report(metrics_data: Dict[str, Any]) -> str:
    now = datetime.now()
    report = f"""Metrics Report - {now.strftime('%Y-%m-%d %H:%M')}

1. Endpoint Performance
-------------------"""
    
    # Format endpoint metrics
    for endpoint, data in metrics_data["endpoints"].items():
        report += f"\n\n{endpoint} Endpoint:"
        report += f"\n- Total Requests: {data['total_requests']}"
        report += f"\n- Average Response Time: {data['avg_response_time']*1000:.2f}ms"
        report += f"\n- Status Distribution: {data['status_distribution']}"
        report += f"\n- Alert Count: {data['alert_count']}"
        if data.get('last_request_time'):
            report += f"\n- Last Request: {data['last_request_time']}"

    # System metrics
    report += "\n\n2. System Metrics"
    report += "\n--------------"
    report += "\nCurrent State:"
    sys_metrics = metrics_data["system_metrics"]["current"]
    report += f"\n- CPU Usage: {sys_metrics['cpu_percent']}%"
    report += f"\n- Memory Usage: {sys_metrics['memory_usage_mb']:.2f} MB"
    
    if "trends" in metrics_data["system_metrics"]:
        trends = metrics_data["system_metrics"]["trends"]
        report += f"\n- Memory Trend: {trends['memory_change_per_hour']:.2f} MB/hour"
        report += f"\n- Average CPU: {trends['cpu_average']}%"

    # Alerts
    report += "\n\n3. Alert History"
    report += "\n-------------"
    report += "\nRecent Alerts:"
    for alert in metrics_data["alerts"]["recent_alerts"]:
        report += f"\n- {alert['timestamp']} - {alert['message']}"

    # Server info
    report += "\n\n4. Server Information"
    report += "\n------------------"
    report += f"\n- Uptime: {metrics_data['general']['uptime_seconds']:.2f} seconds"
    report += f"\n- Start Time: {metrics_data['general']['start_time']}"
    
    return report

def test_endpoints(base_url: str = "http://127.0.0.1:8000") -> None:
    """Test all endpoints and update metrics file"""
    print("Starting endpoint tests...")
    
    try:
        # Initialize metrics logger
        metrics_logger = MetricsLogger()
        
        # Test root endpoint
        print("Testing root endpoint...")
        root_response = requests.get(f"{base_url}/")
        print(f"Root endpoint status: {root_response.status_code}")

        # Test docs endpoint
        print("Testing docs endpoint...")
        docs_response = requests.get(f"{base_url}/docs")
        print(f"Docs endpoint status: {docs_response.status_code}")

        # Test chat endpoint
        print("Testing chat endpoint...")
        chat_data = {
            "session_id": "test_session",
            "query": "Hello, this is a test message"
        }
        chat_response = requests.post(
            f"{base_url}/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Chat endpoint status: {chat_response.status_code}")

        # Get updated metrics
        print("Fetching metrics...")
        metrics_response = requests.get(f"{base_url}/metrics")
        metrics_data = metrics_response.json()

        # Log metrics to CSV
        metrics_logger.log_metrics(metrics_data)
        print("Metrics logged to CSV successfully!")

        # Format and save text report
        report = format_metrics_report(metrics_data)
        with open("metrics_report.txt", "w") as f:
            f.write(report)
        print("Metrics report updated successfully!")

        # Generate and save summary
        summary = metrics_logger.get_metrics_summary()
        with open("metrics_summary.txt", "w") as f:
            f.write(summary)
        print("Metrics summary generated successfully!")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running.")
        sys.exit(1)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        sys.exit(1)

def wait_for_server(base_url: str = "http://127.0.0.1:8000", timeout: int = 30) -> bool:
    """Wait for server to become available"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            requests.get(base_url)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

if __name__ == "__main__":
    print("Waiting for server to start...")
    if wait_for_server():
        print("Server is up! Starting tests...")
        # Wait a bit more for the server to fully initialize
        time.sleep(2)
        test_endpoints()
    else:
        print("Server did not become available within timeout period.")
        sys.exit(1) 