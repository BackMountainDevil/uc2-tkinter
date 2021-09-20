import time

import paho.mqtt.client as mqtt

from util import Hex2Rgb


class UCMqtt(object):
    broker = "localhost"  # borker IP
    port = 1883  # borker port
    # name = "raspi1"  # username
    # pwd = "1ipsar"  # password
    ID = "Test"  # mqttclient_ID
    keepalive = 60
    client = None  # mqtt client
    connected_flag = False
    bad_connection_flag = False
    disconnect_flag = False

    def __init__(self):
        self.client = mqtt.Client(self.ID)
        # self.client.username_pw_set(self.name, self.pwd)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

    def connect(self):
        """connect to the mqtt server."""
        self.client.loop_start()
        try:
            print("MQTTClient: connecting to broker ", self.broker)
            self.client.connect(self.broker, self.port, self.keepalive)
            while not self.connected_flag and not self.bad_connection_flag:
                print("MQTTClient: Waiting for established connection.")
                time.sleep(1)
            if self.bad_connection_flag:
                self.client.loop_stop()
                print(
                    "MQTTClient: had bad-connection. Not trying to connect any further."
                )
        except Exception as err:
            print("MQTTClient: Connection failed")
            print(err)

    def on_disconnect(self, client, userdata, rc):
        print("MQTTClient: disconnect reason: {0}".format)
        self.connected_flag = False
        self.disconnect_flag = True
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        """
        callback func when client connected to the mqtt server.
        rc  0：连接成功
            1：连接被拒绝-协议版本不正确
            2：连接被拒绝-无效的客户端标识符
            3：连接被拒绝-服务器不可用
            4：连接被拒绝-用户名或密码错误
            5：连接被拒绝-未经授权
            6-255：当前未使用。
        """
        if rc == 0:
            self.connected_flag = True
            print(
                "MQTTClient: Connection established successfuly with result code "
                + str(rc)
            )
        else:
            print("MQTTClient: Connection establish ERROR with result code " + str(rc))
            self.bad_connection_flag = True

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """"""
        pass

    def on_message(self, client, userdata, message):
        """
        handle the message when a PUBLISH message is received from the server
        handlers should not set blocked
        """
        print("Time on receive={0}".format(time.asctime(time.localtime(time.time()))))
        print(
            "Received={0}\nTopic={1}\nQOS={2}\nRetain Flag={3}".format(
                message.payload.decode("utf-8"),
                message.topic,
                message.qos,
                message.retain,
            )
        )

    def subscribe(self, topic, **kwargs):
        """
        subscribe topic message
        default set qos to 0
        """
        return self.client.subscribe(topic, **kwargs)

    def unsubscribe(self, topic, properties=None):
        """unsubscribe topic"""
        return self.client.unsubscribe(topic, properties=properties)

    def publish(self, topic, message, **kwargs):
        """publish message through topic"""
        return self.client.publish(topic, message)

    # 以下为自定义消息
    def pubLedOn(self, colorHex):
        """全场亮灯"""
        self.publish("/S001/LAR01/RECM", "RECT+0+0+8+8+" + Hex2Rgb(colorHex))

    def pubLedOff(self):
        """全场灭灯"""
        self.publish("/S001/LAR01/RECM", "CLEAR")

    def pubMotorZ(self, cmd):
        """移动舵机Z到指定的位置"""
        self.publish("/S001/MOT01/RECM", cmd)


if __name__ == "__main__":
    # import 此类不会运行此测试代码
    # 测试代码，用 mosquitto_sub -v -t /S001/MOT01/RECM 进行接收测试
    mc = UCMqtt()
    mc.connect()
    mc.subscribe("S001/MOT01/RECM", qos=1)
    mc.publish("S001/MOT01/RECM", "1000", qos=1, retain=False)
    time.sleep(10)
