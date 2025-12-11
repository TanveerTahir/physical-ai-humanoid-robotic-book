---
title: Nodes, Services, Topics, Actions
sidebar_position: 2
description: Understanding the fundamental communication patterns in ROS2
gpu_notes: This chapter requires GPU for simulation of complex multi-node systems; minimum 6GB VRAM recommended
jetson_notes: Jetson AGX Xavier recommended for multi-node simulation; Jetson Nano can run basic examples
---

# Nodes, Services, Topics, Actions

## Prerequisites

Before studying this chapter, you should have:
- Understanding of ROS2 fundamentals (from Chapter 5)
- Knowledge of basic Python programming
- Experience with command-line tools
- Understanding of distributed systems concepts

## Learning Objectives

By the end of this chapter, you should be able to:
- Distinguish between the different communication patterns in ROS2
- Implement nodes with various communication patterns
- Understand when to use topics, services, or actions
- Design efficient communication architectures for humanoid robots
- Debug communication issues between nodes

## Introduction

In the previous chapter, we introduced the fundamental concepts of ROS2 and explored the basic communication patterns. This chapter delves deeper into the four primary communication patterns in ROS2: Nodes, Topics, Services, and Actions. Understanding these patterns is crucial for designing the nervous system of a humanoid robot, where different components need to communicate efficiently and reliably.

Each communication pattern serves specific purposes and comes with its own trade-offs in terms of reliability, latency, and complexity. The choice of communication pattern significantly impacts the robot's performance, especially in time-sensitive applications like humanoid robotics.

## Nodes: The Execution Units

Nodes are the fundamental building blocks of any ROS2 application. Each node runs as a separate process and encapsulates specific functionality. In humanoid robots, nodes might handle perception, planning, control, or communication tasks.

### Node Lifecycle

Nodes in ROS2 follow a well-defined lifecycle that provides better control over their states:

```python
import rclpy
from rclpy.lifecycle import LifecycleNode, LifecycleState, TransitionCallbackReturn
from rclpy.executors import SingleThreadedExecutor

class LifecycleTalker(LifecycleNode):
    def __init__(self):
        super().__init__('lifecycle_talker')
        self.pub = None

    def on_configure(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Called when node transitions from UNCONFIGURED to INACTIVE"""
        self.get_logger().info(f'Configuring node from {state.label}')
        self.pub = self.create_publisher(String, 'lifecycle_chatter', 10)
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Called when node transitions from INACTIVE to ACTIVE"""
        self.get_logger().info(f'Activating node from {state.label}')
        self.timer = self.create_timer(1.0, self.timer_callback)
        return TransitionCallbackReturn.SUCCESS

    def timer_callback(self):
        if self.pub is not None:
            msg = String()
            msg.data = 'Lifecycle message'
            self.pub.publish(msg)

    def on_deactivate(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Called when node transitions from ACTIVE to INACTIVE"""
        self.get_logger().info(f'Deactivating node from {state.label}')
        self.destroy_timer(self.timer)
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: LifecycleState) -> TransitionCallbackReturn:
        """Called when node transitions from INACTIVE to UNCONFIGURED"""
        self.get_logger().info(f'Cleaning up node from {state.label}')
        self.destroy_publisher(self.pub)
        self.pub = None
        return TransitionCallbackReturn.SUCCESS
```

### Node Composition

For performance-critical applications like humanoid robots, nodes can be composed into a single process to reduce communication overhead:

```python
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from lifecycle_node import LifecycleTalker

class NodeContainer(Node):
    def __init__(self):
        super().__init__('node_container')

        # Create nodes to compose
        self.lc_talker = LifecycleTalker()

        # Create executor and add nodes
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.lc_talker)

        # Spin the executor in a separate thread
        import threading
        self.executor_thread = threading.Thread(target=self.executor.spin)
        self.executor_thread.start()
```

## Topics: Asynchronous Communication

Topics implement a publish-subscribe communication pattern where publishers send messages to topics and subscribers receive messages from topics. This is the most common communication pattern in ROS2 and is ideal for streaming data like sensor readings or robot states.

### Publisher Implementation

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState
import math

class JointStatePublisher(Node):
    def __init__(self):
        super().__init__('joint_state_publisher')

        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Timer to periodically publish joint states
        self.timer = self.create_timer(0.02, self.publish_joint_states)  # 50Hz

        # Initialize joint names and positions
        self.joint_names = [
            'hip_joint', 'knee_joint', 'ankle_joint',
            'shoulder_joint', 'elbow_joint', 'wrist_joint'
        ]
        self.joint_positions = [0.0] * len(self.joint_names)
        self.time = 0.0

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.name = self.joint_names
        msg.position = self.joint_positions

        # Simulate changing joint positions
        self.time += 0.02
        for i in range(len(self.joint_positions)):
            self.joint_positions[i] = 0.5 * math.sin(self.time + i * 0.5)

        self.joint_pub.publish(msg)
```

### Subscriber Implementation

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Time

class JointStateSubscriber(Node):
    def __init__(self):
        super().__init__('joint_state_subscriber')

        # Subscriber for joint states
        self.joint_sub = self.create_subscription(
            JointState,
            'joint_states',
            self.joint_state_callback,
            10
        )

        self.latest_joint_state = None

    def joint_state_callback(self, msg: JointState):
        self.get_logger().info(f'Received joint states for {len(msg.name)} joints')
        self.latest_joint_state = msg

        # Process joint states (e.g., update robot model)
        for name, pos in zip(msg.name, msg.position):
            self.get_logger().debug(f'{name}: {pos:.3f}')
```

### Quality of Service (QoS) Settings

For humanoid robots, QoS settings are critical for ensuring reliable communication:

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

class QoSPublisher(Node):
    def __init__(self):
        super().__init__('qos_publisher')

        # QoS profile for sensor data (high frequency, may lose packets)
        sensor_qos = QoSProfile(
            depth=5,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )

        # QoS profile for critical data (must not lose packets)
        critical_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )

        self.sensor_pub = self.create_publisher(JointState, 'sensor_data', sensor_qos)
        self.critical_pub = self.create_publisher(String, 'critical_commands', critical_qos)
```

## Services: Synchronous Request-Response

Services provide synchronous communication with guaranteed delivery. They're ideal for operations that need a response, such as configuration changes, triggering actions, or requesting specific information.

### Service Server Implementation

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import Trigger, SetBool
from std_srvs.srv import Empty
import threading

class RobotControlService(Node):
    def __init__(self):
        super().__init__('robot_control_service')

        # Service to start robot
        self.start_service = self.create_service(
            Trigger,
            'start_robot',
            self.handle_start_robot
        )

        # Service to stop robot
        self.stop_service = self.create_service(
            Trigger,
            'stop_robot',
            self.handle_stop_robot
        )

        # Service to enable/disable robot
        self.enable_service = self.create_service(
            SetBool,
            'enable_robot',
            self.handle_enable_robot
        )

        self.robot_enabled = False

    def handle_start_robot(self, request, response):
        """Handle start robot request"""
        if not self.robot_enabled:
            response.success = False
            response.message = 'Robot is disabled, cannot start'
            return response

        # Perform start sequence
        self.get_logger().info('Starting robot...')

        # Simulate start process
        # In real implementation, this might initialize motors, calibrate sensors, etc.
        response.success = True
        response.message = 'Robot started successfully'
        return response

    def handle_stop_robot(self, request, response):
        """Handle stop robot request"""
        self.get_logger().info('Stopping robot...')

        # Perform stop sequence
        # In real implementation, this might safely disable motors, save state, etc.
        response.success = True
        response.message = 'Robot stopped successfully'
        return response

    def handle_enable_robot(self, request, response):
        """Handle enable/disable robot request"""
        self.robot_enabled = request.data
        status = 'enabled' if self.robot_enabled else 'disabled'
        self.get_logger().info(f'Robot {status}')

        response.success = True
        response.message = f'Robot {status}'
        return response
```

### Service Client Implementation

```python
import rclpy
from rclpy.node import Node
from example_interfaces.srv import Trigger, SetBool
import time

class ServiceClient(Node):
    def __init__(self):
        super().__init__('service_client')

        # Create clients for services
        self.start_client = self.create_client(Trigger, 'start_robot')
        self.stop_client = self.create_client(Trigger, 'stop_robot')
        self.enable_client = self.create_client(SetBool, 'enable_robot')

        # Wait for services to be available
        while not self.start_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Start service not available, waiting again...')

        while not self.stop_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Stop service not available, waiting again...')

        while not self.enable_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Enable service not available, waiting again...')

    def enable_robot(self, enable=True):
        """Call enable robot service"""
        request = SetBool.Request()
        request.data = enable

        future = self.enable_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        response = future.result()
        if response is not None:
            self.get_logger().info(f'Enable response: {response.message}')
            return response.success
        else:
            self.get_logger().error('Failed to call enable service')
            return False

    def start_robot(self):
        """Call start robot service"""
        request = Trigger.Request()

        future = self.start_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        response = future.result()
        if response is not None:
            self.get_logger().info(f'Start response: {response.message}')
            return response.success
        else:
            self.get_logger().error('Failed to call start service')
            return False

    def stop_robot(self):
        """Call stop robot service"""
        request = Trigger.Request()

        future = self.stop_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        response = future.result()
        if response is not None:
            self.get_logger().info(f'Stop response: {response.message}')
            return response.success
        else:
            self.get_logger().error('Failed to call stop service')
            return False
```

## Actions: Long-Running Tasks with Feedback

Actions are designed for long-running tasks that provide feedback and can be preempted. They're perfect for humanoid robot tasks like walking, grasping, or navigation where you need to know the progress and potentially cancel the operation.

### Action Server Implementation

```python
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from example_interfaces.action import Fibonacci
import threading
import time

class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')

        # Create action server
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_fibonacci,
            callback_group=ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

    def goal_callback(self, goal_request):
        """Accept or reject a goal"""
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject a cancel request"""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    def execute_fibonacci(self, goal_handle):
        """Execute the goal"""
        self.get_logger().info('Executing goal...')

        # Notify that the goal is starting
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        # Simulate a long-running task
        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            # Update feedback
            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1]
            )

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)

            # Sleep to simulate work
            time.sleep(0.5)

        # Goal succeeded
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Goal succeeded with result: {result.sequence}')

        return result
```

### Action Client Implementation

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from example_interfaces.action import Fibonacci

class FibonacciActionClient(Node):
    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._action_client = ActionClient(self, Fibonacci, 'fibonacci')

    def send_goal(self, order=10):
        """Send goal to action server"""
        # Wait for action server
        self._action_client.wait_for_server()

        # Create goal
        goal_msg = Fibonacci.Goal()
        goal_msg.order = order

        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handle goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')

        # Get result
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        """Handle feedback"""
        self.get_logger().info(f'Received feedback: {feedback_msg.feedback.sequence}')

    def get_result_callback(self, future):
        """Handle result"""
        result = future.result().result
        self.get_logger().info(f'Result: {result.sequence}')
        rclpy.shutdown()
```

## Communication Architecture for Humanoid Robots

Humanoid robots require a sophisticated communication architecture to coordinate multiple subsystems:

```
                    ┌─────────────────┐
                    │ Perception Node │
                    │ (Cameras, LIDAR)│
                    └─────────────────┘
                              │
                    ┌─────────────────┐
                    │   State Est.    │
                    │ (Kalman Filter) │
                    └─────────────────┘
                     │           │
        ┌─────────────┘           └─────────────┐
        │                                     │
┌─────────────────┐                   ┌─────────────────┐
│ Planning Node   │                   │ Control Node    │
│ (Motion Planner)│                   │ (Joint Control) │
└─────────────────┘                   └─────────────────┘
        │                                     │
        └─────────────────────────────────────┘
                              │
                    ┌─────────────────┐
                    │   Hardware      │
                    │ Interface Node  │
                    │ (Motor Drivers) │
                    └─────────────────┘
```

### Best Practices for Communication Design

1. **Use appropriate QoS settings**: Sensor data can use BEST_EFFORT, critical commands should use RELIABLE
2. **Minimize message size**: Use efficient data structures and compression when needed
3. **Consider timing requirements**: High-frequency control loops need low-latency communication
4. **Design for fault tolerance**: Implement fallback behaviors when communication fails
5. **Use namespaces**: Organize topics and services with clear naming conventions

## Hands-on Lab: Multi-Node Communication System

Let's create a multi-node communication system that demonstrates all communication patterns:

```python
# coordinator_node.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from example_interfaces.srv import Trigger
from example_interfaces.action import Fibonacci
from rclpy.action import ActionClient

class CoordinatorNode(Node):
    def __init__(self):
        super().__init__('coordinator_node')

        # Publishers and subscribers
        self.status_pub = self.create_publisher(String, 'robot_status', 10)
        self.cmd_sub = self.create_subscription(
            String, 'commands', self.command_callback, 10
        )

        # Service client
        self.start_client = self.create_client(Trigger, 'start_robot')

        # Action client
        self.fibonacci_client = ActionClient(self, Fibonacci, 'fibonacci')

        # Timer to periodically publish status
        self.timer = self.create_timer(1.0, self.publish_status)

    def publish_status(self):
        msg = String()
        msg.data = f'Coordinator running - {self.get_clock().now().seconds_nanoseconds()}'
        self.status_pub.publish(msg)

    def command_callback(self, msg):
        self.get_logger().info(f'Received command: {msg.data}')

        if msg.data == 'start':
            self.start_robot()
        elif msg.data == 'fibonacci':
            self.request_fibonacci()

    def start_robot(self):
        """Call start robot service"""
        while not self.start_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Start service not available')

        request = Trigger.Request()
        future = self.start_client.call_async(request)
        # Handle response asynchronously

    def request_fibonacci(self):
        """Send fibonacci action goal"""
        if not self.fibonacci_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().error('Action server not available')
            return

        goal_msg = Fibonacci.Goal()
        goal_msg.order = 5

        self.fibonacci_client.send_goal_async(
            goal_msg,
            feedback_callback=self.fibonacci_feedback
        )

    def fibonacci_feedback(self, feedback_msg):
        self.get_logger().info(f'Fibonacci feedback: {feedback_msg.feedback.sequence}')
```

## Evaluation Checkpoints

1. What are the key differences between topics, services, and actions?
2. When would you use each communication pattern in a humanoid robot?
3. How do QoS settings affect communication reliability?
4. What is the purpose of the node lifecycle?
5. How can you compose multiple nodes into a single process?

## Troubleshooting Common Issues

### Topic Communication Issues
- **No messages received**: Check topic names match exactly, verify nodes are running
- **Message delay**: Check system load, consider QoS settings
- **Message loss**: Use RELIABLE QoS for critical data

### Service Communication Issues
- **Service not available**: Ensure service server is running and connected to same ROS domain
- **Long response times**: Check server processing time, consider threading

### Action Communication Issues
- **Action server not responding**: Verify action server is running and accepting goals
- **Feedback not updating**: Check if feedback is being published during execution

## Summary

This chapter explored the four fundamental communication patterns in ROS2: Nodes, Topics, Services, and Actions. Each pattern serves specific purposes in a humanoid robot's nervous system, from streaming sensor data through topics to managing long-running tasks with actions.

Understanding when and how to use each communication pattern is essential for designing efficient and reliable robotic systems. The choice of communication pattern directly impacts the robot's performance, especially in real-time applications like humanoid robotics.

In the next chapter, we'll explore how to bind ROS2 with AI agents using the Python client library (rclpy), creating intelligent systems that can interact with the robot's hardware and software infrastructure.