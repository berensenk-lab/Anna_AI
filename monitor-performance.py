#!/usr/bin/env python
"""
Anna AI Performance Monitor
Tracks system performance, memory usage, and GPU utilization
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import psutil
    import torch
    import GPUtil
except ImportError:
    print("ERROR: Required packages missing. Install with:")
    print("  pip install psutil")
    exit(1)


class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.start_timestamp = datetime.now()
        self.metrics = {
            "started": self.start_timestamp.isoformat(),
            "cpu": {},
            "memory": {},
            "gpu": {},
            "ollama": {},
            "python_process": {}
        }

    def get_cpu_metrics(self):
        """Get CPU performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            "percent_used": cpu_percent,
            "count": cpu_count,
            "frequency_mhz": cpu_freq.current if cpu_freq else "N/A",
            "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else "N/A"
        }

    def get_memory_metrics(self):
        """Get system memory metrics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent_used": memory.percent,
            "swap_total_gb": round(swap.total / (1024**3), 2),
            "swap_used_gb": round(swap.used / (1024**3), 2),
            "swap_percent": swap.percent
        }

    def get_gpu_metrics(self):
        """Get GPU performance metrics"""
        try:
            # Check CUDA availability
            cuda_available = torch.cuda.is_available()
            
            if not cuda_available:
                return {"status": "CUDA not available (CPU-only PyTorch)"}
            
            # Get GPU info
            device_count = torch.cuda.device_count()
            gpu_metrics = {
                "status": "OK",
                "cuda_available": True,
                "device_count": device_count,
                "devices": []
            }
            
            for i in range(device_count):
                device_name = torch.cuda.get_device_name(i)
                device_props = torch.cuda.get_device_properties(i)
                device_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                
                try:
                    # Try to get current memory usage
                    allocated = torch.cuda.memory_allocated(i) / (1024**3)
                    reserved = torch.cuda.memory_reserved(i) / (1024**3)
                    cached = torch.cuda.memory_cached(i) / (1024**3) if hasattr(torch.cuda, 'memory_cached') else 0
                except:
                    allocated = reserved = cached = 0
                
                gpu_metrics["devices"].append({
                    "device_id": i,
                    "name": device_name,
                    "total_memory_gb": round(device_memory, 2),
                    "allocated_gb": round(allocated, 2),
                    "reserved_gb": round(reserved, 2),
                    "cached_gb": round(cached, 2),
                    "utilization_percent": round((allocated / device_memory) * 100, 2) if device_memory > 0 else 0,
                    "compute_capability": f"{device_props.major}.{device_props.minor}"
                })
            
            return gpu_metrics
        except Exception as e:
            return {"error": str(e)}

    def get_ollama_metrics(self):
        """Check Ollama connectivity and status"""
        try:
            import requests
            
            response = requests.get('http://localhost:11434/api/version', timeout=2)
            if response.status_code == 200:
                version_info = response.json()
                return {
                    "status": "connected",
                    "version": version_info.get('version', 'unknown'),
                    "endpoint": "http://localhost:11434"
                }
        except Exception as e:
            return {
                "status": "not_responding",
                "error": str(e),
                "endpoint": "http://localhost:11434"
            }
        
        return {"status": "unknown"}

    def get_python_process_metrics(self):
        """Get current Python process metrics"""
        try:
            process = psutil.Process()
            
            return {
                "pid": process.pid,
                "memory_mb": round(process.memory_info().rss / (1024**2), 2),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "num_threads": process.num_threads(),
                "status": process.status()
            }
        except Exception as e:
            return {"error": str(e)}

    def collect_metrics(self):
        """Collect all performance metrics"""
        self.metrics["cpu"] = self.get_cpu_metrics()
        self.metrics["memory"] = self.get_memory_metrics()
        self.metrics["gpu"] = self.get_gpu_metrics()
        self.metrics["ollama"] = self.get_ollama_metrics()
        self.metrics["python_process"] = self.get_python_process_metrics()
        self.metrics["uptime_seconds"] = time.time() - self.start_time
        
        return self.metrics

    def format_output(self, metrics):
        """Format metrics for console display"""
        output = []
        output.append("\n" + "="*60)
        output.append("Anna AI Performance Monitor".center(60))
        output.append("="*60)
        
        # CPU
        output.append(f"\n[CPU]")
        output.append(f"  Usage: {metrics['cpu']['percent_used']}%")
        output.append(f"  Cores: {metrics['cpu']['count']}")
        if metrics['cpu']['frequency_mhz'] != "N/A":
            output.append(f"  Frequency: {metrics['cpu']['frequency_mhz']} MHz")
        
        # Memory
        output.append(f"\n[MEMORY]")
        output.append(f"  Total: {metrics['memory']['total_gb']} GB")
        output.append(f"  Used: {metrics['memory']['used_gb']} GB ({metrics['memory']['percent_used']}%)")
        output.append(f"  Available: {metrics['memory']['available_gb']} GB")
        output.append(f"  Swap: {metrics['memory']['swap_used_gb']} / {metrics['memory']['swap_total_gb']} GB")
        
        # GPU
        output.append(f"\n[GPU]")
        if "error" in metrics['gpu']:
            output.append(f"  Error: {metrics['gpu']['error']}")
        elif "status" in metrics['gpu'] and metrics['gpu']['status'] != "OK":
            output.append(f"  Status: {metrics['gpu']['status']}")
        else:
            output.append(f"  Devices: {metrics['gpu'].get('device_count', 0)}")
            for device in metrics['gpu'].get('devices', []):
                output.append(f"  Device {device['device_id']}: {device['name']}")
                output.append(f"    Memory: {device['allocated_gb']} / {device['total_memory_gb']} GB ({device['utilization_percent']}%)")
                output.append(f"    Compute: {device['compute_capability']}")
        
        # Ollama
        output.append(f"\n[OLLAMA]")
        output.append(f"  Status: {metrics['ollama'].get('status', 'unknown')}")
        if metrics['ollama'].get('version'):
            output.append(f"  Version: {metrics['ollama']['version']}")
        if metrics['ollama'].get('error'):
            output.append(f"  Error: {metrics['ollama']['error']}")
        
        # Uptime
        uptime = metrics['uptime_seconds']
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        output.append(f"\n[UPTIME] {hours}h {minutes}m {seconds}s")
        
        output.append("\n" + "="*60 + "\n")
        
        return "\n".join(output)

    def run(self, continuous=False, interval=5):
        """Run performance monitor"""
        try:
            while True:
                metrics = self.collect_metrics()
                print(self.format_output(metrics))
                
                if not continuous:
                    break
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Anna AI Performance Monitor")
    parser.add_argument("-c", "--continuous", action="store_true", help="Run continuously")
    parser.add_argument("-i", "--interval", type=int, default=5, help="Update interval (seconds)")
    parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    metrics = monitor.collect_metrics()
    
    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        print(monitor.format_output(metrics))
    
    if args.continuous:
        try:
            while True:
                time.sleep(args.interval)
                metrics = monitor.collect_metrics()
                if args.json:
                    print(json.dumps(metrics, indent=2))
                else:
                    print(monitor.format_output(metrics))
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()
