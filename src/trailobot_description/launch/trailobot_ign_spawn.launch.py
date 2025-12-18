#!/usr/bin/env python3

import os
import xacro
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_path = get_package_share_directory('trailobot_description')
    position_x = LaunchConfiguration('position_x', default='0.0')
    position_y = LaunchConfiguration('position_y', default='0.0')
    orientation_yaw = LaunchConfiguration('orientation_yaw', default='0.0')
    bridge_config_path = os.path.join(pkg_path, 'config', 'bridge_config.yaml')
    

    xacro_file = os.path.join(pkg_path, 'urdf', 'robot.xacro')
    robot_description = xacro.process_file(
        xacro_file, 
        mappings={
            'GAZEBO': 'true' ,  # Enable Gazebo-specific configurations
            "wheel_odom_topic": "odom"
        }
    ).toxml()
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {
                'robot_description': robot_description,
                'use_sim_time': True,
                'publish_frequency': 50.0,
                'ignore_timestamp': True
            }
        ],
        output='screen'
    )
    
    
    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            "-topic", "/robot_description",
            "-name", "trailobot",
            "allow_renaming", "true",
            "-x", position_x,
            "-y", position_y,
            "-z", "0.1",
            "-Y", orientation_yaw,
        ]
    )
    
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        parameters=[{
            'config_file': bridge_config_path,
            'container_name': 'ros_gz_bridge_container'
        }]
    )
    
    transform_publisher = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments= ["--x", "0.0",
                    "--y", "0.0",
                    "--z", "0.1",
                    "--Y", "0.0",
                    "--frame-id", "camera_link",
                    "--child-frame-id", "trailobot/base_footprint/camera_link"]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('position_x', default_value='0.0', description='X position of the robot'),
        DeclareLaunchArgument('position_y', default_value='0.0', description='Y position of the robot'),
        DeclareLaunchArgument('orientation_yaw', default_value='0.0', description='Yaw orientation of the robot'),
        robot_state_publisher,
        gz_spawn_entity,
        bridge_node,
        transform_publisher
    ])