#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
from nav2_msgs.srv import ClearEntireCostmap, LoadMap
from action_msgs.msg import GoalInfo
from unique_identifier_msgs.msg import UUID
from action_msgs.srv import CancelGoal
from lifecycle_msgs.srv import GetState, ChangeState
from lifecycle_msgs.msg import Transition
import time


class SimpleCancelNavigation(Node):
    def __init__(self):
        super().__init__('simple_cancel_navigation')

        # Costmap clear clients
        self.clear_global_client = self.create_client(
            ClearEntireCostmap,
            '/global_costmap/clear_entirely_global_costmap'
        )
        self.clear_local_client = self.create_client(
            ClearEntireCostmap,
            '/local_costmap/clear_entirely_local_costmap'
        )

        # Navigation lifecycle clients
        self.navigator_get_state_client = self.create_client(
            GetState,
            '/navigate_to_pose/_action/get_state'
        )
        self.navigator_change_state_client = self.create_client(
            ChangeState,
            '/navigate_to_pose/_action/change_state'
        )
        
        # BT Navigator lifecycle clients
        self.bt_get_state_client = self.create_client(
            GetState,
            '/bt_navigator/get_state'
        )
        self.bt_change_state_client = self.create_client(
            ChangeState,
            '/bt_navigator/change_state'
        )

        # CancelGoal service clients
        self.cancel_clients = {}
        self.setup_cancel_clients()

        # Wait for services to be ready
        self.get_logger().info("Waiting for services...")
        self.wait_for_services()

        # Expose /clear_navigation service
        self.service = self.create_service(
            Empty,
            '/clear_navigation',
            self.clear_callback
        )

        self.get_logger().info('Simple Cancel Navigation Service Ready')

    def setup_cancel_clients(self):
        """Setup multiple possible cancel service clients"""
        cancel_service_paths = [
            '/navigate_to_pose/_action/cancel_goal',
            '/navigate_to_pose/cancel_goal',
            '/bt_navigator/cancel_goal',
            '/follow_waypoints/cancel_goal',
            '/navigate_through_poses/cancel_goal'
        ]
        
        for path in cancel_service_paths:
            self.cancel_clients[path] = self.create_client(CancelGoal, path)

    def wait_for_services(self):
        """Wait for all required services"""
        # Wait for cancel services
        self.active_cancel_client = None
        for path, client in self.cancel_clients.items():
            if client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f"Found cancel service: {path}")
                self.active_cancel_client = client
                break
        
        if not self.active_cancel_client:
            self.get_logger().warn("No cancel goal service found!")

        # Wait for costmap services
        for client, name in [
            (self.clear_global_client, 'global costmap'),
            (self.clear_local_client, 'local costmap')
        ]:
            if not client.wait_for_service(timeout_sec=2.0):
                self.get_logger().warn(f"{name} service not available")

    def reset_navigation_nodes(self):
        """Reset navigation nodes to ensure they can accept new goals"""
        try:
            # Try to reset BT Navigator if it exists
            if self.bt_get_state_client.service_is_ready():
                future = self.bt_get_state_client.call_async(GetState.Request())
                rclpy.spin_until_future_complete(self, future, timeout_sec=1.0)
                
                if future.done():
                    state = future.result().current_state
                    self.get_logger().info(f"BT Navigator state: {state.id}")
                    
                    # If not active, try to activate
                    if state.id != 3:  # 3 is ACTIVE state
                        change_req = ChangeState.Request()
                        change_req.transition.id = Transition.TRANSITION_ACTIVATE
                        future_change = self.bt_change_state_client.call_async(change_req)
                        rclpy.spin_until_future_complete(self, future_change, timeout_sec=1.0)
                        self.get_logger().info("Attempted to activate BT Navigator")
        except Exception as e:
            self.get_logger().warn(f"Failed to reset navigation nodes: {e}")

    def clear_callback(self, request, response):
        self.get_logger().info('Cancelling navigation and clearing costmaps...')

        success = True

        # 1. Cancel all active goals
        if self.active_cancel_client and self.active_cancel_client.service_is_ready():
            try:
                cancel_req = CancelGoal.Request()
                future = self.active_cancel_client.call_async(cancel_req)
                
                # Wait for cancel to complete
                start_time = time.time()
                while not future.done() and (time.time() - start_time) < 2.0:
                    rclpy.spin_once(self, timeout_sec=0.1)
                
                if future.done():
                    result = future.result()
                    self.get_logger().info('Cancel goal request completed')
                else:
                    self.get_logger().warn('Cancel goal request timed out')
                    
            except Exception as e:
                self.get_logger().error(f'Failed to cancel goal: {e}')
                success = False
        else:
            self.get_logger().warn('Cancel service not available')
            success = False

        # 2. Clear costmaps
        try:
            if self.clear_global_client.service_is_ready():
                future_global = self.clear_global_client.call_async(ClearEntireCostmap.Request())
                self.get_logger().info('Clearing global costmap...')
            else:
                self.get_logger().warn('Global costmap service not ready')

            if self.clear_local_client.service_is_ready():
                future_local = self.clear_local_client.call_async(ClearEntireCostmap.Request())
                self.get_logger().info('Clearing local costmap...')
            else:
                self.get_logger().warn('Local costmap service not ready')
                
        except Exception as e:
            self.get_logger().error(f'Failed to clear costmaps: {e}')
            success = False

        # 3. Reset navigation nodes to ensure they can accept new goals
        time.sleep(0.5)  # Brief delay before reset
        self.reset_navigation_nodes()

        if success:
            self.get_logger().info('Navigation cleared successfully - ready for new commands')
        else:
            self.get_logger().warn('Navigation clear completed with warnings')

        return response


def main(args=None):
    rclpy.init(args=args)
    node = SimpleCancelNavigation()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()