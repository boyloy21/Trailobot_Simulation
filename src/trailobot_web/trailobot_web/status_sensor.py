#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8MultiArray
from sensor_msgs.msg import Imu, LaserScan, Image


class StatusSensor(Node):
    def __init__(self):
        super().__init__("sensor_status")
        self.status_pub = self.create_publisher(Int8MultiArray, "trailobot/status_sensor", 10)

        self.create_subscription(Imu, "trailobot/imu", self.imu_callback, 10)
        self.create_subscription(LaserScan, "/scan_left", self.lidar_left_callback, 10)
        self.create_subscription(LaserScan, "/scan_right", self.lidar_right_callback, 10)
        self.create_subscription(Image, "trailobot/depth_camera_left/image", self.camera_left_callback, 10)
        self.create_subscription(Image, "trailobot/depth_camera_right/image", self.camera_right_callback, 10)

        self.last_msg_time = {k: 0.0 for k in ["imu","lidar_left","lidar_right","camera_left","camera_right"]}
        self.timer = self.create_timer(1.0, self.check_sensors)

    def imu_callback(self, msg): self.last_msg_time["imu"] = self.get_clock().now().seconds_nanoseconds()[0]
    def lidar_left_callback(self, msg): self.last_msg_time["lidar_left"] = self.get_clock().now().seconds_nanoseconds()[0]
    def lidar_right_callback(self, msg): self.last_msg_time["lidar_right"] = self.get_clock().now().seconds_nanoseconds()[0]
    def camera_left_callback(self, msg): self.last_msg_time["camera_left"] = self.get_clock().now().seconds_nanoseconds()[0]
    def camera_right_callback(self, msg): self.last_msg_time["camera_right"] = self.get_clock().now().seconds_nanoseconds()[0]

    def check_sensors(self):
        now = self.get_clock().now().seconds_nanoseconds()[0]
        timeout = 2.0
        msg = Int8MultiArray()
        msg.data = [
            int((now - self.last_msg_time["imu"]) < timeout),
            int((now - self.last_msg_time["lidar_left"]) < timeout),
            int((now - self.last_msg_time["lidar_right"]) < timeout),
            int((now - self.last_msg_time["camera_left"]) < timeout),
            int((now - self.last_msg_time["camera_right"]) < timeout),
        ]
        self.status_pub.publish(msg)
        self.get_logger().info(f"Sensor Status: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = StatusSensor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
