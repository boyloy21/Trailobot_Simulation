#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty
import yaml
import os
from ament_index_python.packages import get_package_share_directory
from rcl_interfaces.msg import Parameter, ParameterValue
from rcl_interfaces.srv import SetParameters
import threading
import time

class ParamUpdateService(Node):
    def __init__(self):
        super().__init__('param_update_service')
        
        # Create service for updating parameters from web
        self.update_service = self.create_service(
            Empty, 
            'update_controller_params', 
            self.update_params_callback
        )
        
        # Client to set parameters on controller server
        self.set_params_client = self.create_client(
            SetParameters, 
            '/controller_server/set_parameters'
        )
        
        self.get_logger().info('Parameter update service started')
        
    def update_params_callback(self, request, response):
        try:
            # Load the updated parameters from web-modified YAML
            pkg_trailobot = get_package_share_directory('trailobot_description')
            web_config_path = os.path.join(pkg_trailobot, 'config', 'ControllerServer.yaml')
            
            if not os.path.exists(web_config_path):
                self.get_logger().error(f'Web config file not found: {web_config_path}')
                return response
            
            with open(web_config_path, 'r') as file:
                web_params = yaml.safe_load(file)
            
            # Update the main nav2_params.yaml with web parameters
            main_config_path = os.path.join(pkg_trailobot, 'config', 'nav2_params.yaml')
            
            if os.path.exists(main_config_path):
                with open(main_config_path, 'r') as file:
                    main_config = yaml.safe_load(file) or {}
            else:
                main_config = {}
            
            # Merge web parameters into main config
            if 'controller_server' not in main_config:
                main_config['controller_server'] = {'ros__parameters': {}}
            
            if 'ros__parameters' not in main_config['controller_server']:
                main_config['controller_server']['ros__parameters'] = {}
            
            # Update controller parameters from web config
            if 'ros__parameters' in web_params:
                main_config['controller_server']['ros__parameters'].update(
                    web_params['ros__parameters']
                )
            
            # Save updated main config
            with open(main_config_path, 'w') as file:
                yaml.dump(main_config, file, default_flow_style=False)
            
            self.get_logger().info('Main config file updated with web parameters')
            
            # Apply parameters to running controller server
            self.apply_parameters_to_controller(web_params)
            
        except Exception as e:
            self.get_logger().error(f'Failed to update parameters: {str(e)}')
        
        return response
    
    def apply_parameters_to_controller(self, web_params):
        """Apply parameters to the running controller server"""
        try:
            if 'ros__parameters' not in web_params:
                return
            
            # Wait for controller server to be available
            if not self.set_params_client.wait_for_service(timeout_sec=5.0):
                self.get_logger().warn('Controller server not available, parameters will be applied on next startup')
                return
            
            # Prepare parameter messages
            parameters = []
            for param_name, param_value in web_params['ros__parameters'].items():
                param_msg = Parameter()
                param_msg.name = param_name
                
                param_value_msg = ParameterValue()
                if isinstance(param_value, bool):
                    param_value_msg.type = ParameterValue.Type.BOOL
                    param_value_msg.bool_value = param_value
                elif isinstance(param_value, int):
                    param_value_msg.type = ParameterValue.Type.INTEGER
                    param_value_msg.integer_value = param_value
                elif isinstance(param_value, float):
                    param_value_msg.type = ParameterValue.Type.DOUBLE
                    param_value_msg.double_value = param_value
                elif isinstance(param_value, str):
                    param_value_msg.type = ParameterValue.Type.STRING
                    param_value_msg.string_value = param_value
                else:
                    self.get_logger().warn(f'Unsupported parameter type: {param_name}={param_value}')
                    continue
                
                param_msg.value = param_value_msg
                parameters.append(param_msg)
            
            # Send parameters to controller server
            set_params_request = SetParameters.Request()
            set_params_request.parameters = parameters
            
            future = self.set_params_client.call_async(set_params_request)
            
            # Use a timer to check for result
            timer = threading.Timer(2.0, self.check_set_params_result, [future])
            timer.start()
            
        except Exception as e:
            self.get_logger().error(f'Failed to apply parameters to controller: {str(e)}')
    
    def check_set_params_result(self, future):
        """Check the result of set_parameters call"""
        if future.done():
            try:
                response = future.result()
                if all(result.successful for result in response.results):
                    self.get_logger().info('Parameters applied to controller server successfully')
                else:
                    self.get_logger().error('Failed to apply some parameters to controller server')
            except Exception as e:
                self.get_logger().error(f'Error in set_parameters call: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = ParamUpdateService()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()