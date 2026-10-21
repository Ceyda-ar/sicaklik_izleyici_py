#!/usr/bin/env python3


import random

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Float32

TOPIC_NAME = '/sicaklik'
QUEUE_SIZE = 10


class SensorNode(Node):
  
    def __init__(self) -> None:
        super().__init__('sensor_node')

        
        self.declare_parameter('min_temp', 20.0)
        self.declare_parameter('max_temp', 40.0)
        self.declare_parameter('publish_period', 1.0)

        self._min_temp = self.get_parameter('min_temp').value
        self._max_temp = self.get_parameter('max_temp').value
        period = self.get_parameter('publish_period').value

        if self._min_temp >= self._max_temp:
            self.get_logger().error(
                'min_temp, max_temp değerinden küçük olmalı; '
                'varsayılan 20-40 aralığı kullanılıyor.')
            self._min_temp, self._max_temp = 20.0, 40.0

        if period <= 0.0:
            self.get_logger().error(
                'publish_period pozitif olmalı; 1.0 s kullanılıyor.')
            period = 1.0

        self._publisher = self.create_publisher(
            Float32, TOPIC_NAME, QUEUE_SIZE)
        self._timer = self.create_timer(period, self._publish_temperature)

        self.get_logger().info(
            f'Sensör başlatıldı: {self._min_temp:.1f}-{self._max_temp:.1f} °C, '
            f'her {period:.1f} s, konu: {TOPIC_NAME}')

    def _publish_temperature(self) -> None:
        
        msg = Float32()
        msg.data = random.uniform(self._min_temp, self._max_temp)
        self._publisher.publish(msg)
        self.get_logger().info(f'Yayınlanan sıcaklık: {msg.data:.2f} °C')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SensorNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
