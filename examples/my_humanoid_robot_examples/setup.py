from setuptools import setup

package_name = 'my_humanoid_robot_examples'

setup(
    name=package_name,
    version='0.0.1',
    packages=[],
    py_modules=[
        'my_humanoid_robot_examples.basic_controller',
        'my_humanoid_robot_examples.ai_controller',
        'my_humanoid_robot_examples.urdf_publisher'
    ],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/my_humanoid_robot_examples']),
        ('share/my_humanoid_robot_examples', ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Example Maintainer',
    maintainer_email='example@todo.todo',
    description='Example packages for humanoid robot with ROS2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'basic_controller = my_humanoid_robot_examples.basic_controller:main',
            'ai_controller = my_humanoid_robot_examples.ai_controller:main',
            'urdf_publisher = my_humanoid_robot_examples.urdf_publisher:main',
        ],
    },
)