import time
import psutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from statistics import mean, median
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class AlertConfig:
    response_time_threshold: float = 1.0  # seconds
    memory_threshold: float = 1024  # MB
    cpu_threshold: float = 80.0  # percent

class EndpointMetrics:
    def __init__(self):
        self.response_times = []
        self.status_codes = []
        self.last_request_time = None
        self.alert_count = 0
    
    def add_request(self, response_time: float, status_code: int):
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        self.last_request_time = datetime.now()
    
    def get_stats(self) -> Dict:
        if not self.response_times:
            return {
                "total_requests": 0,
                "avg_response_time": 0,
                "median_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "status_distribution": {},
                "alert_count": 0
            }
        
        return {
            "total_requests": len(self.response_times),
            "avg_response_time": mean(self.response_times),
            "median_response_time": median(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": sorted(self.response_times)[int(len(self.response_times) * 0.95)],
            "status_distribution": {str(code): self.status_codes.count(code) for code in set(self.status_codes)},
            "alert_count": self.alert_count,
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None
        }

class MetricsCollector:
    def __init__(self):
        self.metrics_file = Path("metrics_log.json")
        self.alerts_file = Path("alerts_log.json")
        self.start_time = time.time()
        self.alert_config = AlertConfig()
        self.endpoints = defaultdict(EndpointMetrics)
        self.system_metrics_history = []
        self.max_history_points = 60  # Keep last 60 measurements
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        if not self.metrics_file.exists():
            self.save_metrics({
                "requests": [],
                "system_metrics": []
            })
        if not self.alerts_file.exists():
            self._save_alerts([])
    
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record metrics for a single request"""
        metrics = self.load_metrics()
        
        # Record in time-series data
        request_metric = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "response_time": response_time,
            "status_code": status_code
        }
        metrics["requests"].append(request_metric)
        
        # Record in endpoint-specific metrics
        self.endpoints[endpoint].add_request(response_time, status_code)
        
        # Check for alerts
        self._check_response_time_alert(endpoint, response_time)
        
        self.save_metrics(metrics)
    
    def record_system_metrics(self):
        """Record system-level metrics"""
        process = psutil.Process()
        current_time = datetime.now()
        
        system_metric = {
            "timestamp": current_time.isoformat(),
            "cpu_percent": process.cpu_percent(),
            "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
            "uptime_seconds": time.time() - self.start_time
        }
        
        # Add to time-series data
        metrics = self.load_metrics()
        metrics["system_metrics"].append(system_metric)
        
        # Keep only recent history
        if len(metrics["system_metrics"]) > self.max_history_points:
            metrics["system_metrics"] = metrics["system_metrics"][-self.max_history_points:]
        
        # Check for system alerts
        self._check_system_alerts(system_metric)
        
        self.save_metrics(metrics)
    
    def _check_response_time_alert(self, endpoint: str, response_time: float):
        """Check if response time exceeds threshold and record alert"""
        if response_time > self.alert_config.response_time_threshold:
            self.endpoints[endpoint].alert_count += 1
            self._record_alert(f"Slow response on {endpoint}: {response_time:.2f}s")
    
    def _check_system_alerts(self, metrics: Dict):
        """Check system metrics for alert conditions"""
        if metrics["memory_usage_mb"] > self.alert_config.memory_threshold:
            self._record_alert(f"High memory usage: {metrics['memory_usage_mb']:.2f}MB")
        
        if metrics["cpu_percent"] > self.alert_config.cpu_threshold:
            self._record_alert(f"High CPU usage: {metrics['cpu_percent']:.2f}%")
    
    def _record_alert(self, message: str):
        """Record an alert message"""
        alerts = self._load_alerts()
        alerts.append({
            "timestamp": datetime.now().isoformat(),
            "message": message
        })
        self._save_alerts(alerts)
    
    def get_summary(self) -> Dict:
        """Get a comprehensive summary of all metrics"""
        metrics = self.load_metrics()
        
        # Get the latest system metrics
        latest_system_metrics = metrics["system_metrics"][-1] if metrics["system_metrics"] else None
        
        # Calculate system metrics trends
        system_metrics_trend = self._calculate_system_metrics_trend(metrics["system_metrics"])
        
        return {
            "endpoints": {
                endpoint: metrics.get_stats()
                for endpoint, metrics in self.endpoints.items()
            },
            "system_metrics": {
                "current": latest_system_metrics,
                "trends": system_metrics_trend
            },
            "alerts": {
                "total_alerts": sum(endpoint.alert_count for endpoint in self.endpoints.values()),
                "recent_alerts": self._load_alerts()[-5:] if self._load_alerts() else []
            },
            "general": {
                "uptime_seconds": time.time() - self.start_time,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat()
            }
        }
    
    def _calculate_system_metrics_trend(self, metrics_history: List[Dict]) -> Dict:
        """Calculate trends in system metrics"""
        if not metrics_history:
            return {}
        
        # Calculate changes over the last hour
        recent_metrics = metrics_history[-self.max_history_points:]
        if len(recent_metrics) < 2:
            return {}
        
        first, last = recent_metrics[0], recent_metrics[-1]
        time_diff = (datetime.fromisoformat(last["timestamp"]) - 
                    datetime.fromisoformat(first["timestamp"])).total_seconds() / 3600  # hours
        
        return {
            "memory_change_per_hour": (last["memory_usage_mb"] - first["memory_usage_mb"]) / time_diff,
            "cpu_average": mean(m["cpu_percent"] for m in recent_metrics)
        }
    
    def load_metrics(self) -> Dict:
        """Load metrics from file"""
        if not self.metrics_file.exists():
            return {"requests": [], "system_metrics": []}
        
        with open(self.metrics_file, 'r') as f:
            return json.load(f)
    
    def save_metrics(self, metrics: Dict):
        """Save metrics to file"""
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def _load_alerts(self) -> List:
        """Load alerts from file"""
        if not self.alerts_file.exists():
            return []
        
        with open(self.alerts_file, 'r') as f:
            return json.load(f)
    
    def _save_alerts(self, alerts: List):
        """Save alerts to file"""
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2) 