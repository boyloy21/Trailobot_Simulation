#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import AppendEnvironmentVariable
from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition

def generate_launch_description():
    
    pkg_path = get_package_share_directory('trailobot_description')
    laser_merger_pkg = get_package_share_directory('ros2_laser_scan_merger')
    laser_merger_launch = os.path.join(laser_merger_pkg, "launch", "merge_2_scan.launch.py")
    world_file = os.path.join(pkg_path, 'worlds', 'my_world.sdf')
    gz_sim_share = get_package_share_directory('ros_gz_sim')
    
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_sim_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r -v 4 {world_file}'
        }.items()
    )
    
    
    
    spawn_entity = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_path, 'launch', 'trailobot_ign_spawn.launch.py')
        )
    )
    
    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[os.path.join(pkg_path, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )
    
    laser_merger = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(laser_merger_launch)
    )
    
    # web_video_server = Node(
    #     package='web_video_server',
    #     executable='web_video_server',
    #     name='web_video_server',
    #     output='screen',
    #     parameters=[
    #         {'port': 8080},
    #         {'address': '0.0.0.0'},
    #         {'server_threads': 4}
    #     ],
    # )
    
    
    return LaunchDescription([
        AppendEnvironmentVariable(
            name='IGN_GAZEBO_RESOURCE_PATH',
            value=os.path.join(pkg_path, 'worlds')
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        ),
        gz_sim,
        spawn_entity,
        robot_localization_node,
        laser_merger,
        # web_video_server
    ])