#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
import numpy as np

class PS4ControlNode(Node):
    def __init__(self):
        super().__init__('ps4_control_node')
        self.joy_subscriber = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10
        )
        self.cmd_publisher = self.create_publisher(Twist, 'trailobot/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publish_cmd)   # 10 Hz
        
        # Initialize speed variables
        self.Vx = 0.0
        self.Vy = 0.0
        self.Omega = 0.0
        
        # Initial Increase and decrease values
        self.Speed_linear = 0.6
        self.Speed_angular = 1.0
        self.increase_linear = 0.0
        self.increase_angular = 0.0
        self.descrease_linear = 0.0
        self.descrease_angular = 0.0
        
        # Speed limits
        self.limit_linear_speed = 1.5
        self.limit_angular_speed = 2.0

    def joy_callback(self, msg):
        # Map PS4 controller buttons and axes to robot commands
        self.increase_angular = msg.buttons[5]  # R1 button
        self.descrease_angular = msg.buttons[6]  # R2 button

        self.increase_linear = msg.buttons[4]  # L1 button
        self.descrease_linear = msg.buttons[7]  # L2 button
        if self.increase_linear:
            self.Speed_linear += 0.1
        if self.descrease_linear:
            self.Speed_linear -= 0.1
        if self.increase_angular:
            self.Speed_angular += 0.1
        if self.descrease_angular:
            self.Speed_angular -= 0.1
        self.Vx = msg.axes[1]  # Left stick vertical
        self.Omega = msg.axes[3] # right stick horizontal
        
    def publish_cmd(self):
        cmd_msg = Twist()
        cmd_msg.linear.x = self.Vx * self.Speed_linear
        cmd_msg.linear.y = self.Vy * self.Speed_linear
        cmd_msg.angular.z = self.Omega * self.Speed_angular
        
        # Limit the speed
        cmd_msg.linear.x = np.clip(cmd_msg.linear.x, -self.limit_linear_speed, self.limit_linear_speed)
        cmd_msg.angular.z = np.clip(cmd_msg.angular.z, -self.limit_angular_speed, self.limit_angular_speed)
        
        self.cmd_publisher.publish(cmd_msg)
        self.get_logger().info(f'Publishing: Vx={cmd_msg.linear.x}, Vy={cmd_msg.linear.y}, Omega={cmd_msg.angular.z}')
        
def main(args=None):
    rclpy.init(args=args)
    ps4_control_node = PS4ControlNode()
    rclpy.spin(ps4_control_node)
    ps4_control_node.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()