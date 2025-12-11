#!/usr/bin/env python3
"""
Advanced AI integration example for humanoid robot control
Demonstrates how to integrate AI models with ROS2 for humanoid control
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist, Pose
from std_srvs.srv import Trigger
from cv_bridge import CvBridge
import numpy as np
import time


class AIBasedController(Node):
    """
    AI-based humanoid robot controller demonstrating AI integration with ROS2
    """

    def __init__(self):
        super().__init__('ai_based_controller')

        # Initialize CV bridge
        self.bridge = CvBridge()

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.ai_status_pub = self.create_publisher(String, 'ai_status', 10)

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, 'camera/image_raw', self.image_callback, 10
        )
        self.laser_sub = self.create_subscription(
            LaserScan, 'scan', self.laser_callback, 10
        )

        # Service
        self.ai_control_srv = self.create_service(
            Trigger, 'control_ai_agent', self.control_ai_callback
        )

        # Timer for AI inference
        self.ai_timer = self.create_timer(0.2, self.ai_inference_loop)

        # Internal state
        self.latest_image = None
        self.latest_laser = None
        self.ai_enabled = True
        self.ai_model_loaded = True  # Simulated model loading

        self.get_logger().info('AI-Based Controller initialized')

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
        # Handle infinite values
        self.latest_laser[np.isinf(self.latest_laser)] = msg.range_max
        self.latest_laser[np.isnan(self.latest_laser)] = msg.range_max

    def ai_inference_loop(self):
        """Main AI inference loop"""
        if not self.ai_enabled or not self.ai_model_loaded:
            return

        if self.latest_image is not None and self.latest_laser is not None:
            try:
                # Prepare input data
                processed_data = self.prepare_input_data()

                # Run AI inference (simulated)
                ai_output = self.run_ai_inference(processed_data)

                # Process AI output
                self.process_ai_output(ai_output)

            except Exception as e:
                self.get_logger().error(f'AI inference error: {e}')

    def prepare_input_data(self):
        """Prepare sensor data for AI model"""
        # Process image
        img_processed = self.preprocess_image(self.latest_image)

        # Process laser data
        laser_processed = self.preprocess_laser(self.latest_laser)

        # Combine data (simulated)
        combined_input = {
            'image_features': img_processed,
            'laser_features': laser_processed
        }

        return combined_input

    def preprocess_image(self, image):
        """Preprocess image for AI model"""
        # Resize for faster processing
        h, w, _ = image.shape
        new_h, new_w = h // 4, w // 4  # Reduce resolution
        resized = np.array([[image[y, x] for x in range(0, w, 4)] for y in range(0, h, 4)])

        # Normalize
        normalized = resized.astype(np.float32) / 255.0

        # Flatten for simple processing
        flattened = normalized.flatten()

        return flattened

    def preprocess_laser(self, laser_ranges):
        """Preprocess laser data for AI model"""
        # Downsample laser ranges for efficiency
        downsampled = laser_ranges[::5]  # Take every 5th sample

        # Normalize to [0, 1]
        range_max = np.max(downsampled)
        if range_max > 0:
            normalized = downsampled / range_max
        else:
            normalized = downsampled

        return normalized

    def run_ai_inference(self, input_data):
        """
        Simulate AI inference - in real implementation, this would run an actual ML model
        """
        # Simulate processing time
        time.sleep(0.01)

        # Simple AI decision based on sensor data
        # This is a placeholder - real implementation would use actual AI model

        # Analyze laser data for obstacles
        laser_features = input_data['laser_features']
        obstacle_detected = np.min(laser_features) < 0.5  # Obstacle closer than 0.5m

        # Analyze image for interesting features (simplified)
        image_features = input_data['image_features']
        # For simplicity, just use average brightness as a feature
        avg_brightness = np.mean(image_features)

        # Make decision based on sensor fusion
        linear_vel = 0.0
        angular_vel = 0.0

        if obstacle_detected:
            # Stop and turn away from obstacle
            linear_vel = 0.0
            # Turn away from closest obstacle
            closest_idx = np.argmin(laser_features)
            if closest_idx < len(laser_features) / 2:
                angular_vel = 0.5  # Turn right
            else:
                angular_vel = -0.5  # Turn left
        else:
            # Move forward with slight random turning to explore
            linear_vel = 0.3
            angular_vel = (np.random.random() - 0.5) * 0.2  # Gentle turns

        # Scale velocities based on brightness (brighter = more cautious)
        brightness_factor = min(1.0, avg_brightness * 2)
        linear_vel *= brightness_factor
        angular_vel *= brightness_factor

        return {
            'linear_velocity': linear_vel,
            'angular_velocity': angular_vel,
            'obstacle_detected': obstacle_detected,
            'avg_brightness': avg_brightness
        }

    def process_ai_output(self, ai_output):
        """Process AI output and send robot commands"""
        # Create and send velocity command
        cmd = Twist()
        cmd.linear.x = float(ai_output['linear_velocity'])
        cmd.angular.z = float(ai_output['angular_velocity'])

        self.cmd_vel_pub.publish(cmd)

        # Publish status
        status_msg = String()
        status_msg.data = (
            f'AI: lin={cmd.linear.x:.2f}, ang={cmd.angular.z:.2f}, '
            f'obs={ai_output["obstacle_detected"]}, '
            f'brightness={ai_output["avg_brightness"]:.2f}'
        )
        self.ai_status_pub.publish(status_msg)

    def control_ai_callback(self, request, response):
        """Handle AI control service requests"""
        self.ai_enabled = request.succeed
        status = 'enabled' if self.ai_enabled else 'disabled'
        self.get_logger().info(f'AI agent {status}')

        response.success = True
        response.message = f'AI agent {status}'

        return response


def main(args=None):
    rclpy.init(args=args)

    ai_controller = AIBasedController()

    try:
        rclpy.spin(ai_controller)
    except KeyboardInterrupt:
        ai_controller.get_logger().info('Shutting down AI controller...')
    finally:
        ai_controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()