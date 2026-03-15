import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from diagnostic_msgs.msg import DiagnosticStatus
from diagnostic_updater import Updater

class IMUDiagnostics(Node):
    def __init__(self):
        super().__init__('imu_diagnostics')

        # Create subscription
        self.sub = self.create_subscription(
            Imu, 
            'trailobot/imu', 
            self.imu_cb, 
            10
        )

        # Diagnostics updater
        self.updater = Updater(self)
        self.updater.setHardwareID("imu_sensor")
        
        # Add diagnostic task
        self.updater.add("IMU Status", self.check_imu)

        # Initialize last message time
        self.last_msg_time = self.get_clock().now()
        self.msg_received = False

    def imu_cb(self, msg):
        # Update timestamp when message is received
        self.last_msg_time = self.get_clock().now()
        self.msg_received = True
        self.get_logger().debug('Received IMU message', throttle_duration_sec=5.0)

    def check_imu(self, stat):
        if not self.msg_received:
            stat.summary(DiagnosticStatus.ERROR, "No IMU messages received yet!")
            return stat
            
        now = self.get_clock().now()
        dt = (now - self.last_msg_time).nanoseconds / 1e9  # Convert to seconds
        
        if dt < 1.0:  # Less than 1 second since last message
            stat.summary(DiagnosticStatus.OK, "IMU data OK")
        elif dt < 2.0:  # 1-2 seconds since last message
            stat.summary(DiagnosticStatus.WARN, "IMU data delayed")
            self.get_logger().warn(f"IMU messages delayed: {dt:.1f} seconds")
        else:  # More than 2 seconds since last message
            stat.summary(DiagnosticStatus.ERROR, "No IMU messages!")
            self.get_logger().error(f"No IMU messages for {dt:.1f} seconds")
        
        stat.add("Time since last message", f"{dt:.3f} seconds")
        return stat

def main(args=None):
    rclpy.init(args=args)
    node = IMUDiagnostics()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()