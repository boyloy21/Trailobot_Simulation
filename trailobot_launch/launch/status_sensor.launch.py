#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    
    
    # Status sensor node
    status_sensor_node = Node(
        package='trailobot_web',
        executable='sensor_status',
        name='status_sensor',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    imu_diagnostics_node = Node(
        package='trailobot_web',
        executable='imu_diagnostics',
        name='imu_diagnostics',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    lidar_diagnostics_node = Node(
        package='trailobot_web',
        executable='lidar_diagnostics',
        name='lidar_diagnostics',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use simulation (Gazebo) clock if true'
        ),
        status_sensor_node,
        imu_diagnostics_node,
        lidar_diagnostics_node
    ])
    
    