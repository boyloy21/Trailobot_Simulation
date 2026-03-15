#! /usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from diagnostic_msgs.msg import DiagnosticStatus
from diagnostic_updater import Updater


class LidarDiagnostics(Node):
    def __init__(self):
        super().__init__('lidar_diagnostics')

        # Initialize last message times and received flags
        self.last_msg_time_FR = self.get_clock().now()
        self.last_msg_time_BL = self.get_clock().now()
        self.msg_received_FR = False
        self.msg_received_BL = False
        
        # Create Subscription Lidar left and right
        self.lidarFR_sub = self.create_subscription(LaserScan, '/scan_left', self.lidarFR_cb, 10)
        self.lidarBL_sub = self.create_subscription(LaserScan, '/scan_right', self.lidarBL_cb, 10)
        
        # Diagnostics updater
        self.updater = Updater(self)
        self.updater.setHardwareID("lidar_sensor")

        # Add diagnostic tasks
        self.updater.add("Lidar Front Right Status", self.check_lidarFR)
        self.updater.add("Lidar Back Left Status", self.check_lidarBL)
        
    def lidarFR_cb(self, msg):
        self.last_msg_time_FR = self.get_clock().now()
        self.msg_received_FR = True
        self.get_logger().debug('Received Lidar FR message', throttle_duration_sec=5.0)

    def lidarBL_cb(self, msg):
        self.last_msg_time_BL = self.get_clock().now()
        self.msg_received_BL = True
        self.get_logger().debug('Received Lidar BL message', throttle_duration_sec=5.0)

    def check_lidarFR(self, stat):
        """Check status of the Lidar Front Right"""
        if not self.msg_received_FR:
            stat.summary(DiagnosticStatus.ERROR, "No Lidar FR messages received yet!")
            return stat
            
        now = self.get_clock().now()
        dt = (now - self.last_msg_time_FR).nanoseconds / 1e9
        
        if dt < 1.0:
            stat.summary(DiagnosticStatus.OK, "Lidar FR data OK")
        elif dt < 2.0:
            stat.summary(DiagnosticStatus.WARN, "Lidar FR data delayed")
            self.get_logger().warn(f"Lidar FR messages delayed: {dt:.1f} seconds")
        else:
            stat.summary(DiagnosticStatus.ERROR, "No Lidar FR messages!")
            self.get_logger().error(f"No Lidar FR messages for {dt:.1f} seconds")
        
        stat.add("Time since last message", f"{dt:.3f} seconds")
        return stat
    
    def check_lidarBL(self, stat):
        """Check status of the Lidar Back Left"""
        if not self.msg_received_BL:
            stat.summary(DiagnosticStatus.ERROR, "No Lidar BL messages received yet!")
            return stat
            
        now = self.get_clock().now()
        dt = (now - self.last_msg_time_BL).nanoseconds / 1e9
        
        if dt < 1.0:
            stat.summary(DiagnosticStatus.OK, "Lidar BL data OK")
        elif dt < 2.0:
            stat.summary(DiagnosticStatus.WARN, "Lidar BL data delayed")
            self.get_logger().warn(f"Lidar BL messages delayed: {dt:.1f} seconds")
        else:
            stat.summary(DiagnosticStatus.ERROR, "No Lidar BL messages!")
            self.get_logger().error(f"No Lidar BL messages for {dt:.1f} seconds")
        
        stat.add("Time since last message", f"{dt:.3f} seconds")
        return stat
            
def main(args=None):
    rclpy.init(args=args)
    node = LidarDiagnostics()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()