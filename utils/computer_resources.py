""" 
This module has functions to read the usage of resources and perform ping operations.
"""

import re
import psutil
import subprocess
from typing import Tuple, Optional


def ping(ip: str) -> Optional[float]:
    """
    Sends a single ping request to the specified IP address and returns the response time in seconds.

    Args:
        ip (str): The IP address or hostname to ping.

    Returns:
        Optional[float]: The round-trip time in seconds. Returns None if the ping fails or if the response time cannot be obtained.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        time = re.search(r'time=(\d+\.?\d*) ms', result.stdout)
        if time:
            response_time = float(time.group(1))  # Convert milliseconds to seconds
            return response_time
        else:
            print(f"No se pudo obtener el tiempo de respuesta del ping a {ip}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error haciendo ping a {ip}: {e.stderr}")
        return None


def get_system_usage() -> Tuple[float, float]:
    """
    Gets the current CPU and memory usage of the system.

    Returns:
        Tuple[float, float]: A tuple containing the CPU usage and memory usage, both expressed as values between 0 and 1.
                             The first element is the CPU usage, and the second element is the memory usage.
    """
    cpu_usage = psutil.cpu_percent(interval=1) / 100.0
    memory = psutil.virtual_memory()
    memory_usage = memory.percent / 100.0
    
    return cpu_usage, memory_usage