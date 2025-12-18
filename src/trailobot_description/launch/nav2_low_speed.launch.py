import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_trailobot = get_package_share_directory('trailobot_description')
    
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    autostart = LaunchConfiguration('autostart', default='true')
    map_yaml_file = LaunchConfiguration('map', default=os.path.join(pkg_trailobot, 'map', 'map_edit.yaml'))
    params_file = LaunchConfiguration('params_file', default=os.path.join(pkg_trailobot, 'config', 'nav2_param_normal_speed.yaml'))
    amcl_params_file = LaunchConfiguration('amcl_params_file', default=os.path.join(pkg_trailobot, 'config', 'amcl_params.yaml'))
    
    # Launch arguments
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
    
    declare_map_yaml = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_trailobot, 'map', 'map_edit.yaml'),
        description='Full path to map yaml file to load'
    )
    
    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_trailobot, 'config', 'nav2_param_normal_speed.yaml'),
        description='Full path to the ROS2 parameters file to use for all launched nodes'
    )
    
    declare_amcl_params_file = DeclareLaunchArgument(
        'amcl_params_file',
        default_value=os.path.join(pkg_trailobot, 'config', 'amcl_params.yaml'),
        description='Full path to the AMCL parameters file'
    )

    # Define remappings for proper topic connections
    remappings = [
        ('/cmd_vel', '/trailobot/cmd_vel'),
        ('/odom', '/trailobot/odom'),
        ('/scan', '/trailobot/scan')
    ]

    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    # Costmap nodes for dynamic obstacle detection
    local_costmap_node = Node(
        package='nav2_costmap_2d',
        executable='nav2_costmap_2d',
        name='local_costmap',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    global_costmap_node = Node(
        package='nav2_costmap_2d',
        executable='nav2_costmap_2d',
        name='global_costmap',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    planner_server_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    behavior_server_node = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    # AMCL with its own parameter file
    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    # Map server
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map_yaml_file}, {'use_sim_time': use_sim_time}]
    )
    
    smoother_server_node = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        # output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    waypoint_follower_node = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        # output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings
    )
    
    velocity_smoother_node = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        # output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        remappings=remappings + [('cmd_vel', 'cmd_vel_smoothed')]
    )
    
    # REMOVED: collision_monitor_node - not available in all distributions
    
    # Static transform publisher
    static_transform_publisher_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        # output='screen',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        parameters=[{'use_sim_time': use_sim_time}]
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
    
    # Updated lifecycle manager without recoveries_server and collision_monitor
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
                'smoother_server',
                'waypoint_follower',
                'velocity_smoother'
            ]}
        ]
    )
    
    # Localization lifecycle manager
    loc_lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'autostart': autostart},
            {'node_names': [
                'map_server', 
                'amcl'
                # 'local_costmap',
                # 'global_costmap'
            ]}
        ]
    )
    
    ld = LaunchDescription()
    
    # Add launch arguments
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_autostart)
    ld.add_action(declare_map_yaml)
    ld.add_action(declare_params_file)
    ld.add_action(declare_amcl_params_file)

    # Add nodes in proper order
    ld.add_action(static_transform_publisher_node)
    ld.add_action(joint_state_publisher)
    ld.add_action(remapper_node)
    
    # Localization nodes
    ld.add_action(map_server_node)
    ld.add_action(amcl_node)
    ld.add_action(local_costmap_node)
    ld.add_action(global_costmap_node)
    
    # Navigation nodes  
    ld.add_action(controller_server_node)
    ld.add_action(planner_server_node)
    ld.add_action(behavior_server_node)
    ld.add_action(bt_navigator_node)
    ld.add_action(smoother_server_node)
    ld.add_action(waypoint_follower_node)
    ld.add_action(velocity_smoother_node)
    
    # Lifecycle managers
    ld.add_action(loc_lifecycle_manager)
    ld.add_action(nav_lifecycle_manager)

    return ld