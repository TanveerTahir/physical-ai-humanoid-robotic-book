#!/usr/bin/env python3
"""
URDF and Robot State Publisher example for humanoid robot
Demonstrates how to use URDF models with robot state publisher
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math
import time


class URDFRobotStatePublisher(Node):
    """
    Robot state publisher for humanoid robot URDF model
    """

    def __init__(self):
        super().__init__('urdf_robot_state_publisher')

        # Publisher for joint states
        self.joint_state_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Transform broadcaster for TF tree
        self.tf_broadcaster = TransformBroadcaster(self)

        # Timer for publishing states
        self.timer = self.create_timer(0.05, self.publish_states)  # 20Hz

        # Joint names for a simplified humanoid
        self.joint_names = [
            'neck_joint',
            'left_shoulder_pitch_joint', 'left_elbow_joint',
            'right_shoulder_pitch_joint', 'right_elbow_joint',
            'left_hip_roll_joint', 'left_hip_pitch_joint', 'left_knee_joint',
            'right_hip_roll_joint', 'right_hip_pitch_joint', 'right_knee_joint'
        ]

        self.get_logger().info('URDF Robot State Publisher initialized')

    def publish_states(self):
        """Publish joint states and transforms"""
        # Create joint state message
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # Set joint names
        msg.name = self.joint_names

        # Calculate joint positions (oscillating for demonstration)
        positions = []
        time_now = self.get_clock().now().nanoseconds / 1e9

        for i, joint_name in enumerate(self.joint_names):
            # Different oscillation patterns for different joints
            if 'neck' in joint_name:
                # Neck moves slowly
                pos = math.sin(time_now * 0.5) * 0.2
            elif 'shoulder' in joint_name:
                # Shoulder moves with medium speed
                pos = math.sin(time_now * 1.0 + i) * 0.3
            elif 'elbow' in joint_name:
                # Elbow moves with medium speed, opposite to shoulder
                pos = math.sin(time_now * 1.0 + i + math.pi) * 0.2
            elif 'hip' in joint_name:
                # Hip moves with slower oscillation
                pos = math.sin(time_now * 0.7 + i) * 0.2
            elif 'knee' in joint_name:
                # Knee moves with slower oscillation, complementing hip
                pos = math.sin(time_now * 0.7 + i + math.pi) * 0.2
            else:
                # Default movement
                pos = math.sin(time_now + i) * 0.1

            positions.append(pos)

        msg.position = positions
        msg.velocity = [0.0] * len(positions)  # Zero velocity for simplicity
        msg.effort = [0.0] * len(positions)    # Zero effort for simplicity

        # Publish joint states
        self.joint_state_pub.publish(msg)

        # Broadcast transforms for each joint
        self.broadcast_transforms(msg)

    def broadcast_transforms(self, joint_state_msg):
        """Broadcast transforms for the robot tree"""
        time_stamp = joint_state_msg.header.stamp

        # Base to torso transform
        t = TransformStamped()
        t.header.stamp = time_stamp
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'torso_link'
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.05
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

        # Torso to head transform
        neck_idx = joint_state_msg.name.index('neck_joint') if 'neck_joint' in joint_state_msg.name else -1
        if neck_idx >= 0:
            neck_pos = joint_state_msg.position[neck_idx]
            t = TransformStamped()
            t.header.stamp = time_stamp
            t.header.frame_id = 'torso_link'
            t.child_frame_id = 'head_link'
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.6  # Height of head above torso
            # Rotate around Y axis for neck movement
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = math.sin(neck_pos / 2.0)
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = math.cos(neck_pos / 2.0)
            self.tf_broadcaster.sendTransform(t)

        # Left arm transforms
        if 'left_shoulder_pitch_joint' in joint_state_msg.name and 'left_elbow_joint' in joint_state_msg.name:
            # Shoulder to upper arm
            shoulder_idx = joint_state_msg.name.index('left_shoulder_pitch_joint')
            elbow_idx = joint_state_msg.name.index('left_elbow_joint')

            shoulder_pos = joint_state_msg.position[shoulder_idx]
            elbow_pos = joint_state_msg.position[elbow_idx]

            # Torso to left shoulder
            t = TransformStamped()
            t.header.stamp = time_stamp
            t.header.frame_id = 'torso_link'
            t.child_frame_id = 'left_upper_arm_link'
            t.transform.translation.x = 0.0
            t.transform.translation.y = -0.15  # Left side
            t.transform.translation.z = 0.4   # Shoulder height
            t.transform.rotation.x = math.sin(shoulder_pos / 2.0)
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = math.cos(shoulder_pos / 2.0)
            self.tf_broadcaster.sendTransform(t)

            # Upper arm to forearm
            t = TransformStamped()
            t.header.stamp = time_stamp
            t.header.frame_id = 'left_upper_arm_link'
            t.child_frame_id = 'left_forearm_link'
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = -0.3  # Length of upper arm
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = math.sin(elbow_pos / 2.0)
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = math.cos(elbow_pos / 2.0)
            self.tf_broadcaster.sendTransform(t)

        # Right arm transforms (similar to left)
        if 'right_shoulder_pitch_joint' in joint_state_msg.name and 'right_elbow_joint' in joint_state_msg.name:
            # Shoulder to upper arm
            shoulder_idx = joint_state_msg.name.index('right_shoulder_pitch_joint')
            elbow_idx = joint_state_msg.name.index('right_elbow_joint')

            shoulder_pos = joint_state_msg.position[shoulder_idx]
            elbow_pos = joint_state_msg.position[elbow_idx]

            # Torso to right shoulder
            t = TransformStamped()
            t.header.stamp = time_stamp
            t.header.frame_id = 'torso_link'
            t.child_frame_id = 'right_upper_arm_link'
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.15  # Right side
            t.transform.translation.z = 0.4   # Shoulder height
            t.transform.rotation.x = math.sin(shoulder_pos / 2.0)
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = math.cos(shoulder_pos / 2.0)
            self.tf_broadcaster.sendTransform(t)

            # Upper arm to forearm
            t = TransformStamped()
            t.header.stamp = time_stamp
            t.header.frame_id = 'right_upper_arm_link'
            t.child_frame_id = 'right_forearm_link'
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = -0.3  # Length of upper arm
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = math.sin(elbow_pos / 2.0)
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = math.cos(elbow_pos / 2.0)
            self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)

    state_publisher = URDFRobotStatePublisher()

    try:
        rclpy.spin(state_publisher)
    except KeyboardInterrupt:
        state_publisher.get_logger().info('Shutting down URDF state publisher...')
    finally:
        state_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()