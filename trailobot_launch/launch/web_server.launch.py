#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    
    # Include the web server launch file
    web_bridge_server = Node(
        package='rosbridge_server',
        executable='rosbridge_websocket',
        name='rosbridge_server_node',
        output='screen',  # Optional: print node output to the console
        parameters=[
            {'port': 9090},  # The default port for rosbridge
            {'address': '0.0.0.0'} # Listen on all network interfaces for external connections
        ]
    )

    
    web_video_server = Node(
        package='web_video_server',
        executable='web_video_server',
        name='web_video_server_node',
        output='screen',  # Optional: print node output to the console
        parameters=[
            {'port': 8081},  # Change the port as needed
            {'address': '0.0.0.0'}  # Listen on all network interfaces
            # {'server_threads': 4}  # Set the number of server threads
        ]
    )

   
    
    return LaunchDescription([
        web_bridge_server,
        web_video_server
    ])