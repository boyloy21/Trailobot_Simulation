import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_nav2_dir = get_package_share_directory('nav2_bringup')
    pkg_trailobot = get_package_share_directory('trailobot_description')
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    autostart = LaunchConfiguration('autostart', default='True')

    
    
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically start the slam_toolbox stack'
    )
    
    lifecycle_nodes = [
        'controller_server',
        'smoother_server',
        'planner_server',
        'behavior_server',
        'velocity_smoother',
        'collision_monitor',
        'bt_navigator',
        'waypoint_follower',
    ]

    
    nav2_launch_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'map': os.path.join(pkg_trailobot, 'map', 'my_map.yaml'),
            'params_file': os.path.join(pkg_trailobot, 'config', 'nav2_params.yaml'),
            # 'package_path': pkg_trailobot,
        }.items()
    )
    
     
    
    # rviz_launch_cmd = Node(
    #     package="rviz2",
    #     executable="rviz2",
    #     name="rviz2",
    #     arguments=[
    #         '-d' + os.path.join(
    #             get_package_share_directory('nav2_bringup'),
    #             'rviz',
    #             'nav2_default_view.rviz'
    #         )
    #     ],
    #     parameters=[{'use_sim_time': use_sim_time}]
    # )
    

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            os.path.join(pkg_trailobot, 'config', 'amcl_params.yaml'),
            {'use_sim_time': use_sim_time}
        ]
    )
    
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            {'yaml_filename': os.path.join(pkg_trailobot, 'map', 'my_map.yaml')},
            {'use_sim_time': use_sim_time}
        ], #my_map.yaml
    )
    
    static_transform_publisher_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        parameters=[{'use_sim_time': use_sim_time}],

    )
    
    remapper_node = Node(
        package='trailobot_description',
        executable='remapper.py',
        name='remapper',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    
    lifecycle_manager = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time},
                        {'autostart': autostart},
                        {'node_names': lifecycle_nodes}]
    )
    
    
    # param_update_service = Node(
    #     package='trailobot_description',
    #     executable='param_update_service.py',
    #     name='param_update_service',
    #     output='screen',
    # )

    
    ld = LaunchDescription()
    
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_autostart)
    ld.add_action(joint_state_publisher)
    ld.add_action(nav2_launch_cmd)
    # ld.add_action(rviz_launch_cmd)
    ld.add_action(amcl_node)
    ld.add_action(map_server_node)
    ld.add_action(lifecycle_manager)
    ld.add_action(static_transform_publisher_node)
    ld.add_action(remapper_node)
    # ld.add_action(param_update_service)

    return ld