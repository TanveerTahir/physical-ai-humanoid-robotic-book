---
title: Simulating Physics & Sensors
sidebar_position: 2
description: Understanding physics simulation and sensor modeling in Gazebo for humanoid robotics
gpu_notes: This chapter requires GPU for physics simulation; minimum 6GB VRAM recommended for complex physics
jetson_notes: Jetson AGX Xavier recommended for complex physics simulation; Jetson Nano limited to basic examples
---

# Simulating Physics & Sensors

## Prerequisites

Before studying this chapter, you should have:
- Understanding of Gazebo basics (from Chapter 9)
- Knowledge of ROS2 concepts and communication patterns
- Basic understanding of physics concepts (forces, torques, friction)
- Experience with sensor types in robotics (cameras, lidars, IMUs)
- Familiarity with URDF/SDF model formats

## Learning Objectives

By the end of this chapter, you should be able to:
- Configure realistic physics properties for humanoid robots in Gazebo
- Model and simulate various types of sensors with realistic noise characteristics
- Implement proper collision detection and contact handling
- Validate physics simulation against real-world robot behavior
- Optimize simulation parameters for performance and accuracy

## Introduction

Physics simulation and sensor modeling are critical components of effective humanoid robot simulation. The quality of physics simulation directly impacts the realism of robot behavior, while accurate sensor simulation is essential for developing robust perception and control algorithms. This chapter explores how to configure Gazebo to provide realistic simulation of both physical interactions and sensor data.

For humanoid robots, physics simulation becomes particularly important because these robots must interact with the environment through complex contact points (feet, hands) and must maintain balance while performing dynamic movements. Accurate simulation of these interactions is essential for developing effective control strategies.

## Physics Engine Configuration

### Understanding Gazebo's Physics Engines

Gazebo supports multiple physics engines, each with different strengths:

1. **ODE (Open Dynamics Engine)**: Default engine, good balance of performance and accuracy
2. **Bullet**: Good for complex contact scenarios
3. **DART**: Advanced constraint handling, good for articulated systems

### Physics Parameters in SDFormat

The physics configuration determines how objects behave in the simulation:

```xml
<physics name="ode_physics" type="ode">
  <!-- Gravity vector (x, y, z) -->
  <gravity>0 0 -9.8</gravity>

  <!-- Solver settings -->
  <ode>
    <solver>
      <!-- Type of solver: quick, world, dantzig, pgs -->
      <type>quick</type>
      <!-- Number of iterations for constraint solving -->
      <iters>10</iters>
      <!-- SOR over-relaxation parameter -->
      <sor>1.3</sor>
      <!-- Constraint error reduction parameter -->
      <cfm>0.0</cfm>
      <!-- Constraint force mixing parameter -->
      <erp>0.2</erp>
    </solver>

    <!-- Constraint settings -->
    <constraints>
      <!-- Minimum contact penetration -->
      <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      <!-- Maximum contact penetration correction -->
      <contact_surface_layer>0.001</contact_surface_layer>
    </constraints>
  </ode>

  <!-- Simulation time settings -->
  <max_step_size>0.001</max_step_size>  <!-- 1ms physics steps -->
  <real_time_factor>1.0</real_time_factor>  <!-- Real-time simulation -->
  <real_time_update_rate>1000</real_time_update_rate>  <!-- 1000 Hz physics updates -->
</physics>
```

### Tuning Physics Parameters for Humanoid Robots

Humanoid robots have specific requirements for physics simulation:

```xml
<physics name="humanoid_physics" type="ode">
  <gravity>0 0 -9.8</gravity>

  <ode>
    <solver>
      <type>quick</type>
      <iters>20</iters>  <!-- More iterations for stability with contacts -->
      <sor>1.2</sor>     <!-- Slightly higher for stability -->
      <cfm>0.000001</cfm>  <!-- Very low CFM for precise contacts -->
      <erp>0.1</erp>     <!-- Lower ERP for more precise contacts -->
    </solver>

    <constraints>
      <contact_max_correcting_vel>10.0</contact_max_correcting_vel>  <!-- Lower for stability -->
      <contact_surface_layer>0.0005</contact_surface_layer>  <!-- Thin layer for precise contacts -->
    </constraints>
  </ode>

  <!-- Use smaller step size for humanoid stability -->
  <max_step_size>0.0005</max_step_size>  <!-- 0.5ms for better stability -->
  <real_time_factor>0.5</real_time_factor>  <!-- May need to slow down for stability -->
  <real_time_update_rate>2000</real_time_update_rate>
</physics>
```

## Material Properties and Surface Interactions

### Material Definitions

Realistic material properties are crucial for accurate simulation:

```xml
<!-- In a world file or model -->
<world name="humanoid_world">
  <!-- Define materials with realistic properties -->

  <!-- Concrete floor for walking -->
  <material name="concrete">
    <pbr>
      <metal>
        <albedo_map>materials/textures/concrete.png</albedo_map>
        <normal_map>materials/textures/concrete_normal.png</normal_map>
        <roughness_map>materials/textures/concrete_roughness.png</roughness_map>
      </metal>
    </pbr>
  </material>

  <!-- Rubber for robot feet -->
  <material name="rubber">
    <pbr>
      <metal>
        <albedo_map>materials/textures/rubber.png</albedo_map>
        <roughness>0.8</roughness>
        <metalness>0.1</metalness>
      </metal>
    </pbr>
  </material>
</world>
```

### Friction Modeling

Proper friction modeling is critical for humanoid locomotion:

```xml
<!-- In a robot model's collision element -->
<collision name="foot_collision">
  <geometry>
    <box>
      <size>0.15 0.1 0.02</size>  <!-- Foot dimensions -->
    </box>
  </geometry>

  <surface>
    <friction>
      <!-- ODE friction model -->
      <ode>
        <!-- Primary friction coefficient (forward/backward) -->
        <mu>0.8</mu>
        <!-- Secondary friction coefficient (sideways) -->
        <mu2>0.7</mu2>
        <!-- Direction of primary friction -->
        <fdir1>1 0 0</fdir1>
        <!-- Slip parameters for more realistic sliding -->
        <slip1>0.0</slip1>
        <slip2>0.0</slip2>
      </ode>

      <!-- Bullet friction model -->
      <bullet>
        <friction>0.8</friction>
        <friction2>0.7</friction2>
        <fdir1>1 0 0</fdir1>
        <rolling_friction>0.01</rolling_friction>
      </bullet>
    </friction>

    <!-- Contact behavior -->
    <contact>
      <ode>
        <!-- Constraint Force Mixing parameter -->
        <soft_cfm>0.0</soft_cfm>
        <!-- Error Reduction Parameter -->
        <soft_erp>0.2</soft_erp>
        <!-- Spring stiffness parameter -->
        <kp>1e+13</kp>
        <!-- Damping coefficient -->
        <kd>1</kd>
        <!-- Maximum velocity for contact correction -->
        <max_vel>100.0</max_vel>
        <!-- Minimum depth for contact detection -->
        <min_depth>0.0</min_depth>
      </ode>
    </contact>

    <!-- Bounce behavior -->
    <bounce>
      <restitution_coefficient>0.1</restitution_coefficient>
      <threshold>100000</threshold>
    </bounce>
  </surface>
</collision>
```

## Sensor Simulation

### Camera Sensors

Camera sensors in Gazebo provide realistic image simulation:

```xml
<sensor name="head_camera" type="camera">
  <pose>0.1 0 0.05 0 0 0</pose>  <!-- Offset from parent link -->
  <camera>
    <!-- Field of view -->
    <horizontal_fov>1.047</horizontal_fov>  <!-- ~60 degrees -->

    <!-- Image properties -->
    <image>
      <width>640</width>
      <height>480</height>
      <format>R8G8B8</format>  <!-- RGB format -->
    </image>

    <!-- Anti-aliasing -->
    <anti_aliasing>2</anti_aliasing>

    <!-- Lens distortion -->
    <lens>
      <type>stereographic</type>
      <scale_to_hfov>true</scale_to_hfov>
      <cutoff_angle>1.5707</cutoff_angle>
      <env_texture_size>512</env_texture_size>
      <intrinsics>
        <fx>320</fx>
        <fy>320</fy>
        <cx>320</cx>
        <cy>240</cy>
        <s>0</s>  <!-- Skew -->
      </intrinsics>
      <distortion>
        <k1>0</k1>
        <k2>0</k2>
        <k3>0</k3>
        <p1>0</p1>
        <p2>0</p2>
      </distortion>
    </lens>

    <!-- Clipping distances -->
    <clip>
      <near>0.1</near>
      <far>10.0</far>
    </clip>
  </camera>

  <!-- Update settings -->
  <always_on>true</always_on>
  <update_rate>30</update_rate>
  <visualize>true</visualize>
</sensor>
```

### IMU Sensors

IMU sensors are crucial for humanoid balance and navigation:

```xml
<sensor name="imu_sensor" type="imu">
  <pose>0 0 0 0 0 0</pose>
  <topic>imu/data</topic>

  <update_rate>100</update_rate>  <!-- 100 Hz for IMU -->

  <imu>
    <!-- Linear acceleration noise -->
    <linear_acceleration>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0175</stddev>  <!-- ~0.1 m/s² (typical for IMU) -->
          <bias_mean>0.0000075</bias_mean>
          <bias_stddev>0.0000008</bias_stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0175</stddev>
          <bias_mean>0.0000075</bias_mean>
          <bias_stddev>0.0000008</bias_stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0175</stddev>
          <bias_mean>0.0000075</bias_mean>
          <bias_stddev>0.0000008</bias_stddev>
        </noise>
      </z>
    </linear_acceleration>

    <!-- Angular velocity noise -->
    <angular_velocity>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0014</stddev>  <!-- ~0.008 rad/s (typical for IMU) -->
          <bias_mean>0.000000075</bias_mean>
          <bias_stddev>0.00000008</bias_stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0014</stddev>
          <bias_mean>0.000000075</bias_mean>
          <bias_stddev>0.00000008</bias_stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.0014</stddev>
          <bias_mean>0.000000075</bias_mean>
          <bias_stddev>0.00000008</bias_stddev>
        </noise>
      </z>
    </angular_velocity>

    <!-- Orientation noise (usually minimal) -->
    <orientation>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.001</stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.001</stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.001</stddev>
        </noise>
      </z>
    </orientation>
  </imu>

  <always_on>true</always_on>
  <visualize>false</visualize>
</sensor>
```

### Force/Torque Sensors

Force/torque sensors are important for contact detection and manipulation:

```xml
<sensor name="ft_sensor_left_foot" type="force_torque">
  <pose>0 0 0 0 0 0</pose>
  <update_rate>1000</update_rate>  <!-- High rate for contact detection -->

  <force_torque>
    <frame>child</frame>  <!-- Measure in child frame -->
    <measure_direction>child_to_parent</measure_direction>

    <!-- Noise models for realistic sensor behavior -->
    <force>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.5</stddev>  <!-- 0.5N typical for force sensors -->
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.1</bias_stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.5</stddev>
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.1</bias_stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.5</stddev>
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.1</bias_stddev>
        </noise>
      </z>
    </force>

    <torque>
      <x>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.1</stddev>  <!-- 0.1Nm typical for torque sensors -->
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.01</bias_stddev>
        </noise>
      </x>
      <y>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.1</stddev>
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.01</bias_stddev>
        </noise>
      </y>
      <z>
        <noise type="gaussian">
          <mean>0.0</mean>
          <stddev>0.1</stddev>
          <bias_mean>0.0</bias_mean>
          <bias_stddev>0.01</bias_stddev>
        </noise>
      </z>
    </torque>
  </force_torque>

  <always_on>true</always_on>
  <visualize>false</visualize>
</sensor>
```

## Advanced Physics Concepts

### Joint Dynamics

Proper joint dynamics modeling is essential for realistic robot behavior:

```xml
<joint name="knee_joint" type="revolute">
  <parent>thigh_link</parent>
  <child>shin_link</child>
  <axis>
    <xyz>0 1 0</xyz>  <!-- Rotate around Y axis -->

    <!-- Joint limits -->
    <limit>
      <lower>-2.0</lower>  <!-- -114 degrees -->
      <upper>0.5</upper>   <!-- 28 degrees -->
      <effort>300</effort>  <!-- 300 Nm max torque -->
      <velocity>5</velocity>  <!-- 5 rad/s max velocity -->
    </limit>

    <!-- Dynamics properties -->
    <dynamics>
      <damping>1.0</damping>    <!-- Viscous damping -->
      <friction>0.1</friction>  <!-- Coulomb friction -->
      <spring_reference>0</spring_reference>  <!-- Rest position for spring -->
      <spring_stiffness>0</spring_stiffness>  <!-- Spring constant -->
    </dynamics>

    <!-- Safety controller -->
    <safety_controller>
      <k_velocity>10</k_velocity>  <!-- Velocity scaling factor -->
    </safety_controller>
  </axis>
</joint>
```

### Contact Modeling for Humanoid Locomotion

Humanoid robots require special attention to contact modeling for stable walking:

```xml
<!-- In the foot link collision element -->
<collision name="left_foot_collision">
  <geometry>
    <mesh>
      <uri>model://humanoid_robot/meshes/left_foot.stl</uri>
    </mesh>
  </geometry>

  <surface>
    <friction>
      <ode>
        <mu>0.8</mu>    <!-- High friction for stable walking -->
        <mu2>0.8</mu2>
        <fdir1>0 0 1</fdir1>  <!-- Direction for primary friction -->
      </ode>
    </friction>

    <contact>
      <ode>
        <soft_cfm>0.0001</soft_cfm>  <!-- Very stiff contacts -->
        <soft_erp>0.8</soft_erp>     <!-- High error reduction -->
        <kp>1000000000000.0</kp>    <!-- High stiffness -->
        <kd>1.0</kd>                <!-- Damping -->
        <max_vel>100.0</max_vel>     <!-- Max correction velocity -->
        <min_depth>0.001</min_depth> <!-- Minimum penetration -->
      </ode>
    </contact>

    <bounce>
      <restitution_coefficient>0.01</restitution_coefficient>  <!-- Very low bounce -->
      <threshold>100000</threshold>
    </bounce>
  </surface>
</collision>
```

## Sensor Fusion in Simulation

### Combining Multiple Sensors

In humanoid robots, multiple sensors are often combined for better state estimation:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from geometry_msgs.msg import Pose, Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
import numpy as np
from scipy.spatial.transform import Rotation as R

class SensorFusionNode(Node):
    """
    Demonstrate sensor fusion for humanoid state estimation in simulation
    """

    def __init__(self):
        super().__init__('sensor_fusion_node')

        # Subscribers for different sensors
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10
        )
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, 10
        )

        # Publisher for fused state
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # Internal state
        self.imu_orientation = np.array([0.0, 0.0, 0.0, 1.0])  # x, y, z, w
        self.imu_angular_velocity = np.array([0.0, 0.0, 0.0])
        self.imu_linear_acceleration = np.array([0.0, 0.0, 0.0])

        self.joint_positions = {}
        self.joint_velocities = {}

        # Timing
        self.prev_time = self.get_clock().now()

        # Covariance matrices (simplified)
        self.orientation_cov = np.eye(3) * 0.01  # 0.01 rad² uncertainty
        self.position_cov = np.eye(3) * 0.01    # 0.01 m² uncertainty

        self.get_logger().info('Sensor fusion node initialized')

    def imu_callback(self, msg):
        """Process IMU data"""
        # Extract orientation
        self.imu_orientation = np.array([
            msg.orientation.x,
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ])

        # Extract angular velocity
        self.imu_angular_velocity = np.array([
            msg.angular_velocity.x,
            msg.angular_velocity.y,
            msg.angular_velocity.z
        ])

        # Extract linear acceleration
        self.imu_linear_acceleration = np.array([
            msg.linear_acceleration.x,
            msg.linear_acceleration.y,
            msg.linear_acceleration.z
        ])

    def joint_state_callback(self, msg):
        """Process joint state data"""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]

            if i < len(msg.velocity):
                self.joint_velocities[name] = msg.velocity[i]

    def predict_position_from_joints(self):
        """Predict position based on forward kinematics (simplified)"""
        # This is a simplified example - in practice, use a kinematics library
        # like KDL or moveit for accurate forward kinematics

        # Example: Estimate center of mass position based on joint angles
        # This is highly simplified for demonstration
        com_x = 0.0
        com_y = 0.0
        com_z = 0.8  # Approximate height of COM

        # Adjust based on joint positions (simplified)
        if 'left_hip_pitch_joint' in self.joint_positions:
            hip_angle = self.joint_positions['left_hip_pitch_joint']
            com_z += 0.1 * np.sin(hip_angle)  # Simplified effect of hip angle

        if 'right_hip_pitch_joint' in self.joint_positions:
            hip_angle = self.joint_positions['right_hip_pitch_joint']
            com_z += 0.1 * np.sin(hip_angle)  # Simplified effect of hip angle

        return np.array([com_x, com_y, com_z])

    def update_odometry(self):
        """Fuse sensor data to estimate odometry"""
        current_time = self.get_clock().now()

        # Calculate time delta
        dt = (current_time.nanoseconds - self.prev_time.nanoseconds) / 1e9
        self.prev_time = current_time

        if dt <= 0:
            return

        # Predict position from joint integration (simplified)
        predicted_pos = self.predict_position_from_joints()

        # Integrate IMU acceleration to get velocity change
        # Note: This would drift significantly in real applications
        # but is acceptable for short-term simulation
        linear_acc_global = self.rotate_vector_to_global(
            self.imu_linear_acceleration,
            self.imu_orientation
        )

        # Remove gravity (approximate)
        linear_acc_global[2] -= 9.81

        # Update velocity (simplified integration)
        # In practice, use more sophisticated integration with drift correction
        velocity_change = linear_acc_global * dt

        # For this simulation, we'll use the predicted position from kinematics
        # as the primary source and IMU for orientation
        fused_pose = Pose()
        fused_pose.position.x = float(predicted_pos[0])
        fused_pose.position.y = float(predicted_pos[1])
        fused_pose.position.z = float(predicted_pos[2])

        # Use IMU orientation
        fused_pose.orientation.x = float(self.imu_orientation[0])
        fused_pose.orientation.y = float(self.imu_orientation[1])
        fused_pose.orientation.z = float(self.imu_orientation[2])
        fused_pose.orientation.w = float(self.imu_orientation[3])

        # Create odometry message
        odom_msg = Odometry()
        odom_msg.header.stamp = current_time.to_msg()
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_link'

        odom_msg.pose.pose = fused_pose
        # Set covariance (simplified)
        odom_msg.pose.covariance = list(self.orientation_cov.flatten()) + [0.0] * 3 + [0.0] * 3 + list(self.position_cov.flatten())

        # Publish odometry
        self.odom_pub.publish(odom_msg)

        # Publish transform
        self.publish_transform(odom_msg)

    def rotate_vector_to_global(self, vector, orientation):
        """Rotate a vector from body frame to global frame"""
        # Convert quaternion to rotation matrix
        rot = R.from_quat(orientation)  # x,y,z,w format
        return rot.apply(vector)

    def publish_transform(self, odom_msg):
        """Publish transform from odom to base_link"""
        t = TransformStamped()
        t.header.stamp = odom_msg.header.stamp
        t.header.frame_id = odom_msg.header.frame_id
        t.child_frame_id = odom_msg.child_frame_id

        t.transform.translation.x = odom_msg.pose.pose.position.x
        t.transform.translation.y = odom_msg.pose.pose.position.y
        t.transform.translation.z = odom_msg.pose.pose.position.z

        t.transform.rotation = odom_msg.pose.pose.orientation

        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)

    fusion_node = SensorFusionNode()

    # Timer to update odometry at a reasonable rate
    timer = fusion_node.create_timer(0.02, fusion_node.update_odometry)  # 50 Hz

    try:
        rclpy.spin(fusion_node)
    except KeyboardInterrupt:
        fusion_node.get_logger().info('Shutting down sensor fusion node...')
    finally:
        fusion_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Simulation Optimization Techniques

### Performance Optimization

Large humanoid robots with many degrees of freedom can strain simulation performance:

```python
# Performance optimization for humanoid simulation
import rclpy
from rclpy.node import Node
from gazebo_msgs.msg import ODEPhysics
from std_msgs.msg import Bool

class PhysicsOptimizer(Node):
    """
    Dynamically adjust physics parameters based on simulation complexity
    """

    def __init__(self):
        super().__init__('physics_optimizer')

        # Publisher for physics parameters
        self.physics_param_pub = self.create_publisher(ODEPhysics, '/gazebo/set_physics_properties', 10)

        # Subscriber for simulation status
        self.sim_status_sub = self.create_subscription(
            Bool, '/simulation_performance_ok', self.performance_callback, 10
        )

        # Timer for periodic optimization
        self.optimization_timer = self.create_timer(5.0, self.optimize_physics)

        # Track performance metrics
        self.performance_history = []

        self.get_logger().info('Physics optimizer initialized')

    def optimize_physics(self):
        """Adjust physics parameters based on performance"""
        # Analyze performance history
        if len(self.performance_history) > 10:
            avg_performance = sum(self.performance_history[-10:]) / len(self.performance_history[-10:])

            # Adjust parameters based on performance
            if avg_performance < 0.8:  # Below 80% real-time factor
                self.decrease_accuracy_increase_performance()
            elif avg_performance > 0.95:  # Above 95% - can afford more accuracy
                self.increase_accuracy_decrease_performance()

    def decrease_accuracy_increase_performance(self):
        """Decrease physics accuracy to improve performance"""
        physics_msg = ODEPhysics()

        # Larger step size
        physics_msg.max_step_size = 0.002  # 2ms instead of 1ms

        # Fewer solver iterations
        physics_msg.ode_config.solver_type = "quick"
        physics_msg.ode_config.iters = 10  # Reduced from 20
        physics_msg.ode_config.sor = 1.3

        # More relaxed constraints
        physics_msg.ode_config.cfm = 0.001
        physics_msg.ode_config.erp = 0.3

        # Publish new parameters
        self.physics_param_pub.publish(physics_msg)
        self.get_logger().info('Decreased physics accuracy for better performance')

    def increase_accuracy_decrease_performance(self):
        """Increase physics accuracy (may reduce performance)"""
        physics_msg = ODEPhysics()

        # Smaller step size
        physics_msg.max_step_size = 0.0005  # 0.5ms for better accuracy

        # More solver iterations
        physics_msg.ode_config.solver_type = "quick"
        physics_msg.ode_config.iters = 20  # Increased for stability
        physics_msg.ode_config.sor = 1.2

        # Stricter constraints
        physics_msg.ode_config.cfm = 0.000001
        physics_msg.ode_config.erp = 0.1

        # Publish new parameters
        self.physics_param_pub.publish(physics_msg)
        self.get_logger().info('Increased physics accuracy (performance may decrease)')

    def performance_callback(self, msg):
        """Receive performance feedback from simulation"""
        self.performance_history.append(msg.data)
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]