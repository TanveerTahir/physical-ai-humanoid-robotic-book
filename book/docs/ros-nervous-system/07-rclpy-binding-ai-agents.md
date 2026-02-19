---
title: rclpy Binding with AI Agents
sidebar_position: 3
description: Integrating AI agents with ROS2 using the Python client library
gpu_notes: This chapter requires GPU for running AI models; minimum 8GB VRAM recommended for transformer models
jetson_notes: Jetson AGX Orin recommended for AI inference; Jetson AGX Xavier for lightweight models
---

# rclpy Binding with AI Agents

## Prerequisites

Before studying this chapter, you should have:
- Understanding of ROS2 fundamentals and communication patterns (from Chapters 5-6)
- Knowledge of Python programming and AI concepts
- Basic understanding of neural networks and machine learning
- Experience with ROS2 Python client library (rclpy)
- Familiarity with AI frameworks like TensorFlow or PyTorch

## Learning Objectives

By the end of this chapter, you should be able to:
- Integrate AI agents with ROS2 using rclpy
- Design communication patterns between AI agents and robot systems
- Implement real-time AI inference within ROS2 nodes
- Create AI-powered services and actions for robot control
- Optimize AI agent performance for real-time robotics applications

## Introduction

The integration of AI agents with ROS2 systems represents a crucial advancement in humanoid robotics. Traditional robotics relied on pre-programmed behaviors, but modern humanoid robots require intelligent decision-making capabilities that can adapt to dynamic environments. This chapter explores how to bind AI agents with ROS2 using the rclpy Python client library, creating intelligent systems that can perceive, reason, and act in real-time.

The rclpy library provides a Python interface to ROS2, making it an ideal choice for integrating AI agents that are often developed in Python. This integration enables humanoid robots to leverage advanced AI capabilities while maintaining the robust communication infrastructure provided by ROS2.

## AI Agent Architecture for Robotics

AI agents in robotics typically follow a perception-action loop:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Perception    │───▶│    Reasoning    │───▶│    Action       │
│   (Sensors)     │    │   (Decision)    │    │   (Actuators)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                                           │
         │                                           │
         └───────────────────────────────────────────┘
                           Feedback Loop
```

### Components of an AI Agent in ROS2

1. **Perception Module**: Processes sensor data from ROS2 topics
2. **Memory System**: Stores and retrieves relevant information
3. **Reasoning Engine**: Makes decisions based on current state
4. **Action Executor**: Sends commands to robot actuators via ROS2
5. **Learning Component**: Updates behavior based on experience

## Setting Up AI Integration with rclpy

### Installing Required Dependencies

First, let's set up the necessary dependencies for AI integration:

```bash
# Install AI libraries alongside ROS2
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install tensorflow
pip3 install transformers
pip3 install scikit-learn
pip3 install opencv-python
pip3 install numpy scipy
```

### Basic AI Node Structure

Here's a template for creating an AI-powered ROS2 node:

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from std_srvs.srv import Trigger
import numpy as np
import torch
import cv2
from cv_bridge import CvBridge

class AIAgentNode(Node):
    def __init__(self):
        super().__init__('ai_agent_node')

        # Initialize AI model
        self.ai_model = self.load_ai_model()

        # Initialize CV bridge for image processing
        self.bridge = CvBridge()

        # Publishers for AI outputs
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.ai_status_pub = self.create_publisher(String, 'ai_status', 10)

        # Subscribers for sensor inputs
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10
        )
        self.laser_sub = self.create_subscription(
            LaserScan, 'scan', self.laser_callback, 10
        )

        # Service for AI control
        self.ai_control_srv = self.create_service(
            Trigger, 'control_ai_agent', self.control_ai_callback
        )

        # Timer for AI inference loop
        self.inference_timer = self.create_timer(0.1, self.ai_inference_loop)

        # Internal state
        self.latest_image = None
        self.latest_laser = None
        self.ai_enabled = True

        self.get_logger().info('AI Agent Node initialized')

    def load_ai_model(self):
        """Load the AI model for inference"""
        # This is a placeholder - in practice, load your specific model
        try:
            # Example: Load a pre-trained model
            # model = torch.load('path/to/model.pth')
            # model.eval()
            # return model

            # For demonstration, return a dummy model
            class DummyModel:
                def __call__(self, x):
                    return np.random.random(4)  # Example output

            return DummyModel()
        except Exception as e:
            self.get_logger().error(f'Failed to load AI model: {e}')
            return None

    def image_callback(self, msg):
        """Process incoming image data"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.latest_image = cv_image
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def laser_callback(self, msg):
        """Process incoming laser scan data"""
        self.latest_laser = np.array(msg.ranges)

    def ai_inference_loop(self):
        """Main AI inference loop"""
        if not self.ai_enabled:
            return

        if self.ai_model is None:
            return

        # Prepare input data for AI model
        input_data = self.prepare_input_data()

        if input_data is not None:
            # Run AI inference
            ai_output = self.run_ai_inference(input_data)

            # Process AI output and send commands
            self.process_ai_output(ai_output)

    def prepare_input_data(self):
        """Prepare sensor data for AI model"""
        if self.latest_image is None or self.latest_laser is None:
            return None

        # Process image and laser data for AI model
        processed_image = self.preprocess_image(self.latest_image)
        processed_laser = self.preprocess_laser(self.latest_laser)

        # Combine sensor data into model input
        input_tensor = np.concatenate([processed_image.flatten(), processed_laser])

        return input_tensor

    def preprocess_image(self, image):
        """Preprocess image for AI model"""
        # Resize, normalize, etc.
        resized = cv2.resize(image, (224, 224))
        normalized = resized.astype(np.float32) / 255.0
        return normalized

    def preprocess_laser(self, laser_ranges):
        """Preprocess laser data for AI model"""
        # Handle infinite ranges and normalize
        processed = np.array(laser_ranges)
        processed[np.isinf(processed)] = 10.0  # Replace inf with max range
        processed = np.clip(processed, 0.0, 10.0) / 10.0  # Normalize to [0, 1]
        return processed

    def run_ai_inference(self, input_data):
        """Run AI model inference"""
        try:
            # Convert to tensor if using PyTorch
            if isinstance(input_data, np.ndarray):
                input_tensor = torch.from_numpy(input_data).float()
                input_tensor = input_tensor.unsqueeze(0)  # Add batch dimension

            # Run inference
            with torch.no_grad():
                output = self.ai_model(input_tensor)

            # Convert output back to numpy
            if torch.is_tensor(output):
                output = output.numpy()

            return output
        except Exception as e:
            self.get_logger().error(f'AI inference error: {e}')
            return None

    def process_ai_output(self, ai_output):
        """Process AI output and send robot commands"""
        if ai_output is None:
            return

        # Interpret AI output and generate robot commands
        cmd_vel = Twist()

        # Example: Use first two outputs as linear and angular velocity
        cmd_vel.linear.x = float(ai_output[0] * 2.0 - 1.0)  # Scale to [-1, 1]
        cmd_vel.angular.z = float(ai_output[1] * 2.0 - 1.0)  # Scale to [-1, 1]

        # Publish command
        self.cmd_vel_pub.publish(cmd_vel)

        # Publish status
        status_msg = String()
        status_msg.data = f'AI commanding: lin.x={cmd_vel.linear.x:.2f}, ang.z={cmd_vel.angular.z:.2f}'
        self.ai_status_pub.publish(status_msg)

    def control_ai_callback(self, request, response):
        """Handle AI control service requests"""
        if request.succeed:
            self.ai_enabled = True
            response.success = True
            response.message = 'AI agent enabled'
        else:
            self.ai_enabled = False
            response.success = True
            response.message = 'AI agent disabled'

        return response

def main(args=None):
    rclpy.init(args=args)

    ai_agent_node = AIAgentNode()

    try:
        rclpy.spin(ai_agent_node)
    except KeyboardInterrupt:
        ai_agent_node.get_logger().info('Interrupted, shutting down...')
    finally:
        ai_agent_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Real-Time AI Inference in ROS2

### Optimizing AI Models for Robotics

Real-time robotics applications require AI models that can run efficiently on the robot's hardware:

```python
import torch
import torch.nn as nn
import numpy as np

class OptimizedRobotVisionNet(nn.Module):
    """Optimized neural network for robot vision tasks"""
    def __init__(self, num_classes=5):
        super().__init__()

        # Lightweight convolutional layers
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=2, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4))  # Fixed size output
        )

        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

class RealTimeAINode(Node):
    def __init__(self):
        super().__init__('realtime_ai_node')

        # Load optimized model
        self.model = OptimizedRobotVisionNet()
        self.model.eval()

        # Move to GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        # Track inference times
        self.inference_times = []

        # Setup ROS2 components
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.optimized_image_callback, 5
        )

        # Use reduced QoS for performance
        qos_profile = rclpy.qos.QoSProfile(depth=1)
        qos_profile.reliability = rclpy.qos.ReliabilityPolicy.BEST_EFFORT
        qos_profile.durability = rclpy.qos.DurabilityPolicy.VOLATILE

        self.result_pub = self.create_publisher(String, 'ai_result', qos_profile)

        self.get_logger().info(f'AI Model loaded on {self.device}')

    def optimized_image_callback(self, msg):
        """Optimized image processing with performance tracking"""
        start_time = self.get_clock().now()

        try:
            # Convert image with minimal processing
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Preprocess for model
            input_tensor = self.preprocess_for_model(cv_image)

            # Run inference
            with torch.no_grad():
                if self.device.type == 'cuda':
                    torch.cuda.synchronize()  # Accurate timing

                output = self.model(input_tensor)

                if self.device.type == 'cuda':
                    torch.cuda.synchronize()  # Accurate timing

            # Process results
            result = self.process_output(output)

            # Publish results
            result_msg = String()
            result_msg.data = result
            self.result_pub.publish(result_msg)

            # Track performance
            end_time = self.get_clock().now()
            inference_time = (end_time.nanoseconds - start_time.nanoseconds) / 1e6  # ms
            self.inference_times.append(inference_time)

            # Log performance every 100 inferences
            if len(self.inference_times) % 100 == 0:
                avg_time = sum(self.inference_times[-100:]) / 100
                self.get_logger().info(f'Average inference time: {avg_time:.2f}ms')

        except Exception as e:
            self.get_logger().error(f'Error in optimized callback: {e}')

    def preprocess_for_model(self, image):
        """Efficient preprocessing for model inference"""
        # Resize to model input size
        resized = cv2.resize(image, (64, 64))  # Smaller size for speed

        # Convert to tensor
        tensor = torch.from_numpy(resized).float()
        tensor = tensor.permute(2, 0, 1)  # HWC to CHW
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        tensor = tensor.to(self.device)
        tensor = tensor / 255.0  # Normalize

        return tensor

    def process_output(self, output):
        """Process model output efficiently"""
        probabilities = torch.softmax(output, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()

        return f'class_{predicted_class}_confidence_{confidence:.3f}'
```

## AI-Powered Services and Actions

### AI Service Server

Create services that leverage AI capabilities:

```python
from example_interfaces.srv import Trigger, SetBool
import json

class AIPerceptionService(Node):
    def __init__(self):
        super().__init__('ai_perception_service')

        # Load perception model
        self.perception_model = self.load_perception_model()

        # Service for object detection
        self.detect_service = self.create_service(
            Trigger, 'detect_objects', self.detect_objects_callback
        )

        # Service for scene understanding
        self.understand_service = self.create_service(
            Trigger, 'understand_scene', self.understand_scene_callback
        )

        # Service for navigation planning with AI
        self.plan_nav_service = self.create_service(
            Trigger, 'plan_navigation_ai', self.plan_navigation_callback
        )

        # Store latest sensor data
        self.latest_data = {}

        # Subscribe to sensor data
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.store_image, 1
        )

        self.get_logger().info('AI Perception Service initialized')

    def store_image(self, msg):
        """Store latest image for service calls"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.latest_data['image'] = cv_image
        except Exception as e:
            self.get_logger().error(f'Error storing image: {e}')

    def detect_objects_callback(self, request, response):
        """Detect objects in the latest image"""
        if 'image' not in self.latest_data:
            response.success = False
            response.message = 'No image data available'
            return response

        try:
            # Run object detection
            detections = self.run_object_detection(self.latest_data['image'])

            # Format results
            result_str = json.dumps(detections)
            response.success = True
            response.message = result_str

        except Exception as e:
            response.success = False
            response.message = f'Object detection failed: {str(e)}'

        return response

    def run_object_detection(self, image):
        """Run object detection on image"""
        # Preprocess image
        input_tensor = self.preprocess_for_detection(image)

        # Run model
        with torch.no_grad():
            outputs = self.perception_model(input_tensor)

        # Process outputs (this is simplified - real implementation would parse model outputs)
        detections = {
            'objects': [],
            'confidence_threshold': 0.5,
            'processing_time_ms': 23.4  # Example timing
        }

        # In real implementation, parse actual model outputs
        # For now, return example structure
        detections['objects'] = [
            {'class': 'person', 'confidence': 0.89, 'bbox': [100, 150, 200, 300]},
            {'class': 'chair', 'confidence': 0.76, 'bbox': [300, 200, 450, 350]}
        ]

        return detections

    def understand_scene_callback(self, request, response):
        """Understand the scene context"""
        if 'image' not in self.latest_data:
            response.success = False
            response.message = 'No image data available'
            return response

        try:
            # Run scene understanding
            scene_description = self.run_scene_understanding(self.latest_data['image'])

            response.success = True
            response.message = scene_description

        except Exception as e:
            response.success = False
            response.message = f'Scene understanding failed: {str(e)}'

        return response

    def plan_navigation_callback(self, request, response):
        """Plan navigation using AI"""
        # This would typically use a navigation AI model
        # For now, return example response
        response.success = True
        response.message = json.dumps({
            'path': [[0, 0], [1, 1], [2, 2], [3, 3]],
            'safe': True,
            'estimated_time': 15.5
        })

        return response

    def load_perception_model(self):
        """Load perception model"""
        # In practice, load a pre-trained object detection model
        # This is a placeholder
        class DummyModel:
            def __call__(self, x):
                return torch.randn(1, 10, 6)  # Example output

        return DummyModel()
```

### AI-Powered Action Server

Create actions that involve AI planning and execution:

```python
from rclpy.action import ActionServer
from example_interfaces.action import Fibonacci  # Using Fibonacci as example
import threading
import time

class AIPlanningActionServer(Node):
    def __init__(self):
        super().__init__('ai_planning_action_server')

        # Load planning model
        self.planning_model = self.load_planning_model()

        # Create action server for AI planning
        self._action_server = ActionServer(
            self,
            Fibonacci,  # In real implementation, use custom action type
            'ai_plan_execution',
            execute_callback=self.execute_ai_plan,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        self.get_logger().info('AI Planning Action Server initialized')

    def goal_callback(self, goal_request):
        """Accept or reject AI planning goals"""
        self.get_logger().info(f'Received AI planning goal: {goal_request}')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Handle AI planning cancellation"""
        self.get_logger().info('Received AI planning cancellation')
        return CancelResponse.ACCEPT

    def execute_ai_plan(self, goal_handle):
        """Execute AI planning with feedback"""
        self.get_logger().info('Executing AI plan...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        # Simulate AI planning process
        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('AI plan canceled')
                return Fibonacci.Result()

            # Simulate AI planning step
            next_value = feedback_msg.sequence[i] + feedback_msg.sequence[i-1]
            feedback_msg.sequence.append(next_value)

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)

            # Simulate processing time
            time.sleep(0.2)

            # In real implementation, this would involve actual AI planning
            # such as path planning, manipulation planning, etc.

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence

        self.get_logger().info(f'AI plan completed: {result.sequence}')
        return result

    def load_planning_model(self):
        """Load AI planning model"""
        # Placeholder for loading actual planning model
        class DummyPlanningModel:
            def plan(self, start, goal, obstacles):
                # Return a simple path
                return [start, goal]  # Simplified

        return DummyPlanningModel()
```

## Memory and Learning Integration

### Episodic Memory for AI Agents

Humanoid robots benefit from memory systems that store and recall experiences:

```python
import pickle
import os
from collections import deque
import hashlib

class RobotMemorySystem(Node):
    def __init__(self):
        super().__init__('robot_memory_system')

        # Memory storage
        self.episodic_memory = deque(maxlen=1000)  # Recent episodes
        self.semantic_memory = {}  # General knowledge
        self.procedural_memory = {}  # Learned procedures

        # Memory persistence
        self.memory_dir = os.path.expanduser('~/.robot_memory')
        os.makedirs(self.memory_dir, exist_ok=True)

        # Service for memory operations
        self.store_memory_srv = self.create_service(
            Trigger, 'store_episode', self.store_episode_callback
        )
        self.retrieve_memory_srv = self.create_service(
            Trigger, 'retrieve_memory', self.retrieve_memory_callback
        )

        # Timer for memory consolidation
        self.consolidation_timer = self.create_timer(30.0, self.consolidate_memories)

        self.get_logger().info('Robot Memory System initialized')

    def store_episode_callback(self, request, response):
        """Store current episode in memory"""
        try:
            # Get current robot state
            episode_data = {
                'timestamp': self.get_clock().now().nanoseconds,
                'sensor_data': self.get_latest_sensor_data(),
                'actions_taken': self.get_recent_actions(),
                'outcome': 'success'  # Would be determined by execution
            }

            # Store in episodic memory
            self.episodic_memory.append(episode_data)

            # Save to persistent storage
            self.save_memory_to_disk()

            response.success = True
            response.message = f'Stored episode at {episode_data["timestamp"]}'

        except Exception as e:
            response.success = False
            response.message = f'Memory storage failed: {str(e)}'

        return response

    def retrieve_memory_callback(self, request, response):
        """Retrieve relevant memories"""
        try:
            # In real implementation, this would use similarity search
            # For now, return recent episodes
            recent_episodes = list(self.episodic_memory)[-5:]  # Last 5 episodes

            # Format response
            memory_summary = {
                'episode_count': len(recent_episodes),
                'episodes': [
                    {
                        'timestamp': ep['timestamp'],
                        'outcome': ep['outcome']
                    } for ep in recent_episodes
                ]
            }

            response.success = True
            response.message = str(memory_summary)

        except Exception as e:
            response.success = False
            response.message = f'Memory retrieval failed: {str(e)}'

        return response

    def get_latest_sensor_data(self):
        """Get latest sensor data"""
        # This would interface with actual sensor data
        return {'placeholder': True}

    def get_recent_actions(self):
        """Get recent actions taken by the robot"""
        # This would interface with action history
        return [{'action': 'move_forward', 'timestamp': 1234567890}]

    def save_memory_to_disk(self):
        """Save memories to persistent storage"""
        try:
            # Save episodic memory
            episodic_path = os.path.join(self.memory_dir, 'episodic.pkl')
            with open(episodic_path, 'wb') as f:
                pickle.dump(list(self.episodic_memory), f)

            # Save semantic memory
            semantic_path = os.path.join(self.memory_dir, 'semantic.pkl')
            with open(semantic_path, 'wb') as f:
                pickle.dump(self.semantic_memory, f)

        except Exception as e:
            self.get_logger().error(f'Failed to save memory to disk: {e}')

    def load_memory_from_disk(self):
        """Load memories from persistent storage"""
        try:
            # Load episodic memory
            episodic_path = os.path.join(self.memory_dir, 'episodic.pkl')
            if os.path.exists(episodic_path):
                with open(episodic_path, 'rb') as f:
                    loaded_episodes = pickle.load(f)
                    self.episodic_memory = deque(loaded_episodes, maxlen=1000)

            # Load semantic memory
            semantic_path = os.path.join(self.memory_dir, 'semantic.pkl')
            if os.path.exists(semantic_path):
                with open(semantic_path, 'rb') as f:
                    self.semantic_memory = pickle.load(f)

        except Exception as e:
            self.get_logger().error(f'Failed to load memory from disk: {e}')

    def consolidate_memories(self):
        """Consolidate memories and extract general knowledge"""
        self.get_logger().info('Consolidating memories...')

        # This would involve:
        # - Finding patterns in episodic memories
        # - Extracting general rules/procedures
        # - Updating semantic and procedural memory
        # - Pruning old memories
        pass
```

## Performance Optimization for AI-Robot Integration

### Efficient AI Model Serving

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

class OptimizedAINode(Node):
    def __init__(self):
        super().__init__('optimized_ai_node')

        # Thread pool for CPU-bound AI operations
        self.thread_pool = ThreadPoolExecutor(max_workers=2)

        # Async event loop for non-blocking operations
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.run_event_loop, daemon=True).start()

        # Model serving optimization
        self.model_lock = threading.Lock()
        self.input_queue = asyncio.Queue(maxsize=5)  # Prevent backlog

        # Setup publishers/subscribers
        self.setup_communication()

        self.get_logger().info('Optimized AI Node initialized')

    def run_event_loop(self):
        """Run asyncio event loop in background thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def setup_communication(self):
        """Setup optimized ROS2 communication"""
        # Use appropriate QoS for different data types
        sensor_qos = rclpy.qos.QoSProfile(
            depth=1,
            reliability=rclpy.qos.ReliabilityPolicy.BEST_EFFORT,
            durability=rclpy.qos.DurabilityPolicy.VOLATILE
        )

        command_qos = rclpy.qos.QoSProfile(
            depth=10,
            reliability=rclpy.qos.ReliabilityPolicy.RELIABLE,
            durability=rclpy.qos.DurabilityPolicy.VOLATILE
        )

        # Subscribers with optimized QoS
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.optimized_image_handler, sensor_qos
        )

        # Publishers with optimized QoS
        self.ai_cmd_pub = self.create_publisher(Twist, 'ai_cmd_vel', command_qos)

    async def process_ai_input_async(self, sensor_data):
        """Process AI input asynchronously"""
        # Queue input for processing
        try:
            await self.input_queue.put(sensor_data)
        except asyncio.QueueFull:
            # Drop oldest if queue full
            try:
                await self.input_queue.get()
                await self.input_queue.put(sensor_data)
            except Exception:
                pass  # Queue might be closed

    def optimized_image_handler(self, msg):
        """Optimized image handler using async processing"""
        # Convert image to format needed for AI
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

            # Process in event loop
            future = asyncio.run_coroutine_threadsafe(
                self.process_ai_input_async(cv_image),
                self.loop
            )

        except Exception as e:
            self.get_logger().error(f'Error in image handler: {e}')
```

## Hands-on Lab: Creating an AI-Integrated Navigation System

Let's create a complete example that integrates AI with ROS2 for navigation:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import LaserScan, Image
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import String
import numpy as np
import torch
import torch.nn as nn
import cv2
from cv_bridge import CvBridge

class AINavigationNode(Node):
    def __init__(self):
        super().__init__('ai_navigation_node')

        # Initialize AI navigation model
        self.nav_model = self.create_navigation_model()
        self.nav_model.eval()

        # CV bridge
        self.bridge = CvBridge()

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.status_pub = self.create_publisher(String, 'ai_nav_status', 10)

        # Subscribers
        self.scan_sub = self.create_subscription(
            LaserScan, 'scan', self.scan_callback, 10
        )
        self.camera_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10
        )

        # Internal state
        self.latest_scan = None
        self.latest_image = None
        self.nav_enabled = True

        # Timer for navigation decisions
        self.nav_timer = self.create_timer(0.2, self.make_navigation_decision)

        self.get_logger().info('AI Navigation Node initialized')

    def create_navigation_model(self):
        """Create a simple navigation AI model"""
        class SimpleNavModel(nn.Module):
            def __init__(self):
                super().__init__()
                # Simple model that takes sensor data and outputs movement commands
                self.network = nn.Sequential(
                    nn.Linear(360 + 3072, 128),  # 360 laser points + flattened 32x32x3 image
                    nn.ReLU(),
                    nn.Linear(128, 64),
                    nn.ReLU(),
                    nn.Linear(64, 2)  # linear and angular velocities
                )

            def forward(self, laser_data, image_data):
                combined = torch.cat([laser_data, image_data], dim=1)
                return self.network(combined)

        return SimpleNavModel()

    def scan_callback(self, msg):
        """Process laser scan data"""
        ranges = np.array(msg.ranges)
        # Handle invalid ranges
        ranges[np.isnan(ranges)] = msg.range_max
        ranges[np.isinf(ranges)] = msg.range_max
        self.latest_scan = ranges

    def image_callback(self, msg):
        """Process camera image"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            # Resize for processing speed
            resized = cv2.resize(cv_image, (32, 32))
            self.latest_image = resized
        except Exception as e:
            self.get_logger().error(f'Image processing error: {e}')

    def make_navigation_decision(self):
        """Make navigation decisions using AI"""
        if not self.nav_enabled:
            return

        if self.latest_scan is None or self.latest_image is None:
            return

        try:
            # Prepare input data
            laser_tensor = torch.from_numpy(self.latest_scan).float().unsqueeze(0)
            image_tensor = torch.from_numpy(
                self.latest_image.transpose(2, 0, 1)
            ).float().unsqueeze(0) / 255.0

            # Run AI model
            with torch.no_grad():
                velocities = self.nav_model(laser_tensor, image_tensor)

            # Extract commands
            linear_vel = float(torch.tanh(velocities[0, 0]).item())
            angular_vel = float(torch.tanh(velocities[0, 1]).item())

            # Publish command
            cmd = Twist()
            cmd.linear.x = linear_vel * 0.5  # Scale down for safety
            cmd.angular.z = angular_vel * 0.5
            self.cmd_vel_pub.publish(cmd)

            # Publish status
            status = String()
            status.data = f'AI Nav: lin={linear_vel:.2f}, ang={angular_vel:.2f}'
            self.status_pub.publish(status)

        except Exception as e:
            self.get_logger().error(f'Navigation decision error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = AINavigationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down AI Navigation Node...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Evaluation Checkpoints

1. How does rclpy enable integration between AI agents and ROS2 systems?
2. What are the key components of an AI agent in a robotics context?
3. How can you optimize AI model performance for real-time robotics applications?
4. What are the differences between using services vs. actions for AI capabilities?
5. How do memory systems enhance AI agent performance in robotics?

## Troubleshooting AI Integration Issues

### Performance Issues
- **Slow inference**: Use model quantization, pruning, or specialized hardware
- **Memory leaks**: Properly manage tensor lifecycle and use context managers
- **Timing violations**: Optimize model architecture and use appropriate QoS settings

### Communication Issues
- **Message delays**: Use appropriate QoS settings for different data types
- **Data synchronization**: Implement proper buffering and timestamping
- **Bandwidth limitations**: Compress data or reduce update rates appropriately

### Model Issues
- **Inconsistent predictions**: Ensure proper input normalization and preprocessing
- **Model drift**: Implement online learning or periodic retraining
- **Overfitting to simulation**: Use domain randomization and real-world fine-tuning

## Summary

This chapter explored the integration of AI agents with ROS2 using the rclpy Python client library. We covered the architecture of AI agents in robotics, performance optimization techniques, and implementation of AI-powered services and actions.

The integration of AI with ROS2 enables humanoid robots to exhibit intelligent behaviors that adapt to changing environments and tasks. By leveraging the communication infrastructure of ROS2 and the flexibility of Python-based AI frameworks, we can create sophisticated robotic systems that combine the best of both worlds.

In the next chapter, we'll explore URDF (Unified Robot Description Format) and how to model humanoid robots for simulation and control in ROS2.