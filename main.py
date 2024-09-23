""" Main file to run the server. """
from server.joint_detection import main as joint_detection
from local.detection import main as local_main
from server.detection import main as server_main

if __name__ == "__main__":
    joint_detection()
