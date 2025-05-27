import csv
from datetime import datetime
import os
from typing import Dict, Any

class MetricsLogger:
    def __init__(self, csv_file: str = "metrics_history.csv"):
        self.csv_file = csv_file
        self.initialize_csv()
    
    def initialize_csv(self):
        """Create CSV with headers if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            headers = [
                'timestamp',
                'endpoint',
                'total_requests',
                'avg_response_time_ms',
                'success_rate',
                'alert_count',
                'cpu_percent',
                'memory_usage_mb',
                'memory_trend_mb_hour',
                'uptime_seconds'
            ]
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    def log_metrics(self, metrics_data: Dict[str, Any]):
        """Append current metrics to CSV file"""
        current_time = datetime.now().isoformat()
        system_metrics = metrics_data["system_metrics"]["current"]
        system_trends = metrics_data["system_metrics"].get("trends", {})
        
        # Prepare rows for each endpoint
        rows = []
        for endpoint, data in metrics_data["endpoints"].items():
            # Calculate success rate
            total_requests = data["total_requests"]
            success_count = data["status_distribution"].get("200", 0)
            success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
            
            row = [
                current_time,
                endpoint,
                total_requests,
                round(data["avg_response_time"] * 1000, 2),  # Convert to ms
                round(success_rate, 2),
                data["alert_count"],
                system_metrics["cpu_percent"],
                round(system_metrics["memory_usage_mb"], 2),
                round(system_trends.get("memory_change_per_hour", 0), 2),
                round(metrics_data["general"]["uptime_seconds"], 2)
            ]
            rows.append(row)
        
        # Append to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    def get_latest_metrics(self) -> Dict[str, Any]:
        """Read the latest metrics for each endpoint from the CSV"""
        if not os.path.exists(self.csv_file):
            return {}
        
        latest_metrics = {}
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                return {}
            
            # Get the latest entry for each endpoint
            for row in reversed(rows):
                endpoint = row['endpoint']
                if endpoint not in latest_metrics:
                    latest_metrics[endpoint] = {
                        'timestamp': row['timestamp'],
                        'total_requests': int(row['total_requests']),
                        'avg_response_time_ms': float(row['avg_response_time_ms']),
                        'success_rate': float(row['success_rate']),
                        'alert_count': int(row['alert_count']),
                        'system_metrics': {
                            'cpu_percent': float(row['cpu_percent']),
                            'memory_usage_mb': float(row['memory_usage_mb']),
                            'memory_trend_mb_hour': float(row['memory_trend_mb_hour'])
                        }
                    }
        
        return latest_metrics

    def get_metrics_summary(self) -> str:
        """Generate a summary of metrics history"""
        if not os.path.exists(self.csv_file):
            return "No metrics data available."
        
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                return "No metrics data available."
            
            summary = "Metrics Summary\n"
            summary += "===============\n\n"
            
            # Group by endpoint
            endpoints = {}
            for row in rows:
                endpoint = row['endpoint']
                if endpoint not in endpoints:
                    endpoints[endpoint] = []
                endpoints[endpoint].append(row)
            
            # Generate summary for each endpoint
            for endpoint, data in endpoints.items():
                summary += f"Endpoint: {endpoint}\n"
                summary += "-" * (len(endpoint) + 10) + "\n"
                
                # Calculate averages
                avg_response_time = sum(float(d['avg_response_time_ms']) for d in data) / len(data)
                avg_success_rate = sum(float(d['success_rate']) for d in data) / len(data)
                total_alerts = sum(int(d['alert_count']) for d in data)
                
                summary += f"Average Response Time: {avg_response_time:.2f}ms\n"
                summary += f"Average Success Rate: {avg_success_rate:.2f}%\n"
                summary += f"Total Alerts: {total_alerts}\n"
                summary += f"Total Requests: {data[-1]['total_requests']}\n\n"
            
            # System metrics from latest entry
            latest = rows[-1]
            summary += "Current System Metrics\n"
            summary += "---------------------\n"
            summary += f"CPU Usage: {latest['cpu_percent']}%\n"
            summary += f"Memory Usage: {latest['memory_usage_mb']} MB\n"
            summary += f"Memory Trend: {latest['memory_trend_mb_hour']} MB/hour\n"
            
            return summary 