#!/usr/bin/env python3
"""
Basic ROS2 example for humanoid robot control
This example demonstrates fundamental ROS2 concepts for humanoid robots
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Duration
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class HumanoidController(Node):
    """
    Basic humanoid robot controller demonstrating ROS2 concepts
    """

    def __init__(self):
        super().__init__('humanoid_controller')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.joint_trajectory_pub = self.create_publisher(
            JointTrajectory, 'joint_trajectory', 10
        )
        self.status_pub = self.create_publisher(String, 'status', 10)

        # Subscribers
        self.joint_state_sub = self.create_subscription(
            JointState, 'joint_states', self.joint_state_callback, 10
        )

        # Timers
        self.control_timer = self.create_timer(0.1, self.control_loop)

        # Internal state
        self.joint_positions = {}
        self.target_joint_positions = {}

        self.get_logger().info('Humanoid Controller initialized')

    def joint_state_callback(self, msg):
        """Process joint state messages"""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_positions[name] = msg.position[i]

    def control_loop(self):
        """Main control loop"""
        # Example: Publish a simple command
        cmd = Twist()
        cmd.linear.x = 0.1  # Move forward slowly
        cmd.angular.z = 0.05  # Turn slightly
        self.cmd_vel_pub.publish(cmd)

        # Example: Send joint trajectory
        if self.joint_positions:
            self.send_joint_trajectory()

        # Publish status
        status_msg = String()
        status_msg.data = f'Controlling humanoid with {len(self.joint_positions)} joints'
        self.status_pub.publish(status_msg)

    def send_joint_trajectory(self):
        """Send a simple joint trajectory"""
        trajectory = JointTrajectory()
        trajectory.joint_names = list(self.joint_positions.keys())[:3]  # Use first 3 joints

        point = JointTrajectoryPoint()

        # Set target positions (oscillating for demonstration)
        import math
        time_now = self.get_clock().now().nanoseconds / 1e9
        positions = []
        for i in range(len(trajectory.joint_names)):
            # Oscillate each joint differently
            pos = math.sin(time_now + i) * 0.5
            positions.append(pos)

        point.positions = positions
        point.time_from_start = Duration(sec=0, nanosec=100000000)  # 0.1 seconds

        trajectory.points = [point]
        self.joint_trajectory_pub.publish(trajectory)


def main(args=None):
    rclpy.init(args=args)

    controller = HumanoidController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Shutting down...')
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()