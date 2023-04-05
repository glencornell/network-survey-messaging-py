import os
import json
import datetime
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt
from .args import Args
import ssl
import time

PUBLISHER_QOS = os.getenv('PUBLISHER_QOS') or '1'
PUBLISHER_QOS = int(PUBLISHER_QOS)

class InvalidTimeTypeError(Exception):
    """ this is raised when the time type is unknown"""
    pass

class AbstractMessage(object):
    """Abstract Network Survey Message"""
    recordNumber = 0 # Increments with each new object instance

    def __init__(self, args):
        self.mqtt_host = args.mqtt_host
        self.mqtt_port = args.mqtt_port
        self.mqtt_user = args.mqtt_user
        self.mqtt_password = args.mqtt_password
        self.mqtt_tls = args.mqtt_tls
        self.mqtt_use_ca_cert = args.mqtt_use_ca_cert
        self.mqtt_client = None
        self.mqtt_client_id = (args.mqtt_client_id or os.getenv('MQTT_CLIENT_ID') or os.getenv('DEVICE_NAME')) + os.uname().nodename
        self.mqtt_topic = None
        #
        self.messageType = None
        self.version = args.protocol_version
        self.deviceSerialNumber = args.device_id
        self.deviceName = args.device_name
        self.deviceModel = args.device_model
        self.missionId = args.survey_name
        self.recordNumber = AbstractMessage.recordNumber
        AbstractMessage.recordNumber = AbstractMessage.recordNumber + 1
        #
        self.deviceTime = 0
        self.latitude = 0
        self.longitude = 0
        self.accuracy = 0
        # Include altitude only if there's a 3d GPS fix
        self.altitude = 0
        self.heading = 0

    def update_gps(self,gps):
        if issubclass(type(gps.time), datetime.datetime):
            self.deviceTime = gps.get_time().isoformat(timespec='microseconds')
        elif issubclass(type(gps.time), str):
            self.deviceTime = gps.time if gps.time else datetime.datetime.utcnow().isoformat(timespec='microseconds')
        else:
            raise InvalidTimeTypeError

        self.latitude = gps.lat
        self.longitude = gps.lon
        self.accuracy = max(gps.error['x'], gps.error['y'])
        # Include altitude only if there's a 3d GPS fix
        self.altitude = gps.alt if gps.mode > 2 else None
        self.heading = gps.heading

    def to_dict(self):
        """ Translate the object instance to a python dictionary in the form of a network-survey-messaging MQTT message payload"""
        message = {
            "version": self.version,
            "messageType": self.messageType,
            "data": {
                "deviceSerialNumber": self.deviceSerialNumber,
                "deviceName": self.deviceName,
                "deviceTime": self.deviceTime,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "missionId": self.missionId,
                "recordNumber": AbstractMessage.recordNumber,
                "deviceModel": self.deviceModel,
                "accuracy": self.accuracy,
                "heading": self.heading
            }
        }
        if self.altitude != None:
            message["data"]["altitude"] = self.altitude
        return message

    def dumps(self):
        """ Convert the message to a JSON string. """
        return json.dumps(self.to_dict())

    def connect(self):
        MQTT_CA_CERT = '/ca.crt' if self.mqtt_use_ca_cert else None

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                client.connected_flag = True
            else:
                print("******************** network-survey-messaging Bad connection Returned code=", rc)
                client.bad_connection_flag=True

        mqtt.Client.connected_flag=False
        mqtt.Client.bad_connection_flag=False
        self.mqtt_client = mqtt.Client(self.mqtt_client_id)

        if self.mqtt_user:
            self.mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_password)

        if self.mqtt_tls:
            self.mqtt_client.tls_set(ca_certs=MQTT_CA_CERT, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
            self.mqtt_client.tls_insecure_set(True)

        self.mqtt_client.on_connect = on_connect

        self.mqtt_client.loop_start()

        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)

        while not self.mqtt_client.connected_flag and not self.mqtt_client.bad_connection_flag: #wait in loop
            print("Waiting for MQTT connection...")
            time.sleep(1)

        if self.mqtt_client.bad_connection_flag:
            self.mqtt_client.loop_stop()    #Stop loop
            sys.exit()

    def publish(self):
        if not self.mqtt_client.connected_flag:
            self.connect()

        """ Publish the message to the MQTT Broker """

        #print(self.mqtt_topic, self.mqtt_host, self.mqtt_port, self.dumps())
        #rc = mqtt_publish.single(topic=self.mqtt_topic, payload=self.dumps(), hostname=self.mqtt_host, port=self.mqtt_port, auth=mqtt_auth, tls=None)
        ret,mid = self.mqtt_client.publish(self.mqtt_topic, payload=self.dumps(), qos=PUBLISHER_QOS)

        if ret:
            print("*** Publish MID ", mid, " Returned code=", ret)

