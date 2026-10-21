#!/usr/bin/env python3

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
from std_msgs.msg import Float32

TOPIC_NAME = '/sicaklik'
QUEUE_SIZE = 10
DEFAULT_THRESHOLD = 30.0


class IzleyiciNode(Node):

    def __init__(self) -> None:
        super().__init__('izleyici_node')

        self.declare_parameter(
            'esik_degeri',
            DEFAULT_THRESHOLD,
            ParameterDescriptor(
                description='Uyarı verilecek sıcaklık eşiği (°C).'))
        self._threshold = float(self.get_parameter('esik_degeri').value)
        self.add_on_set_parameters_callback(self._on_parameter_change)

        self._subscription = self.create_subscription(
            Float32, TOPIC_NAME, self._listener_callback, QUEUE_SIZE)

        self.get_logger().info(
            f'İzleyici başlatıldı: konu: {TOPIC_NAME}, '
            f'eşik: {self._threshold:.1f} °C')

    def _on_parameter_change(self, params: list[Parameter]) -> SetParametersResult:
        for param in params:
            if param.name != 'esik_degeri':
                continue
            if param.type_ not in (Parameter.Type.DOUBLE, Parameter.Type.INTEGER):
                return SetParametersResult(
                    successful=False, reason='esik_degeri sayısal olmalı.')
            self._threshold = float(param.value)
            self.get_logger().info(
                f'Eşik değeri güncellendi: {self._threshold:.1f} °C')
        return SetParametersResult(successful=True)

    def _listener_callback(self, msg: Float32) -> None:
        temp = msg.data
        self.get_logger().info(f'Okunan sıcaklık: {temp:.2f} °C')

        if temp > self._threshold:
            self.get_logger().warn(
                f'UYARI: Sıcaklık eşiği aştı! '
                f'({temp:.2f} °C > {self._threshold:.2f} °C)')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = IzleyiciNode()
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
