---
title: URDF for Humanoids
sidebar_position: 4
description: Creating and using Unified Robot Description Format for humanoid robots
gpu_notes: This chapter requires GPU for complex URDF simulation; minimum 6GB VRAM recommended for physics simulation
jetson_notes: Jetson AGX Xavier recommended for URDF processing; Jetson Nano can handle basic URDF visualization
---

# URDF for Humanoids

## Prerequisites

Before studying this chapter, you should have:
- Understanding of ROS2 fundamentals and communication patterns (from Chapters 5-6)
- Knowledge of rclpy binding with AI agents (from Chapter 7)
- Basic understanding of robotics kinematics and dynamics
- Familiarity with 3D modeling concepts
- Experience with XML file format

## Learning Objectives

By the end of this chapter, you should be able to:
- Create comprehensive URDF models for humanoid robots
- Understand the structure and components of URDF files
- Integrate URDF models with ROS2 simulation environments
- Configure physical properties and joint constraints for humanoid robots
- Optimize URDF models for efficient simulation and control

## Introduction

Unified Robot Description Format (URDF) is the standard for representing robot models in ROS2. For humanoid robots, URDF becomes particularly important as these robots have complex kinematic chains, numerous degrees of freedom, and intricate physical properties that must be accurately modeled for effective simulation and control.

Humanoid robots present unique challenges in URDF modeling due to their human-like structure with multiple limbs, complex joint arrangements, and balance requirements. This chapter explores how to create detailed and accurate URDF models that properly represent the physical and kinematic properties of humanoid robots.

## URDF Fundamentals

URDF is an XML-based format that describes robot models in terms of links, joints, and their relationships. A humanoid robot model typically includes:

- **Links**: Rigid bodies that make up the robot structure
- **Joints**: Connections between links that define degrees of freedom
- **Materials**: Visual properties for rendering
- **Gazebo plugins**: Simulation-specific properties

### Basic URDF Structure

```xml
<?xml version="1.0"?>
<robot name="humanoid_robot">
  <!-- Materials -->
  <material name="blue">
    <color rgba="0.0 0.0 0.8 1.0"/>
  </material>

  <!-- Links -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.5"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.5 0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.083" ixy="0.0" ixz="0.0" iyy="0.083" iyz="0.0" izz="0.083"/>
    </inertial>
  </link>

  <!-- Joints -->
  <joint name="base_to_head" type="fixed">
    <parent link="base_link"/>
    <child link="head_link"/>
    <origin xyz="0.0 0.0 0.6" rpy="0 0 0"/>
  </joint>

  <link name="head_link">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="0.5"/>
      <inertia ixx="0.0033" ixy="0.0" ixz="0.0" iyy="0.0033" iyz="0.0" izz="0.0033"/>
    </inertial>
  </link>
</robot>
```

## Humanoid Robot Kinematic Structure

Humanoid robots have a characteristic structure that typically includes:

- **Trunk**: Torso or base body segment
- **Head**: With neck joint for orientation
- **Arms**: With shoulder, elbow, and wrist joints
- **Legs**: With hip, knee, and ankle joints
- **Hands and feet**: With multiple joints for manipulation and balance

### Kinematic Chains

Humanoid robots have multiple kinematic chains that branch from the trunk:

```
        base_link
            |
        torso_link
           /   \
    left_leg      right_leg
    chain         chain
         |           |
    left_arm    right_arm
    chain       chain
```

## Complete Humanoid URDF Example

Here's a comprehensive URDF model for a simplified humanoid robot:

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Materials -->
  <material name="black">
    <color rgba="0.0 0.0 0.0 1.0"/>
  </material>
  <material name="blue">
    <color rgba="0.0 0.0 0.8 1.0"/>
  </material>
  <material name="green">
    <color rgba="0.0 0.8 0.0 1.0"/>
  </material>
  <material name="grey">
    <color rgba="0.5 0.5 0.5 1.0"/>
  </material>
  <material name="orange">
    <color rgba="1.0 0.423529411765 0.0392156862745 1.0"/>
  </material>
  <material name="brown">
    <color rgba="0.870588235294 0.811764705882 0.764705882353 1.0"/>
  </material>
  <material name="red">
    <color rgba="0.8 0.0 0.0 1.0"/>
  </material>
  <material name="white">
    <color rgba="1.0 1.0 1.0 1.0"/>
  </material>

  <!-- Constants -->
  <xacro:property name="PI" value="3.1415926535897931"/>

  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="10.0"/>
      <origin xyz="0 0 0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0"/>
      <geometry>
        <box size="0.3 0.3 0.1"/>
      </geometry>
      <material name="grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0"/>
      <geometry>
        <box size="0.3 0.3 0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Torso -->
  <joint name="torso_joint" type="fixed">
    <parent link="base_link"/>
    <child link="torso_link"/>
    <origin xyz="0 0 0.05"/>
  </joint>

  <link name="torso_link">
    <inertial>
      <mass value="15.0"/>
      <origin xyz="0 0 0.3"/>
      <inertia ixx="0.5" ixy="0" ixz="0" iyy="0.5" iyz="0" izz="0.2"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0.3"/>
      <geometry>
        <box size="0.2 0.3 0.6"/>
      </geometry>
      <material name="white"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.3"/>
      <geometry>
        <box size="0.2 0.3 0.6"/>
      </geometry>
    </collision>
  </link>

  <!-- Head -->
  <joint name="neck_joint" type="revolute">
    <parent link="torso_link"/>
    <child link="head_link"/>
    <origin xyz="0 0 0.6"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/2}" upper="${PI/2}" effort="100" velocity="1"/>
  </joint>

  <link name="head_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 0.05"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0.05"/>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="orange"/>
    </visual>
    <collision>
      <origin xyz="0 0 0.05"/>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Left Hip -->
  <joint name="left_hip_roll_joint" type="revolute">
    <parent link="torso_link"/>
    <child link="left_hip_roll_link"/>
    <origin xyz="0 -0.15 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="${-PI/4}" upper="${PI/4}" effort="200" velocity="1"/>
  </joint>

  <link name="left_hip_roll_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.05"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_hip_yaw_joint" type="revolute">
    <parent link="left_hip_roll_link"/>
    <child link="left_hip_yaw_link"/>
    <origin xyz="0 0 -0.15"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-PI/4}" upper="${PI/4}" effort="200" velocity="1"/>
  </joint>

  <link name="left_hip_yaw_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.15"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <material name="green"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.3"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_hip_pitch_joint" type="revolute">
    <parent link="left_hip_yaw_link"/>
    <child link="left_thigh_link"/>
    <origin xyz="0 0 -0.3"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/2}" upper="${PI/2}" effort="300" velocity="1"/>
  </joint>

  <link name="left_thigh_link">
    <inertial>
      <mass value="5.0"/>
      <origin xyz="0 0 -0.2"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.05"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.07"/>
      </geometry>
      <material name="red"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.07"/>
      </geometry>
    </collision>
  </link>

  <!-- Continue with knee and ankle joints -->
  <joint name="left_knee_joint" type="revolute">
    <parent link="left_thigh_link"/>
    <child link="left_shin_link"/>
    <origin xyz="0 0 -0.4"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/2}" upper="0" effort="300" velocity="1"/>
  </joint>

  <link name="left_shin_link">
    <inertial>
      <mass value="4.0"/>
      <origin xyz="0 0 -0.2"/>
      <inertia ixx="0.08" ixy="0" ixz="0" iyy="0.08" iyz="0" izz="0.04"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.06"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.06"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_ankle_pitch_joint" type="revolute">
    <parent link="left_shin_link"/>
    <child link="left_foot_link"/>
    <origin xyz="0 0 -0.4"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/4}" upper="${PI/4}" effort="100" velocity="1"/>
  </joint>

  <link name="left_foot_link">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0.1 0 -0.05"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0.1 0 -0.05"/>
      <geometry>
        <box size="0.3 0.15 0.1"/>
      </geometry>
      <material name="brown"/>
    </visual>
    <collision>
      <origin xyz="0.1 0 -0.05"/>
      <geometry>
        <box size="0.3 0.15 0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Right leg (mirrored) -->
  <joint name="right_hip_roll_joint" type="revolute">
    <parent link="torso_link"/>
    <child link="right_hip_roll_link"/>
    <origin xyz="0 0.15 0"/>
    <axis xyz="1 0 0"/>
    <limit lower="${-PI/4}" upper="${PI/4}" effort="200" velocity="1"/>
  </joint>

  <link name="right_hip_roll_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.05"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_hip_yaw_joint" type="revolute">
    <parent link="right_hip_roll_link"/>
    <child link="right_hip_yaw_link"/>
    <origin xyz="0 0 -0.15"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-PI/4}" upper="${PI/4}" effort="200" velocity="1"/>
  </joint>

  <link name="right_hip_yaw_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.15"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <material name="green"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_hip_pitch_joint" type="revolute">
    <parent link="right_hip_yaw_link"/>
    <child link="right_thigh_link"/>
    <origin xyz="0 0 -0.3"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/2}" upper="${PI/2}" effort="300" velocity="1"/>
  </joint>

  <link name="right_thigh_link">
    <inertial>
      <mass value="5.0"/>
      <origin xyz="0 0 -0.2"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.05"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.07"/>
      </geometry>
      <material name="red"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.07"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_knee_joint" type="revolute">
    <parent link="right_thigh_link"/>
    <child link="right_shin_link"/>
    <origin xyz="0 0 -0.4"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/2}" upper="0" effort="300" velocity="1"/>
  </joint>

  <link name="right_shin_link">
    <inertial>
      <mass value="4.0"/>
      <origin xyz="0 0 -0.2"/>
      <inertia ixx="0.08" ixy="0" ixz="0" iyy="0.08" iyz="0" izz="0.04"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.06"/>
      </geometry>
      <material name="blue"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.2"/>
      <geometry>
        <cylinder length="0.4" radius="0.06"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_ankle_pitch_joint" type="revolute">
    <parent link="right_shin_link"/>
    <child link="right_foot_link"/>
    <origin xyz="0 0 -0.4"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/4}" upper="${PI/4}" effort="100" velocity="1"/>
  </joint>

  <link name="right_foot_link">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0.1 0 -0.05"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0.1 0 -0.05"/>
      <geometry>
        <box size="0.3 0.15 0.1"/>
      </geometry>
      <material name="brown"/>
    </visual>
    <collision>
      <origin xyz="0.1 0 -0.05"/>
      <geometry>
        <box size="0.3 0.15 0.1"/>
      </geometry>
    </collision>
  </link>

  <!-- Left Arm -->
  <joint name="left_shoulder_pitch_joint" type="revolute">
    <parent link="torso_link"/>
    <child link="left_upper_arm_link"/>
    <origin xyz="0 -0.15 0.4"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/2}" upper="${PI/2}" effort="100" velocity="1"/>
  </joint>

  <link name="left_upper_arm_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.15"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <material name="green"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="left_elbow_joint" type="revolute">
    <parent link="left_upper_arm_link"/>
    <child link="left_forearm_link"/>
    <origin xyz="0 0 -0.3"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-PI/2}" upper="${PI/2}" effort="50" velocity="1"/>
  </joint>

  <link name="left_forearm_link">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.005"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.04"/>
      </geometry>
      <material name="orange"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.04"/>
      </geometry>
    </collision>
  </link>

  <!-- Right Arm -->
  <joint name="right_shoulder_pitch_joint" type="revolute">
    <parent link="torso_link"/>
    <child link="right_upper_arm_link"/>
    <origin xyz="0 0.15 0.4"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-PI/2}" upper="${PI/2}" effort="100" velocity="1"/>
  </joint>

  <link name="right_upper_arm_link">
    <inertial>
      <mass value="2.0"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.15"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <material name="green"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.15"/>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
    </collision>
  </link>

  <joint name="right_elbow_joint" type="revolute">
    <parent link="right_upper_arm_link"/>
    <child link="right_forearm_link"/>
    <origin xyz="0 0 -0.3"/>
    <axis xyz="0 0 1"/>
    <limit lower="${-PI/2}" upper="${PI/2}" effort="50" velocity="1"/>
  </joint>

  <link name="right_forearm_link">
    <inertial>
      <mass value="1.0"/>
      <origin xyz="0 0 -0.1"/>
      <inertia ixx="0.005" ixy="0" ixz="0" iyy="0.005" iyz="0" izz="0.005"/>
    </inertial>
    <visual>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.04"/>
      </geometry>
      <material name="orange"/>
    </visual>
    <collision>
      <origin xyz="0 0 -0.1"/>
      <geometry>
        <cylinder length="0.2" radius="0.04"/>
      </geometry>
    </collision>
  </link>

</robot>
```

## Xacro for Complex Models

For complex humanoid models, Xacro (XML Macros) is essential for avoiding repetition:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid_with_xacro">

  <!-- Properties -->
  <xacro:property name="PI" value="3.1415926535897931"/>
  <xacro:property name="mass_body" value="10.0"/>
  <xacro:property name="mass_arm" value="2.0"/>
  <xacro:property name="mass_leg" value="5.0"/>
  <xacro:property name="body_width" value="0.3"/>
  <xacro:property name="body_depth" value="0.3"/>
  <xacro:property name="body_height" value="0.1"/>

  <!-- Macro for a generic limb -->
  <xacro:macro name="limb" params="name side parent_link position *origin *geometry *inertial">
    <joint name="${side}_${name}_joint" type="revolute">
      <parent link="${parent_link}"/>
      <child link="${side}_${name}_link"/>
      <xacro:insert_block name="origin"/>
      <axis xyz="0 1 0"/>
      <limit lower="${-PI/2}" upper="${PI/2}" effort="100" velocity="1"/>
    </joint>

    <link name="${side}_${name}_link">
      <xacro:insert_block name="inertial"/>
      <visual>
        <xacro:insert_block name="origin"/>
        <xacro:insert_block name="geometry"/>
        <material name="blue"/>
      </visual>
      <collision>
        <xacro:insert_block name="origin"/>
        <xacro:insert_block name="geometry"/>
      </collision>
    </link>
  </xacro:macro>

  <!-- Base link -->
  <link name="base_link">
    <inertial>
      <mass value="${mass_body}"/>
      <origin xyz="0 0 0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
    <visual>
      <origin xyz="0 0 0"/>
      <geometry>
        <box size="${body_width} ${body_depth} ${body_height}"/>
      </geometry>
      <material name="grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0"/>
      <geometry>
        <box size="${body_width} ${body_depth} ${body_height}"/>
      </geometry>
    </collision>
  </link>

  <!-- Use the macro to create arms -->
  <xacro:limb name="upper_arm" side="left" parent_link="base_link" position="front">
    <origin xyz="0 -0.15 0.1" rpy="0 0 0"/>
    <geometry>
      <cylinder length="0.3" radius="0.05"/>
    </geometry>
    <inertial>
      <mass value="${mass_arm}"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </xacro:limb>

  <xacro:limb name="upper_arm" side="right" parent_link="base_link" position="front">
    <origin xyz="0 0.15 0.1" rpy="0 0 0"/>
    <geometry>
      <cylinder length="0.3" radius="0.05"/>
    </geometry>
    <inertial>
      <mass value="${mass_arm}"/>
      <origin xyz="0 0 -0.15"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </xacro:limb>

</robot>
```

## Integration with ROS2 Simulation

### Gazebo Integration

To integrate URDF models with Gazebo simulation, add Gazebo-specific plugins:

```xml
<?xml version="1.0"?>
<robot name="humanoid_with_gazebo_plugins" xmlns:xacro="http://www.ros.org/wiki/xacro">

  <!-- Include the main robot model -->
  <xacro:include filename="$(find my_robot_description)/urdf/main_robot.urdf.xacro"/>

  <!-- Gazebo material definitions -->
  <gazebo reference="base_link">
    <material>Gazebo/Grey</material>
  </gazebo>

  <!-- Gazebo plugin for ROS control -->
  <gazebo>
    <plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">
      <robotNamespace>/humanoid_robot</robotNamespace>
      <robotSimType>gazebo_ros_control/DefaultRobotHWSim</robotSimType>
    </plugin>
  </gazebo>

  <!-- Gazebo plugin for IMU sensor -->
  <gazebo reference="head_link">
    <sensor type="imu" name="imu_sensor">
      <always_on>true</always_on>
      <update_rate>100</update_rate>
      <visualize>true</visualize>
      <imu>
        <noise>
          <type>gaussian</type>
          <rate>
            <mean>0.0</mean>
            <stddev>2e-4</stddev>
            <bias_mean>0.0000075</bias_mean>
            <bias_stddev>0.0000008</bias_stddev>
          </rate>
          <accel>
            <mean>0.0</mean>
            <stddev>1.7e-2</stddev>
            <bias_mean>0.1</bias_mean>
            <bias_stddev>0.001</bias_stddev>
          </accel>
        </noise>
      </imu>
    </sensor>
  </gazebo>

  <!-- Gazebo plugin for laser scanner -->
  <gazebo reference="base_link">
    <sensor type="ray" name="laser_scanner">
      <pose>0.1 0 0.1 0 0 0</pose>
      <visualize>false</visualize>
      <update_rate>10</update_rate>
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
          <max>30.0</max>
          <resolution>0.01</resolution>
        </range>
      </ray>
      <plugin name="laser_controller" filename="libgazebo_ros_laser.so">
        <topicName>/scan</topicName>
        <frameName>base_link</frameName>
      </plugin>
    </sensor>
  </gazebo>

</robot>
```

## Physical Properties and Dynamics

### Inertial Properties

Accurate inertial properties are crucial for realistic simulation:

```python
# Example Python script to calculate inertial properties
import numpy as np

def calculate_box_inertia(mass, width, depth, height):
    """
    Calculate the inertia tensor for a box
    """
    ixx = (1/12) * mass * (depth**2 + height**2)
    iyy = (1/12) * mass * (width**2 + height**2)
    izz = (1/12) * mass * (width**2 + depth**2)

    return {
        'ixx': ixx,
        'iyy': iyy,
        'izz': izz,
        'ixy': 0,
        'ixz': 0,
        'iyz': 0
    }

def calculate_cylinder_inertia(mass, radius, length):
    """
    Calculate the inertia tensor for a cylinder aligned along Z-axis
    """
    ixx = (1/12) * mass * (3 * radius**2 + length**2)
    iyy = (1/12) * mass * (3 * radius**2 + length**2)
    izz = (1/2) * mass * radius**2

    return {
        'ixx': ixx,
        'iyy': iyy,
        'izz': izz,
        'ixy': 0,
        'ixz': 0,
        'iyz': 0
    }

# Example usage
body_properties = calculate_box_inertia(10.0, 0.3, 0.3, 0.1)
print(f"Body inertia: {body_properties}")

arm_properties = calculate_cylinder_inertia(2.0, 0.05, 0.3)
print(f"Arm inertia: {arm_properties}")
```

### Joint Transmission Configuration

For controlling the humanoid robot, transmission elements are needed:

```xml
<!-- Transmission for a revolute joint -->
<transmission name="left_elbow_transmission">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="left_elbow_joint">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
  </joint>
  <actuator name="left_elbow_motor">
    <hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>

<transmission name="right_knee_transmission">
  <type>transmission_interface/SimpleTransmission</type>
  <joint name="right_knee_joint">
    <hardwareInterface>hardware_interface/PositionJointInterface</hardwareInterface>
  </joint>
  <actuator name="right_knee_motor">
    <hardwareInterface>hardware_interface/PositionJointInterface</hardwareInterface>
    <mechanicalReduction>1</mechanicalReduction>
  </actuator>
</transmission>
```

## URDF Visualization and Debugging

### Checking URDF Model

Before simulation, validate the URDF model:

```bash
# Check for URDF errors
check_urdf /path/to/robot.urdf

# Visualize the robot model
urdf_to_graphiz /path/to/robot.urdf

# Launch RViz to visualize
ros2 run rviz2 rviz2
```

### Python URDF Parsing

For programmatic access to URDF models:

```python
import xml.etree.ElementTree as ET
import numpy as np

class URDFParser:
    def __init__(self, urdf_file):
        self.tree = ET.parse(urdf_file)
        self.root = self.tree.getroot()
        self.robot_name = self.root.get('name')

    def get_joint_info(self, joint_name):
        """Get information about a specific joint"""
        for joint in self.root.findall('joint'):
            if joint.get('name') == joint_name:
                joint_type = joint.get('type')

                # Get parent and child links
                parent = joint.find('parent').get('link')
                child = joint.find('child').get('link')

                # Get limits if they exist
                limit_elem = joint.find('limit')
                if limit_elem is not None:
                    lower = float(limit_elem.get('lower', -np.inf))
                    upper = float(limit_elem.get('upper', np.inf))
                    effort = float(limit_elem.get('effort', 0))
                    velocity = float(limit_elem.get('velocity', 0))
                else:
                    lower = upper = effort = velocity = None

                return {
                    'type': joint_type,
                    'parent': parent,
                    'child': child,
                    'limits': {
                        'lower': lower,
                        'upper': upper,
                        'effort': effort,
                        'velocity': velocity
                    }
                }

        return None

    def get_link_mass(self, link_name):
        """Get mass of a specific link"""
        for link in self.root.findall('link'):
            if link.get('name') == link_name:
                inertial = link.find('inertial')
                if inertial is not None:
                    mass_elem = inertial.find('mass')
                    if mass_elem is not None:
                        return float(mass_elem.get('value'))

        return None

# Example usage
parser = URDFParser('simple_humanoid.urdf')
joint_info = parser.get_joint_info('left_knee_joint')
print(f"Left knee joint info: {joint_info}")

mass = parser.get_link_mass('torso_link')
print(f"Torso mass: {mass} kg")
```

## Optimization Techniques for Humanoid URDF

### Simplified Collision Models

For efficient simulation, use simplified collision geometries:

```xml
<!-- Complex visual geometry -->
<link name="complex_visual_link">
  <visual>
    <geometry>
      <mesh filename="meshes/complex_shape.stl"/>
    </geometry>
  </visual>
  <!-- Simplified collision geometry -->
  <collision>
    <geometry>
      <box size="0.2 0.1 0.15"/>
    </geometry>
  </collision>
  <inertial>
    <mass value="1.0"/>
    <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
  </inertial>
</link>
```

### Level of Detail (LOD)

For visualization at different scales:

```xml
<!-- Use different meshes based on viewing distance -->
<visual>
  <geometry>
    <mesh filename="meshes/humanoid_detailed.dae"/>
  </geometry>
  <!-- LOD could be handled by visualization software -->
</visual>
```

## Hands-on Lab: Creating a Custom Humanoid Model

Let's create a complete example of a simplified humanoid model with a launch file:

**launch/humanoid_simulation.launch.py:**
```python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Declare launch arguments
    model_arg = DeclareLaunchArgument(
        'model',
        default_value='simple_humanoid.urdf',
        description='URDF file to load'
    )

    # Path to URDF file
    urdf_path = PathJoinSubstitution([
        FindPackageShare('my_humanoid_description'),
        'urdf',
        LaunchConfiguration('model')
    ])

    # Robot State Publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': open(urdf_path.perform({})).read()
        }]
    )

    # Joint State Publisher GUI for manual control
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    # RViz node
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', PathJoinSubstitution([
            FindPackageShare('my_humanoid_description'),
            'rviz',
            'humanoid_view.rviz'
        ])]
    )

    return LaunchDescription([
        model_arg,
        robot_state_publisher,
        joint_state_publisher_gui,
        rviz
    ])
```

## Evaluation Checkpoints

1. What are the essential components of a humanoid robot URDF model?
2. How do joints and links define the kinematic structure of a humanoid?
3. What is the importance of accurate inertial properties in URDF?
4. How does Xacro help in creating complex humanoid models?
5. What are the key considerations for optimizing URDF for simulation?

## Troubleshooting Common URDF Issues

### Joint Limit Issues
- **Symptom**: Robot moves beyond physical limits
- **Solution**: Define proper joint limits in URDF and controller configurations

### Inertial Property Issues
- **Symptom**: Unstable simulation, unrealistic movement
- **Solution**: Verify mass and inertia values are physically accurate

### Collision Detection Issues
- **Symptom**: Parts intersecting or phantom collisions
- **Solution**: Check collision geometries and origins match visual geometries

### Visualization Issues
- **Symptom**: Model not displaying correctly in RViz
- **Solution**: Verify link names match between URDF and TF frames

## Summary

URDF is fundamental to humanoid robotics in ROS2, providing the geometric and kinematic description necessary for simulation, visualization, and control. Creating accurate URDF models for humanoid robots requires attention to proper joint definitions, physical properties, and optimization for efficient simulation.

The combination of URDF with ROS2's ecosystem enables powerful capabilities for humanoid robot development, from simulation to real-world control. Understanding how to create and optimize URDF models is essential for anyone working with humanoid robots in the ROS2 framework.

This completes Section B: ROS2 Nervous System. We've covered the fundamentals of ROS2, communication patterns, AI integration, and URDF modeling - all essential components of a humanoid robot's software architecture.