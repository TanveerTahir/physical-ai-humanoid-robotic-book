---
title: Sensors, State Estimation & Perception
sidebar_position: 3
description: Understanding sensors, state estimation techniques, and perception for humanoid robotics
gpu_notes: This chapter requires GPU for perception algorithms; minimum 6GB VRAM recommended for vision processing
jetson_notes: Jetson AGX Xavier or higher recommended for real-time perception; Jetson Nano can run simplified examples
---

# Sensors, State Estimation & Perception

## Prerequisites

Before studying this chapter, you should have:
- Understanding of basic AI and robotics concepts (from Chapters 1-2)
- Knowledge of probability and statistics basics
- Elementary understanding of linear algebra (vectors, matrices)
- Basic familiarity with signal processing concepts
- Some programming experience in Python

## Learning Objectives

By the end of this chapter, you should be able to:
- Identify different types of sensors used in humanoid robotics
- Explain state estimation techniques including filtering methods
- Understand perception challenges in humanoid robotics
- Apply sensor fusion techniques to improve state estimation
- Evaluate the impact of sensor noise on humanoid robot performance

## Introduction

Sensors, state estimation, and perception form the foundation of any autonomous physical system. For humanoid robots, these systems are particularly challenging due to the complexity of human-like sensing requirements and the need for real-time processing of multi-modal sensor data. This chapter explores the fundamental concepts and techniques used in humanoid robot sensing and perception.

## Types of Sensors in Humanoid Robotics

Humanoid robots require various types of sensors to perceive and interact with their environment effectively:

### Proprioceptive Sensors
These sensors measure internal robot state:

#### Joint Encoders
- Measure joint angles with high precision
- Critical for kinematic control
- Typically optical or magnetic encoders
- Sample rate: 100Hz-1kHz

#### Inertial Measurement Units (IMUs)
- Measure linear acceleration and angular velocity
- Essential for balance and orientation
- Include accelerometers, gyroscopes, and sometimes magnetometers
- Sample rate: 100Hz-1kHz

#### Force/Torque Sensors
- Measure contact forces and torques
- Critical for manipulation and locomotion
- Located at joints or in end-effectors
- Sample rate: 100Hz-2kHz

### Exteroceptive Sensors
These sensors measure the external environment:

#### Vision Sensors
- RGB cameras for color vision
- Depth cameras for 3D information
- Stereo cameras for depth perception
- Sample rate: 30Hz-60Hz for standard cameras

#### Range Sensors
- LIDAR for precise distance measurements
- Ultrasonic sensors for proximity detection
- Infrared sensors for short-range detection
- Sample rate: 5Hz-20Hz for LIDAR

#### Tactile Sensors
- Measure contact forces and textures
- Important for manipulation tasks
- Located in fingertips and palms
- Sample rate: 100Hz-500Hz

## State Estimation Fundamentals

State estimation is the process of determining the robot's state (position, velocity, orientation, etc.) from sensor measurements. This is challenging due to sensor noise, bias, and the dynamic nature of humanoid robots.

### The State Estimation Problem

For a humanoid robot, the state vector might include:
- Joint positions and velocities
- Base position and orientation
- Base linear and angular velocities
- Center of mass position and velocity

Mathematically, we want to estimate the state x at time t given all measurements up to time t:

```
p(x_t | z_1:t, u_1:t)
```

Where:
- z_1:t are all measurements up to time t
- u_1:t are all control inputs up to time t

### Filtering Approaches

#### Kalman Filter
The Kalman Filter is optimal for linear systems with Gaussian noise:

```python
import numpy as np

class KalmanFilter:
    def __init__(self, state_dim, measurement_dim):
        self.state_dim = state_dim
        self.measurement_dim = measurement_dim

        # State vector [position, velocity]
        self.x = np.zeros(state_dim)

        # Covariance matrix
        self.P = np.eye(state_dim) * 1000

        # Process and measurement noise
        self.Q = np.eye(state_dim) * 0.1
        self.R = np.eye(measurement_dim) * 1.0

        # State transition and measurement matrices
        self.F = np.eye(state_dim)  # Will be updated based on dynamics
        self.H = np.zeros((measurement_dim, state_dim))  # Will be set based on measurement model

    def predict(self, dt):
        """Prediction step"""
        # Update state transition matrix based on time step
        self.F[0, 1] = dt  # position += velocity * dt

        # Predict state
        self.x = self.F @ self.x

        # Predict covariance
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, z):
        """Update step"""
        # Innovation
        y = z - self.H @ self.x

        # Innovation covariance
        S = self.H @ self.P @ self.H.T + self.R

        # Kalman gain
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update state
        self.x = self.x + K @ y

        # Update covariance
        I_KH = np.eye(self.state_dim) - K @ self.H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R @ K.T
```

#### Extended Kalman Filter (EKF)
For nonlinear systems, the EKF linearizes around the current state:

```python
class ExtendedKalmanFilter:
    def __init__(self, state_dim, measurement_dim):
        self.state_dim = state_dim
        self.measurement_dim = measurement_dim
        self.x = np.zeros(state_dim)
        self.P = np.eye(state_dim) * 1000
        self.Q = np.eye(state_dim) * 0.1
        self.R = np.eye(measurement_dim) * 1.0

    def predict(self, dt):
        """Nonlinear prediction step"""
        # Compute Jacobian of motion model
        F = self.compute_motion_jacobian(self.x, dt)

        # Predict state using nonlinear model
        self.x = self.motion_model(self.x, dt)

        # Predict covariance
        self.P = F @ self.P @ F.T + self.Q

    def update(self, z):
        """Nonlinear update step"""
        # Compute Jacobian of measurement model
        H = self.compute_measurement_jacobian(self.x)

        # Innovation
        y = z - self.measurement_model(self.x)

        # Innovation covariance
        S = H @ self.P @ H.T + self.R

        # Kalman gain
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update state
        self.x = self.x + K @ y

        # Update covariance
        I_KH = np.eye(self.state_dim) - K @ H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R @ K.T

    def motion_model(self, x, dt):
        """Nonlinear motion model - example for 2D position and velocity"""
        new_x = x.copy()
        new_x[0] += x[2] * dt  # x position += x velocity * dt
        new_x[1] += x[3] * dt  # y position += y velocity * dt
        new_x[2] += 0  # x velocity (assuming no acceleration for simplicity)
        new_x[3] += 0  # y velocity
        return new_x

    def compute_motion_jacobian(self, x, dt):
        """Jacobian of motion model"""
        F = np.eye(self.state_dim)
        F[0, 2] = dt  # dx/dx_vel = dt
        F[1, 3] = dt  # dy/dy_vel = dt
        return F

    def measurement_model(self, x):
        """Nonlinear measurement model"""
        return x[:2]  # Measure position only

    def compute_measurement_jacobian(self, x):
        """Jacobian of measurement model"""
        H = np.zeros((2, self.state_dim))
        H[0, 0] = 1  # dx/dx = 1
        H[1, 1] = 1  # dy/dy = 1
        return H
```

#### Particle Filter
For highly nonlinear systems with non-Gaussian noise:

```python
class ParticleFilter:
    def __init__(self, state_dim, num_particles=1000):
        self.state_dim = state_dim
        self.num_particles = num_particles

        # Initialize particles
        self.particles = np.random.normal(0, 1, (num_particles, state_dim))
        self.weights = np.ones(num_particles) / num_particles

    def predict(self, control_input, noise_std):
        """Predict step - propagate particles forward"""
        for i in range(self.num_particles):
            # Apply motion model with noise
            self.particles[i] = self.motion_model(
                self.particles[i], control_input, noise_std
            )

    def update(self, measurement, measurement_std):
        """Update step - reweight particles based on measurement"""
        for i in range(self.num_particles):
            # Calculate likelihood of measurement given particle state
            predicted_measurement = self.measurement_model(self.particles[i])
            likelihood = self.gaussian_likelihood(
                measurement, predicted_measurement, measurement_std
            )
            self.weights[i] *= likelihood

        # Normalize weights
        self.weights += 1e-300  # Avoid numerical issues
        self.weights /= np.sum(self.weights)

    def resample(self):
        """Resample particles based on weights"""
        # Systematic resampling
        indices = self.systematic_resample()
        self.particles = self.particles[indices]
        self.weights = np.ones(self.num_particles) / self.num_particles

    def estimate(self):
        """Calculate state estimate from particles"""
        return np.average(self.particles, axis=0, weights=self.weights)

    def systematic_resample(self):
        """Systematic resampling algorithm"""
        cumulative_sum = np.cumsum(self.weights)
        start = np.random.uniform(0, 1/self.num_particles)
        indices = []
        i, j = 0, 0
        while i < self.num_particles:
            if start + i / self.num_particles < cumulative_sum[j]:
                indices.append(j)
                i += 1
            else:
                j += 1
        return np.array(indices)

    def motion_model(self, state, control, noise_std):
        """Simple motion model with noise"""
        new_state = state.copy()
        new_state += np.random.normal(0, noise_std, size=state.shape)
        return new_state

    def measurement_model(self, state):
        """Simple measurement model"""
        return state  # Direct measurement

    def gaussian_likelihood(self, measurement, predicted, std):
        """Calculate Gaussian likelihood"""
        diff = measurement - predicted
        return np.exp(-0.5 * np.sum((diff/std)**2))
```

## Sensor Fusion

Sensor fusion combines data from multiple sensors to improve state estimation:

### Kalman Filter Sensor Fusion
```python
class SensorFusionKF:
    def __init__(self):
        # State: [x, y, z, vx, vy, vz, qw, qx, qy, qz]
        # Position, velocity, and orientation (quaternion)
        self.state_dim = 10
        self.x = np.zeros(self.state_dim)
        self.x[6] = 1  # Initialize quaternion to [1, 0, 0, 0] (no rotation)

        self.P = np.eye(self.state_dim) * 1000
        self.Q = np.eye(self.state_dim) * 0.01

        # Measurement noise for different sensors
        self.R_imu = np.eye(6) * 0.01  # Accel + Gyro
        self.R_vision = np.eye(7) * 0.1  # Position + Orientation
        self.R_encoders = np.eye(3) * 0.001  # Joint positions

    def fuse_imu_vision(self, imu_data, vision_data):
        """Fusion of IMU and vision data"""
        # First, predict using IMU data (gyroscope)
        self.predict_imu(imu_data['gyro'])

        # Then, update using vision data (more accurate position)
        self.update_vision(vision_data)

        # Occasionally, update using encoder data
        if self.should_update_encoders():
            self.update_encoders()

    def predict_imu(self, gyro_data):
        """Prediction using gyroscope data"""
        # Convert gyro to quaternion derivative
        omega_quat = np.array([0, gyro_data[0], gyro_data[1], gyro_data[2]])
        quat = self.x[6:10]

        # Quaternion derivative
        quat_dot = 0.5 * self.quat_multiply(omega_quat, quat)

        # Update quaternion in state
        self.x[6:10] += quat_dot * 0.01  # 100Hz IMU

        # Normalize quaternion
        self.x[6:10] /= np.linalg.norm(self.x[6:10])

    def quat_multiply(self, q1, q2):
        """Quaternion multiplication"""
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        w = w1*w2 - x1*x2 - y1*y2 - z1*z2
        x = w1*x2 + x1*w2 + y1*z2 - z1*y2
        y = w1*y2 - x1*z2 + y1*w2 + z1*x2
        z = w1*z2 + x1*y2 - y1*x2 + z1*w2
        return np.array([w, x, y, z])
```

## Perception in Humanoid Robotics

Perception for humanoid robots involves processing multi-modal sensor data to understand the environment and the robot's state within it.

### Visual Perception

Visual perception is critical for humanoid robots to navigate and interact with human environments:

```python
import cv2
import numpy as np

class VisualPerception:
    def __init__(self):
        self.feature_detector = cv2.ORB_create()
        self.matcher = cv2.BFMatcher()
        self.position_estimator = None  # Will be initialized with camera params

    def detect_objects(self, image):
        """Detect objects in the image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect features
        keypoints, descriptors = self.feature_detector.detectAndCompute(gray, None)

        # Classify objects (simplified)
        objects = []
        for kp in keypoints:
            # In a real system, this would use a trained classifier
            if self.is_person(kp.pt, gray):
                objects.append({'type': 'person', 'position': kp.pt})
            elif self.is_obstacle(kp.pt, gray):
                objects.append({'type': 'obstacle', 'position': kp.pt})

        return objects

    def estimate_depth(self, stereo_images):
        """Estimate depth from stereo images"""
        left_img = stereo_images['left']
        right_img = stereo_images['right']

        # Convert to grayscale
        left_gray = cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY)

        # Compute disparity
        stereo = cv2.StereoSGBM_create(
            minDisparity=0,
            numDisparities=96,
            blockSize=11,
            P1=8 * 3 * 11**2,
            P2=32 * 3 * 11**2
        )

        disparity = stereo.compute(left_gray, right_gray).astype(np.float32) / 16.0

        # Convert disparity to depth
        baseline = 0.1  # Camera baseline in meters
        focal_length = 800  # Focal length in pixels
        depth = (baseline * focal_length) / (disparity + 1e-6)

        return depth

    def is_person(self, point, image):
        """Simple person detection (in practice, use a trained model)"""
        # This is a placeholder - in reality, use a CNN or HOG descriptor
        return False

    def is_obstacle(self, point, image):
        """Simple obstacle detection"""
        # This is a placeholder
        return False
```

### Multi-Modal Perception

Humanoid robots must integrate information from multiple sensors:

```python
class MultiModalPerception:
    def __init__(self):
        self.vision_system = VisualPerception()
        self.lidar_system = self.initialize_lidar()
        self.tactile_system = self.initialize_tactile()

    def perceive_environment(self, sensor_data):
        """Integrate data from multiple sensors"""
        # Process visual data
        visual_info = self.process_vision(sensor_data['camera'])

        # Process LIDAR data
        lidar_info = self.process_lidar(sensor_data['lidar'])

        # Process tactile data
        tactile_info = self.process_tactile(sensor_data['tactile'])

        # Fuse information
        fused_perception = self.fuse_modalities(visual_info, lidar_info, tactile_info)

        return fused_perception

    def process_vision(self, camera_data):
        """Process visual information"""
        objects = self.vision_system.detect_objects(camera_data)
        return {'objects': objects}

    def process_lidar(self, lidar_data):
        """Process LIDAR information"""
        # Convert to occupancy grid
        occupancy_grid = self.lidar_to_grid(lidar_data)
        return {'occupancy_grid': occupancy_grid}

    def process_tactile(self, tactile_data):
        """Process tactile information"""
        contact_points = self.extract_contact_points(tactile_data)
        return {'contacts': contact_points}

    def fuse_modalities(self, visual, lidar, tactile):
        """Fuse information from different modalities"""
        # Create unified representation
        unified_map = {
            'static_objects': self.merge_static_objects(visual['objects'], lidar['occupancy_grid']),
            'dynamic_objects': visual['objects'],  # Objects that move
            'contact_points': tactile['contacts'],
            'navigation_map': lidar['occupancy_grid']
        }

        return unified_map
```

## Challenges in Humanoid Perception

### Computational Constraints
Humanoid robots have limited computational resources, especially when running on embedded systems like NVIDIA Jetson:

```python
class EfficientPerception:
    def __init__(self, hardware_target="jetson_nano"):
        self.hardware_target = hardware_target
        self.computation_budget = self.get_computation_budget()

    def get_computation_budget(self):
        """Get computation budget based on hardware"""
        budgets = {
            "gpu_workstation": 100.0,  # Relative units
            "jetson_agx": 30.0,
            "jetson_xavier": 20.0,
            "jetson_nano": 5.0
        }
        return budgets.get(self.hardware_target, 5.0)

    def adaptive_perception(self, sensor_data):
        """Adjust perception complexity based on available computation"""
        if self.computation_budget < 10.0:
            # Use simplified perception
            return self.simple_perception(sensor_data)
        elif self.computation_budget < 30.0:
            # Use moderate perception
            return self.moderate_perception(sensor_data)
        else:
            # Use full perception
            return self.full_perception(sensor_data)

    def simple_perception(self, sensor_data):
        """Lightweight perception algorithm"""
        # Use fast, approximate methods
        pass

    def moderate_perception(self, sensor_data):
        """Moderate perception algorithm"""
        # Use balanced approach
        pass

    def full_perception(self, sensor_data):
        """Full perception algorithm"""
        # Use all available sensors and methods
        pass
```

### Real-Time Requirements
Perception systems must operate in real-time:

```python
import time

class RealTimePerception:
    def __init__(self, target_frequency=30):  # 30 Hz for vision
        self.target_period = 1.0 / target_frequency
        self.last_process_time = time.time()

    def process_frame(self, sensor_data):
        """Process frame with real-time constraints"""
        start_time = time.time()

        # Perform perception
        result = self.perception_algorithm(sensor_data)

        # Calculate processing time
        processing_time = time.time() - start_time

        # Check if we're meeting real-time requirements
        if processing_time > self.target_period:
            print(f"Warning: Processing took {processing_time:.3f}s, target {self.target_period:.3f}s")

        return result

    def perception_algorithm(self, sensor_data):
        """Main perception algorithm"""
        # Implementation here
        pass
```

## Evaluation Checkpoints

1. What are the different types of sensors used in humanoid robotics?
2. How do Kalman Filters, Extended Kalman Filters, and Particle Filters differ in their applications?
3. What is sensor fusion and why is it important for humanoid robots?
4. What are the main challenges in implementing perception for humanoid robots?
5. How do computational constraints affect perception system design?

## Hands-on Lab: Simple State Estimation

Implement a simple state estimation system:

```python
import numpy as np
import matplotlib.pyplot as plt

# Simulate a simple humanoid robot moving in 2D
class SimpleHumanoid:
    def __init__(self):
        # State: [x, y, vx, vy]
        self.state = np.array([0.0, 0.0, 0.1, 0.05])  # Start with small velocity
        self.dt = 0.01  # 100 Hz control rate

    def step(self, control_input):
        """Update state with dynamics"""
        # Add some process noise
        noise = np.random.normal(0, 0.001, size=4)

        # Simple dynamics: position += velocity * dt
        self.state[0] += self.state[2] * self.dt
        self.state[1] += self.state[3] * self.dt

        # Add control input to velocity
        self.state[2] += control_input[0] * self.dt
        self.state[3] += control_input[1] * self.dt

        # Add noise
        self.state += noise

        return self.state.copy()

    def get_noisy_measurement(self):
        """Get noisy measurement of position"""
        true_position = self.state[:2]
        noise = np.random.normal(0, 0.02, size=2)  # 2cm measurement noise
        return true_position + noise

# Run simulation
robot = SimpleHumanoid()
kf = KalmanFilter(state_dim=4, measurement_dim=2)

# Measurement matrix (we only measure position, not velocity)
kf.H = np.array([
    [1, 0, 0, 0],  # Measure x position
    [0, 1, 0, 0]   # Measure y position
])

# Set process model (constant velocity model)
dt = 0.01
kf.F = np.array([
    [1, 0, dt, 0],   # x = x + vx*dt
    [0, 1, 0, dt],   # y = y + vy*dt
    [0, 0, 1, 0],    # vx = vx
    [0, 0, 0, 1]     # vy = vy
])

# Initial state (we'll start with zero and let filter learn)
kf.x = np.array([0, 0, 0, 0])

# Store trajectories for plotting
true_trajectory = []
measured_trajectory = []
estimated_trajectory = []

for i in range(500):  # 5 seconds of simulation
    # Apply a simple control (go in a circle)
    control = np.array([0.01 * np.sin(i*0.02), 0.01 * np.cos(i*0.02)])

    # Step the robot
    true_state = robot.step(control)

    # Get noisy measurement
    measurement = robot.get_noisy_measurement()

    # Update Kalman filter
    kf.predict(dt)
    kf.update(measurement)

    # Store trajectories
    true_trajectory.append(true_state[:2].copy())
    measured_trajectory.append(measurement.copy())
    estimated_trajectory.append(kf.x[:2].copy())

true_trajectory = np.array(true_trajectory)
measured_trajectory = np.array(measured_trajectory)
estimated_trajectory = np.array(estimated_trajectory)

print(f"Final position - True: {true_trajectory[-1]}, Measured: {measured_trajectory[-1]}, Estimated: {estimated_trajectory[-1]}")
print(f"Estimation error: {np.linalg.norm(true_trajectory[-1] - estimated_trajectory[-1]):.3f}")
```

## Summary

Sensors, state estimation, and perception are fundamental to humanoid robotics. The multi-modal nature of humanoid sensing requires sophisticated fusion techniques to create coherent understanding of the robot's state and environment. Challenges include computational constraints, real-time requirements, and sensor noise.

Understanding these concepts is essential for building humanoid robots that can effectively perceive and interact with their environment. The next chapter will explore the high-level system architecture that integrates these perception capabilities into a complete humanoid robot system.