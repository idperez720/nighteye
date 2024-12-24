""" This module"""
import time
import random

def cpu_task(duration):
    """Function to simulate 20% CPU usage for a specified duration."""
    busy_time = 0.2  # 20% of the time busy
    idle_time = 0.8  # 80% of the time idle

    end_time = time.time() + duration
    while time.time() < end_time:
        # Busy loop for `busy_time`
        busy_start = time.time()
        while time.time() - busy_start < busy_time:
            pass  # Simulates CPU-intensive work

        # Idle for `idle_time`
        time.sleep(idle_time)

def random_cpu_usage():
    """Randomly generates CPU usage at 20% for random intervals."""
    print("Running... Press Ctrl+C to stop.")
    while True:
        # Random duration between 5 and 15 seconds
        duration = random.uniform(5, 15)
        print(f"Simulating 20% CPU usage for {duration:.2f} seconds...")
        cpu_task(duration)

if __name__ == "__main__":
    try:
        random_cpu_usage()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting...")