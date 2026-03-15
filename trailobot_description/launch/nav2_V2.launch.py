import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_trailobot = get_package_share_directory('trailobot_description')
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    autostart = LaunchConfiguration('autostart', default='true')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    declare_autostart = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically start the nav2 stack'
    )
    
    # Common remappings
    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]
    
    # Controller Server with separate parameter file
    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[
            os.path.join(pkg_trailobot, 'config', 'ControllerServer.yaml'),
            {'use_sim_time': use_sim_time}
        ],
        # remappings=remappings + [('cmd_vel', 'cmd_vel_nav')]
    )
    
    # Other navigation nodes with main parameter file
    planner_server_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[
            os.path.join(pkg_trailobot, 'config', 'nav2_params2.yaml'),
            {'use_sim_time': use_sim_time}
        ],
        # remappings=remappings
    )
    
    behavior_server_node = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[
            os.path.join(pkg_trailobot, 'config', 'nav2_params2.yaml'),
            {'use_sim_time': use_sim_time}
        ],
        # remappings=remappings + [('cmd_vel', 'cmd_vel_nav')]
    )
    
    bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[
            os.path.join(pkg_trailobot, 'config', 'nav2_params2.yaml'),
            {'use_sim_time': use_sim_time}
        ],
        # remappings=remappings
    )
    
    # AMCL with its own parameter file
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            os.path.join(pkg_trailobot, 'config', 'amcl_params.yaml'),
            {'use_sim_time': use_sim_time}
        ],
        # remappings=[('scan', '/trailobot/scan')] + remappings
    )
    
    # Map server
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            {'yaml_filename': os.path.join(pkg_trailobot, 'map', 'map_edit.yaml')},
            {'use_sim_time': use_sim_time}
        ]
    )
    
    # Other nodes (add as needed)
    smoother_server_node = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[
            os.path.join(pkg_trailobot, 'config', 'nav2_params2.yaml'),
            {'use_sim_time': use_sim_time}
        ],
        # remappings=remappings
    )
    
    # Static transform publisher
    static_transform_publisher_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )
    
    # Remapper node
    remapper_node = Node(
        package='trailobot_description',
        executable='remapper.py',
        name='remapper',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    
    # Joint state publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': use_sim_time}],
    )
    
    # Lifecycle manager for navigation nodes
    nav_lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': autostart},
            {'node_names': [
                'controller_server',
                'planner_server',
                'behavior_server',
                'bt_navigator',
                'smoother_server'
            ]}
        ]
    )
    
    # Lifecycle manager for localization nodes
    loc_lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': autostart},
            {'node_names': ['map_server', 'amcl']}
        ]
    )
    
    ld = LaunchDescription()
    
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_autostart)
    ld.add_action(joint_state_publisher)
    ld.add_action(static_transform_publisher_node)
    ld.add_action(remapper_node)
    ld.add_action(map_server_node)
    ld.add_action(amcl_node)
    ld.add_action(controller_server_node)
    ld.add_action(planner_server_node)
    ld.add_action(behavior_server_node)
    ld.add_action(bt_navigator_node)
    ld.add_action(smoother_server_node)
    ld.add_action(loc_lifecycle_manager)
    ld.add_action(nav_lifecycle_manager)

    return ld