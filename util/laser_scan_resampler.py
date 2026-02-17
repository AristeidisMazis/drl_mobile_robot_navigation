# Developed by Aristeidis Mazis as part of Undergraduate Thesis, 2025.

#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import numpy as np
from sensor_msgs.msg import LaserScan


class LaserScanResampler(Node):

    def __init__(self):
        super().__init__('laser_scan_resampler')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.publisher_ = self.create_publisher(
            LaserScan,
            '/scan_resampled',
            10
        )

        self.target_samples = 40
        self.get_logger().info('LaserScanResampler initialized. Waiting for /scan data...')

    def scan_callback(self, msg):
        original_ranges = np.array(msg.ranges)
        original_len = len(original_ranges)

        if original_len < self.target_samples:
            self.get_logger().warn(f"Not enough samples to resample: got {original_len}")
            return

        # Compute equally spaced indices for downsampling
        indices = np.linspace(0, original_len - 1, self.target_samples).astype(int)
        resampled_ranges = original_ranges[indices]

        # Create a new LaserScan message
        resampled_msg = LaserScan()
        resampled_msg.header = msg.header
        resampled_msg.angle_min = msg.angle_min
        resampled_msg.angle_max = msg.angle_max
        resampled_msg.angle_increment = (msg.angle_max - msg.angle_min) / (self.target_samples - 1)
        resampled_msg.time_increment = msg.time_increment * (original_len / self.target_samples)
        resampled_msg.scan_time = msg.scan_time
        resampled_msg.range_min = msg.range_min
        resampled_msg.range_max = msg.range_max
        resampled_msg.ranges = resampled_ranges.tolist()
        resampled_msg.intensities = []

        self.publisher_.publish(resampled_msg)
        self.get_logger().info("Published resampled scan with 40 samples.")


def main():
    rclpy.init()
    node = LaserScanResampler()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
