import os
import platform
import sys
from typing import Dict, Any, List
import psutil
from utils.logger import logger

class SystemInfoProvider:
    """
    Comprehensive System & Hardware Diagnostics Provider collecting
    real-time metrics for CPU, RAM, GPU, Disks, Battery, Network, and OS build.
    """

    def get_system_metrics(self) -> Dict[str, Any]:
        """Gathers full hardware, resource usage, and Windows platform metrics."""
        
        # 1. CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()

        # 2. Memory
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # 3. Disks
        disk_partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disk_partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent_used": usage.percent
                })
            except Exception:
                continue

        # 4. Battery
        battery_data = None
        try:
            bat = psutil.sensors_battery()
            if bat:
                battery_data = {
                    "percent": bat.percent,
                    "power_plugged": bat.power_plugged,
                    "secs_left": bat.secsleft if bat.secsleft != psutil.POWER_TIME_UNLIMITED else -1
                }
        except Exception:
            battery_data = None

        # 5. Network
        net_io = psutil.net_io_counters()
        net_ifaddrs = {}
        for iface, addrs in psutil.net_if_addrs().items():
            net_ifaddrs[iface] = [
                {"address": addr.address, "family": str(addr.family)}
                for addr in addrs
            ]

        # 6. GPU
        gpu_info = self._get_gpu_details()

        # 7. OS Metadata
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }

        # 8. Temperatures (if available)
        temps = {}
        try:
            if hasattr(psutil, "sensors_temperatures"):
                st = psutil.sensors_temperatures()
                for name, entries in st.items():
                    temps[name] = [{"label": e.label or name, "current": e.current} for e in entries]
        except Exception:
            temps = {}

        return {
            "os": os_info,
            "cpu": {
                "usage_percent": cpu_percent,
                "logical_cores": cpu_count_logical,
                "physical_cores": cpu_count_physical,
                "frequency_mhz": round(cpu_freq.current, 2) if cpu_freq else 0
            },
            "ram": {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent_used": mem.percent
            },
            "swap": {
                "total_gb": round(swap.total / (1024**3), 2),
                "used_gb": round(swap.used / (1024**3), 2),
                "percent_used": swap.percent
            },
            "disks": disk_partitions,
            "battery": battery_data,
            "gpu": gpu_info,
            "network": {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "interfaces": net_ifaddrs
            },
            "temperatures": temps
        }

    def _get_gpu_details(self) -> List[Dict[str, Any]]:
        """Queries WMI or system commands for GPU hardware details."""
        gpus = []
        if sys.platform == "win32":
            try:
                import subprocess
                cmd = "wmic path win32_VideoController get Name,AdapterRAM,DriverVersion /format:csv"
                out = subprocess.check_output(cmd, shell=True, text=True, errors="ignore")
                lines = [line.strip() for line in out.strip().split("\n") if line.strip()]
                if len(lines) > 1:
                    headers = lines[0].split(",")
                    for line in lines[1:]:
                        parts = line.split(",")
                        if len(parts) >= 3:
                            gpus.append({
                                "name": parts[-2] if len(parts) >= 4 else parts[-1],
                                "driver_version": parts[1] if len(parts) >= 4 else "",
                                "type": "Dedicated/Integrated GPU"
                            })
            except Exception:
                pass
        return gpus or [{"name": "Default Graphics Accelerator", "type": "System Graphics"}]


system_info_provider = SystemInfoProvider()
