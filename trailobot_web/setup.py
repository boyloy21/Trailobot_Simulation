from setuptools import find_packages, setup

package_name = 'trailobot_web'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yinchheanyun',
    maintainer_email='yinchheanyun@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sensor_status = trailobot_web.status_sensor:main',
            'imu_diagnostics = trailobot_web.imu_diagnostics:main',
            'lidar_diagnostics = trailobot_web.Lidar_diagnostics:main',
            'cancel_nav = trailobot_web.CancelNavigationService:main',
        ],
    },
)
