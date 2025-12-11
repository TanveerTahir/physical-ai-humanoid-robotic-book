---
title: ROS2 Fundamentals
sidebar_position: 1
description: Understanding the fundamentals of Robot Operating System 2 (ROS2)
gpu_notes: This chapter requires GPU for simulation examples; minimum 4GB VRAM recommended for complex simulations
jetson_notes: Jetson AGX Xavier recommended for running ROS2 examples; Jetson Nano can run basic examples
---

# ROS2 Fundamentals

## Prerequisites

Before studying this chapter, you should have:
- Understanding of Physical AI and embodied intelligence (from Chapter 1)
- Knowledge of real-world vs. digital AI differences (from Chapter 2)
- Basic understanding of Linux command line
- Elementary knowledge of Python programming
- Familiarity with distributed systems concepts

## Learning Objectives

By the end of this chapter, you should be able to:
- Explain the core concepts of Robot Operating System 2 (ROS2)
- Identify the key differences between ROS1 and ROS2
- Create and manage ROS2 workspaces and packages
- Understand the publisher-subscriber and client-service communication patterns
- Launch and manage ROS2 nodes and processes

## Introduction

Robot Operating System 2 (ROS2) serves as the nervous system for many humanoid robots, providing the communication infrastructure that allows different components to work together seamlessly. Unlike its predecessor ROS1, ROS2 is built from the ground up with industrial-grade reliability, security, and real-time performance in mind.

This chapter introduces the fundamental concepts of ROS2 that form the backbone of the humanoid robot's software architecture. We'll explore how ROS2 enables distributed computing in robotic systems and provides the foundation for complex robot behaviors.

## What is ROS2?

ROS2 is not an operating system in the traditional sense, but rather a collection of libraries, tools, and conventions that facilitate the development of robot applications. It provides:

1. **Communication framework**: Enables different parts of a robot system to communicate
2. **Package management**: Organizes code into reusable components
3. **Development tools**: Provides debugging, visualization, and testing utilities
4. **Hardware abstraction**: Allows code to work across different robot platforms

### Key Improvements over ROS1

ROS2 addresses several limitations of ROS1:

- **Real-time support**: Deterministic behavior for time-critical applications
- **Security**: Authentication, authorization, and encryption capabilities
- **Distributed architecture**: No central master node that can be a single point of failure
- **Official Windows and macOS support**: Broader platform compatibility
- **Standard middleware**: DDS (Data Distribution Service) for robust communication

## ROS2 Architecture

ROS2 uses a distributed architecture based on the DDS (Data Distribution Service) middleware:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Node A        │    │   Node B        │    │   Node C        │
│                 │    │                 │    │                 │
│ Publisher ──────┼────┼───┐             │    │                 │
│ Subscriber ◄────┼────┼───┼─► Publisher │    │ Subscriber ◄────┤
│ Service Client  │    │   │ │           │    │ Service Server  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                    ┌─────────────────┐
                    │   DDS Layer     │
                    │ (Communication) │
                    └─────────────────┘
```

### Nodes

Nodes are the fundamental execution units in ROS2. Each node performs a specific function:

```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Topics and Messages

Topics enable asynchronous communication between nodes using a publish-subscribe pattern:

```python
# Publisher example
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.counter = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello ROS2 World: {self.counter}'
        self.publisher.publish(msg)
        self.counter += 1
        self.get_logger().info(f'Publishing: {msg.data}')
```

```python
# Subscriber example
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: {msg.data}')
```

### Services

Services provide synchronous request-response communication:

```python
# Service server
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('add_two_ints_server')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'Returning: {response.sum}')
        return response
```

```python
# Service client
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AddTwoIntsClient(Node):
    def __init__(self):
        super().__init__('add_two_ints_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

        self.req = AddTwoInts.Request()

    def send_request(self, a, b):
        self.req.a = a
        self.req.b = b
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()
```

## Creating a ROS2 Workspace

A ROS2 workspace is a directory where you develop and build ROS2 packages:

```bash
# Create workspace directory
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Source the ROS2 installation
source /opt/ros/humble/setup.bash  # or your ROS2 distribution

# Build the workspace
colcon build

# Source the workspace
source install/setup.bash
```

## Package Structure

A typical ROS2 package follows this structure:

```
my_robot_package/
├── CMakeLists.txt
├── package.xml
├── src/
│   ├── node.cpp
│   └── other_cpp_files.cpp
├── include/
│   └── my_robot_package/
│       └── header_files.hpp
├── launch/
│   └── my_launch_file.launch.py
├── config/
│   └── parameters.yaml
├── scripts/
├── test/
└── README.md
```

## Hands-on Lab: Creating Your First ROS2 Package

Let's create a simple ROS2 package that demonstrates the fundamental concepts:

```bash
# Navigate to your workspace
cd ~/ros2_ws/src

# Create a new package
ros2 pkg create --build-type ament_python my_first_ros2_pkg --dependencies rclpy std_msgs

# Navigate to the package directory
cd my_first_ros2_pkg
```

Now let's create a simple publisher and subscriber:

**publisher_member_function.py:**
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

**subscriber_member_function.py:**
```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

Add the executables to setup.py:

```python
entry_points={
    'console_scripts': [
        'talker = my_first_ros2_pkg.publisher_member_function:main',
        'listener = my_first_ros2_pkg.subscriber_member_function:main',
    ],
},
```

Build and run:
```bash
# Build the package
cd ~/ros2_ws
colcon build --packages-select my_first_ros2_pkg

# Source the workspace
source install/setup.bash

# Run the publisher in one terminal
ros2 run my_first_ros2_pkg talker

# Run the subscriber in another terminal
ros2 run my_first_ros2_pkg listener
```

## Launch Files

Launch files allow you to start multiple nodes simultaneously:

**example_launch.py:**
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'node_prefix',
            default_value='',
            description='Prefix of the node'),
        Node(
            package='my_first_ros2_pkg',
            executable='talker',
            name='minimal_publisher',
        ),
        Node(
            package='my_first_ros2_pkg',
            executable='listener',
            name='minimal_subscriber',
        ),
    ])
```

## Parameters

ROS2 supports parameter management for configuring nodes:

**params.yaml:**
```yaml
talker_node:
  ros__parameters:
    param_name: "param_value"
    frequency: 10
    use_sim_time: false
```

Access parameters in code:
```python
class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with default values
        self.declare_parameter('frequency', 10)
        self.declare_parameter('robot_name', 'default_robot')

        # Get parameter values
        freq = self.get_parameter('frequency').value
        name = self.get_parameter('robot_name').value

        self.get_logger().info(f'Frequency: {freq}, Robot: {name}')
```

## Evaluation Checkpoints

1. What are the main differences between ROS1 and ROS2?
2. Explain the publish-subscribe communication pattern in ROS2.
3. How do you create a new ROS2 package?
4. What is the purpose of launch files?
5. How do you handle parameters in ROS2 nodes?

## Summary

ROS2 provides the essential communication infrastructure for humanoid robots, enabling different components to work together harmoniously. Its distributed architecture, improved security, and real-time capabilities make it suitable for the complex requirements of humanoid robotics.

Understanding these fundamentals is crucial as we'll build upon them in the next chapters to create more sophisticated robot behaviors and integrate AI agents with the ROS2 ecosystem.

In the next chapter, we'll explore the different communication patterns in ROS2 including nodes, services, topics, and actions in greater detail.