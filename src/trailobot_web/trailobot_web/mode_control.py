#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from std_msgs.msg import String

class AutoModeController(Node):
    def __init__(self):
        super().__init__('auto_mode_controller')

        # Publishers
        self.initialpose_pub = self.create_publisher(
            PoseWithCovarianceStamped, '/initialpose', 10
        )
        self.goal_pub = self.create_publisher(PoseStamped, '/goal_pose', 10)
        self.waypoint_pub = self.create_publisher(String, '/waypoint_follower/transition_event', 10)

        # Subscribe to a mode command if you still want reactive mode switching
        self.create_subscription(String, '/robot_mode', self.mode_callback, 10)

        # Example waypoint list
        self.waypoints = [
            {'x': 1.0, 'y': 1.0, 'theta': 0.0},
            {'x': 2.0, 'y': 1.5, 'theta': 0.0},
            {'x': 0.5, 'y': 2.0, 'theta': 0.0},
        ]
        self.current_waypoint = 0

        self.get_logger().info("AutoModeController started")

    def mode_callback(self, msg: String):
        mode = msg.data.lower()
        self.get_logger().info(f"Switching to mode: {mode}")

        if mode == 'relocate':
            self.send_initialpose(0.0, 0.0, 0.0)
        elif mode == 'navigation':
            self.send_goal(1.0, 1.0, 0.0)  # example goal
        elif mode == 'waypoint':
            self.start_waypoints()

    def send_initialpose(self, x, y, theta):
        pose = PoseWithCovarianceStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x = x
        pose.pose.pose.position.y = y
        pose.pose.pose.position.z = 0.0
        # Simple orientation as yaw
        import math
        from tf_transformations import quaternion_from_euler
        q = quaternion_from_euler(0, 0, theta)
        pose.pose.pose.orientation.x = q[0]
        pose.pose.pose.orientation.y = q[1]
        pose.pose.pose.orientation.z = q[2]
        pose.pose.pose.orientation.w = q[3]
        self.initialpose_pub.publish(pose)
        self.get_logger().info(f"Relocate pose sent: x={x}, y={y}, theta={theta}")

    def send_goal(self, x, y, theta):
        goal = PoseStamped()
        goal.header.stamp = self.get_clock().now().to_msg()
        goal.header.frame_id = 'map'
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = 0.0
        import math
        from tf_transformations import quaternion_from_euler
        q = quaternion_from_euler(0, 0, theta)
        goal.pose.orientation.x = q[0]
        goal.pose.orientation.y = q[1]
        goal.pose.orientation.z = q[2]
        goal.pose.orientation.w = q[3]
        self.goal_pub.publish(goal)
        self.get_logger().info(f"Navigation goal sent: x={x}, y={y}, theta={theta}")

    def start_waypoints(self):
        if self.current_waypoint >= len(self.waypoints):
            self.get_logger().info("All waypoints finished")
            return
        wp = self.waypoints[self.current_waypoint]
        self.send_goal(wp['x'], wp['y'], wp['theta'])
        self.current_waypoint += 1
        self.get_logger().info(f"Waypoint {self.current_waypoint} sent")

def main(args=None):
    rclpy.init(args=args)
    node = AutoModeController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
