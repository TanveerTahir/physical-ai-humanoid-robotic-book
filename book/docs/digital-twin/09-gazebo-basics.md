---
title: Gazebo Basics
sidebar_position: 1
description: Understanding the fundamentals of Gazebo simulation environment for robotics
gpu_notes: This chapter requires GPU for Gazebo simulation; minimum 4GB VRAM recommended for graphics rendering
jetson_notes: Jetson AGX Xavier recommended for Gazebo simulation; Jetson Nano can run basic simulations only
---

# Gazebo Basics

## Prerequisites

Before studying this chapter, you should have:
- Understanding of robotics fundamentals and kinematics (from Chapter 1)
- Knowledge of ROS2 concepts and communication patterns (from Chapter 5)
- Basic understanding of URDF models (from Chapter 8)
- Familiarity with 3D visualization concepts
- Experience with Linux command line

## Learning Objectives

By the end of this chapter, you should be able to:
- Understand the architecture and components of the Gazebo simulation environment
- Create basic simulation worlds with physics properties
- Spawn and control robots in Gazebo using ROS2 interfaces
- Configure sensors and actuators for simulation
- Implement basic robot simulation scenarios

## Introduction

Gazebo is a powerful 3D simulation environment that plays a critical role in the development and testing of humanoid robots. It provides realistic physics simulation, high-quality graphics, and convenient programmatic interfaces that make it an essential tool in the robotics development pipeline.

For humanoid robots, Gazebo serves as a safe and cost-effective environment to test complex behaviors, validate control algorithms, and develop perception systems before deploying on real hardware. The ability to simulate complex interactions between the robot and its environment is crucial for developing robust humanoid capabilities.

## Gazebo Architecture

Gazebo's architecture is built around a client-server model with multiple components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gazebo GUI   │◄──►│  Gazebo Server  │◄──►│   Plugins       │
│   (gzclient)   │    │   (gzserver)    │    │ (libgazebo.so)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────── INTERFACE ──────────────────────────┐
         ▲                       ▲                       ▲
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    ROS2         │◄──►│   SDFormat      │◄──►│   Physics       │
│   Interface     │    │   Models        │    │   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

1. **Gazebo Server (gzserver)**: Runs the physics simulation and handles all simulation logic
2. **Gazebo Client (gzclient)**: Provides the graphical user interface for visualization
3. **SDFormat**: Simulation Description Format for defining worlds, models, and physics properties
4. **Physics Engine**: Underlying physics simulation (ODE, Bullet, Simbody)
5. **Plugins System**: Extensible architecture for custom simulation behaviors

## Setting Up Gazebo with ROS2

### Installation

For Ubuntu with ROS2 Humble:
```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-dev
sudo apt install gazebo libgazebo-dev
```

### Basic Launch

To start Gazebo with ROS2 interface:
```bash
# Launch empty world
ros2 launch gazebo_ros empty_world.launch.py

# Launch with GUI
ros2 launch gazebo_ros gzserver.launch.py gui:=true
```

## Creating Basic Worlds

Gazebo worlds are defined using SDFormat (Simulation Description Format) XML files:

**basic_world.sdf:**
```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="basic_world">
    <!-- Physics engine -->
    <physics name="1ms" type="ode">
      <gravity>0 0 -9.8</gravity>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Sun light -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- A simple box obstacle -->
    <model name="box_obstacle">
      <pose>2 0 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.2 0.2 1</ambient>
            <diffuse>0.8 0.2 0.2 1</diffuse>
          </material>
        </visual>
        <inertial>
          <mass>1.0</mass>
          <inertia>
            <ixx>0.166667</ixx>
            <ixy>0</ixy>
            <ixz>0</ixz>
            <iyy>0.166667</iyy>
            <iyz>0</iyz>
            <izz>0.166667</izz>
          </inertia>
        </inertial>
      </link>
    </model>
  </world>
</sdf>
```

### Launching Custom Worlds

To launch your custom world:
```bash
# Launch custom world
gz sim -r basic_world.sdf

# Or with ROS2 launch file
ros2 launch gazebo_ros gzserver.launch.py world:=/path/to/basic_world.sdf
```

## Spawning Robots in Gazebo

### Using ROS2 Services

Robots can be spawned programmatically using ROS2 services:

```python
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Pose
import time

class RobotSpawner(Node):
    def __init__(self):
        super().__init__('robot_spawner')

        # Create client for spawn service
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')

        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Spawn service not available, waiting again...')

        # Timer to spawn robot after service is ready
        self.spawn_timer = self.create_timer(1.0, self.spawn_robot)

    def spawn_robot(self):
        """Spawn robot in Gazebo"""
        request = SpawnEntity.Request()

        # Load robot model from URDF file
        with open('/path/to/robot.urdf', 'r') as f:
            request.xml = f.read()

        # Set robot name
        request.name = 'my_robot'

        # Set initial pose
        request.initial_pose.position.x = 0.0
        request.initial_pose.position.y = 0.0
        request.initial_pose.position.z = 1.0  # Start 1m above ground
        request.initial_pose.orientation.x = 0.0
        request.initial_pose.orientation.y = 0.0
        request.initial_pose.orientation.z = 0.0
        request.initial_pose.orientation.w = 1.0

        # Call spawn service
        future = self.spawn_client.call_async(request)
        future.add_done_callback(self.spawn_response_callback)

    def spawn_response_callback(self, future):
        """Handle spawn response"""
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Successfully spawned {response.status_message}')
            else:
                self.get_logger().error(f'Failed to spawn: {response.status_message}')
        except Exception as e:
            self.get_logger().error(f'Spawn service call failed: {e}')

def main(args=None):
    rclpy.init(args=args)
    spawner = RobotSpawner()

    try:
        rclpy.spin(spawner)
    except KeyboardInterrupt:
        spawner.get_logger().info('Shutting down robot spawner...')
    finally:
        spawner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Using Command Line Tools

Alternatively, robots can be spawned using command line tools:
```bash
# Spawn robot from URDF file
ros2 run gazebo_ros spawn_entity.py -entity my_robot -file /path/to/robot.urdf -x 0 -y 0 -z 1

# Spawn with custom parameters
ros2 run gazebo_ros spawn_entity.py -entity my_robot -topic robot_description -x 1 -y 1 -z 0.5
```

## Robot Control in Gazebo

### Joint State Publisher

Gazebo publishes joint states through the `/joint_states` topic:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

class JointStateMonitor(Node):
    def __init__(self):
        super().__init__('joint_state_monitor')

        # Subscribe to joint states from Gazebo
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        # Publisher for joint commands (if needed)
        self.joint_cmd_pub = self.create_publisher(
            JointState,
            '/joint_commands',
            10
        )

    def joint_state_callback(self, msg):
        """Process joint state messages from Gazebo"""
        self.get_logger().info(f'Received {len(msg.name)} joints:')

        for i, name in enumerate(msg.name):
            if i < len(msg.position) and i < len(msg.velocity) and i < len(msg.effort):
                pos = msg.position[i] if i < len(msg.position) else 0.0
                vel = msg.velocity[i] if i < len(msg.velocity) else 0.0
                eff = msg.effort[i] if i < len(msg.effort) else 0.0

                self.get_logger().info(f'  {name}: pos={pos:.3f}, vel={vel:.3f}, eff={eff:.3f}')

def main(args=None):
    rclpy.init(args=args)
    monitor = JointStateMonitor()

    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        monitor.get_logger().info('Shutting down joint state monitor...')
    finally:
        monitor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Velocity Control

For differential drive robots, velocity commands can be sent through the `/cmd_vel` topic:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')

        # Publisher for velocity commands
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Publisher for joint position commands (for articulated robots)
        self.joint_cmd_pub = self.create_publisher(Float64MultiArray, '/joint_group_position_controller/commands', 10)

        # Timer for control loop
        self.control_timer = self.create_timer(0.1, self.control_loop)  # 10Hz

        self.step = 0

    def control_loop(self):
        """Main control loop"""
        # Send velocity command
        cmd = Twist()
        cmd.linear.x = 0.5  # Move forward at 0.5 m/s
        cmd.angular.z = 0.2 * (self.step % 50 > 25)  # Turn occasionally

        self.cmd_vel_pub.publish(cmd)

        # Send joint position commands (example for articulated robot)
        joint_cmd = Float64MultiArray()
        joint_cmd.data = [0.1 * (self.step % 100) for _ in range(6)]  # Oscillate joints
        self.joint_cmd_pub.publish(joint_cmd)

        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    controller = RobotController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Shutting down robot controller...')
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Sensors in Gazebo

Gazebo provides various sensor plugins that simulate real-world sensors:

### Camera Sensor

**Camera in URDF/SDF:**
```xml
<sensor name="camera" type="camera">
  <camera>
    <horizontal_fov>1.047</horizontal_fov>
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>
    </image>
    <clip>
      <near>0.1</near>
      <far>100</far>
    </clip>
  </camera>
  <always_on>true</always_on>
  <update_rate>30</update_rate>
  <visualize>true</visualize>
</sensor>
```

### Laser Range Finder

**Lidar in URDF/SDF:**
```xml
<sensor name="lidar" type="ray">
  <ray>
    <scan>
      <horizontal>
        <samples>360</samples>
        <resolution>1</resolution>
        <min_angle>-3.14159</min_angle>
        <max_angle>3.14159</max_angle>
      </horizontal>
    </scan>
    <range>
      <min>0.1</min>
      <max>10.0</max>
      <resolution>0.01</resolution>
    </range>
  </ray>
  <always_on>true</always_on>
  <update_rate>10</update_rate>
  <visualize>true</visualize>
</sensor>
```

### Processing Sensor Data

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan, CameraInfo
from cv_bridge import CvBridge
import numpy as np

class SensorProcessor(Node):
    def __init__(self):
        super().__init__('sensor_processor')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Subscribe to camera data
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Subscribe to lidar data
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            10
        )

        # Publishers for processed data
        self.processed_img_pub = self.create_publisher(Image, '/processed_image', 10)

    def image_callback(self, msg):
        """Process camera image from Gazebo"""
        try:
            # Convert ROS image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Process image (example: simple edge detection)
            processed = cv2.Canny(cv_image, 50, 150)

            # Convert back to ROS format and publish
            processed_msg = self.bridge.cv2_to_imgmsg(processed, "mono8")
            processed_msg.header = msg.header
            self.processed_img_pub.publish(processed_msg)

        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def laser_callback(self, msg):
        """Process lidar scan from Gazebo"""
        # Convert to numpy array
        ranges = np.array(msg.ranges)

        # Handle invalid ranges
        ranges[np.isnan(ranges)] = msg.range_max
        ranges[np.isinf(ranges)] = msg.range_max

        # Find nearest obstacle
        min_range = np.min(ranges)
        min_idx = np.argmin(ranges)

        # Convert angle index to actual angle
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        obstacle_angle = angle_min + min_idx * angle_increment

        self.get_logger().info(f'Nearest obstacle: {min_range:.2f}m at {obstacle_angle:.2f}rad')

def main(args=None):
    rclpy.init(args=args)
    processor = SensorProcessor()

    try:
        rclpy.spin(processor)
    except KeyboardInterrupt:
        processor.get_logger().info('Shutting down sensor processor...')
    finally:
        processor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Physics Configuration

Proper physics configuration is crucial for realistic simulation:

### Material Properties

**In SDFormat:**
```xml
<material name="rubber_wheel">
  <pbr>
    <metal>
      <albedo_map>materials/textures/rubber.png</albedo_map>
      <roughness_map>materials/textures/rubber_roughness.png</roughness_map>
      <metalness_map>materials/textures/rubber_metalness.png</metalness_map>
    </metal>
  </pbr>
</material>
```

### Contact Properties

**Friction and damping:**
```xml
<collision name="wheel_collision">
  <surface>
    <friction>
      <ode>
        <mu>1.0</mu>  <!-- Coefficient of friction -->
        <mu2>1.0</mu2>
        <fdir1>0 0 1</fdir1>
        <slip1>0</slip1>
        <slip2>0</slip2>
      </ode>
    </friction>
    <bounce>
      <restitution_coefficient>0.1</restitution_coefficient>
      <threshold>100000</threshold>
    </bounce>
    <contact>
      <ode>
        <soft_cfm>0</soft_cfm>
        <soft_erp>0.2</soft_erp>
        <kp>1e+13</kp>
        <kd>1</kd>
        <max_vel>0.01</max_vel>
        <min_depth>0</min_depth>
      </ode>
    </contact>
  </surface>
</collision>
```

## Best Practices for Gazebo Simulation

### Performance Optimization

1. **Reduce Update Rates**: Use appropriate update rates for different sensors
2. **Simplify Models**: Use simplified collision geometries for better performance
3. **Limit Physics Steps**: Balance accuracy with performance
4. **Use Appropriate Meshes**: Optimize mesh complexity for visualization

### Accuracy Considerations

1. **Realistic Physics Properties**: Use materials and friction coefficients that match reality
2. **Sensor Noise**: Add realistic noise models to sensor outputs
3. **Time Synchronization**: Ensure proper timing between simulation and control loops
4. **Validation**: Compare simulation results with real-world data when possible

## Hands-on Lab: Basic Robot Simulation

Let's create a simple differential drive robot simulation:

**Create a launch file:**
```python
# launch/basic_robot_simulation.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # World file argument
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty_world.sdf',
        description='Choose one of the world files from `/gazebo_ros/worlds`'
    )

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzserver.launch.py'
            ])
        ]),
        launch_arguments={
            'world': PathJoinSubstitution([
                FindPackageShare('my_robot_description'),
                'worlds',
                'basic_world.sdf'
            ])
        }.items()
    )

    # Launch Gazebo client
    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gzclient.launch.py'
            ])
        ])
    )

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True
        }]
    )

    # Joint state publisher
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True
        }]
    )

    return LaunchDescription([
        world_arg,
        gazebo,
        gazebo_client,
        robot_state_publisher,
        joint_state_publisher
    ])
```

## Evaluation Checkpoints

1. What are the main components of the Gazebo architecture?
2. How do you spawn a robot model in Gazebo programmatically?
3. What are the key physics parameters that affect simulation realism?
4. How do you interface between ROS2 and Gazebo for sensor and actuator control?
5. What are the best practices for optimizing Gazebo simulation performance?

## Troubleshooting Common Issues

### Performance Issues
- **Symptom**: Slow simulation, dropped frames
- **Solution**: Reduce physics update rate, simplify collision models, use faster physics engine

### Physics Issues
- **Symptom**: Robot falls through ground, unrealistic movements
- **Solution**: Check mass/inertia properties, friction coefficients, collision geometries

### Sensor Issues
- **Symptom**: No sensor data, incorrect readings
- **Solution**: Verify sensor plugin configuration, check topic names, validate transforms

### Control Issues
- **Symptom**: Robot doesn't respond to commands, delayed response
- **Solution**: Check topic remapping, verify control loop timing, validate joint names

## Summary

Gazebo provides a powerful simulation environment for developing and testing humanoid robots. Understanding how to configure physics properties, spawn robots, and interface with ROS2 is essential for effective simulation-based development.

The combination of realistic physics simulation, sensor modeling, and ROS2 integration makes Gazebo an invaluable tool for humanoid robot development, allowing for safe testing of complex behaviors before deployment on real hardware.

In the next chapter, we'll explore more advanced simulation techniques including physics modeling and sensor simulation for humanoid robots.