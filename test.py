"""Run test cases for the resource usage detection module."""

from tests.resource_usage import run_detection_tests
from tests.resource_usage_server import run_detection_tests as run_detection_tests_server
# from tests.resource_usage_joint import run_detection_tests as run_detection_tests_joint

if __name__ == "__main__":
    # run_detection_tests()
    run_detection_tests_server(server_ip='172.20.10.8')
