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

class WifiBeaconRecord(AbstractMessage):
    """Wi-Fi Beacon Record"""
    def __init__(self, args):
        super().__init__(args)
        self.mqtt_topic = "80211_beacon_message"
        self.messageType = self.__class__.__name__
        self.bssid = None
        self.beaconInterval = None
        self.serviceSetType = None
        self.ssid = None
        self.supportedRates = None
        self.extendedSupportedRates = None
        self.cypherSuites = None
        self.akmSuites = None
        self.encryptionType = None
        self.wps = None
        self.channel = None
        self.frequencyMhz = None
        self.signalStrength = None
        self.snr = None
        self.nodeType = None
        self.standard = None

    def to_dict(self):
        message = super().to_dict()
        if self.bssid != None:
            message["data"]["bssid"] = self.bssid
        if self.beaconInterval != None:
            message["data"]["beaconInterval"] = self.beaconInterval
        if self.serviceSetType != None:
            message["data"]["serviceSetType"] = self.serviceSetType
        if self.ssid != None:
            message["data"]["ssid"] = self.ssid
        if self.supportedRates != None:
            message["data"]["supportedRates"] = self.supportedRates
        if self.extendedSupportedRates != None:
            message["data"]["extendedSupportedRates"] = self.extendedSupportedRates
        if self.cypherSuites != None:
            message["data"]["cypherSuites"] = self.cypherSuites
        if self.akmSuites != None:
            message["data"]["akmSuites"] = self.akmSuites
        if self.encryptionType != None:
            message["data"]["encryptionType"] = self.encryptionType
        if self.wps != None:
            message["data"]["wps"] = self.wps
        if self.channel != None:
            message["data"]["channel"] = self.channel
        if self.frequencyMhz != None:
            message["data"]["frequencyMhz"] = self.frequencyMhz
        if self.signalStrength != None:
            message["data"]["signalStrength"] = self.signalStrength
        if self.snr != None:
            message["data"]["snr"] = self.snr
        if self.nodeType != None:
            message["data"]["nodeType"] = self.nodeType
        if self.standard != None:
            message["data"]["standard"] = self.standard
        return message


class WifiProbeRequestRecord(AbstractMessage):
    """The 80211_probe_request_message MQTT topic"""
    def __init__(self, args):
        super().__init__(args)
        self.mqtt_topic = "80211_probe_request_message"
        self.messageType = self.__class__.__name__
        self.sourceAddress = None
        self.destinationAddress = None
        self.bssid = None
        self.ssid = None
        self.channel = None
        self.frequencyMhz = None
        self.signalStrength = None
        self.snr = None
        self.nodeType = None
        self.standard = None

    def to_dict(self):
        message = super().to_dict()
        if self.sourceAddress != None:
            message["data"]["sourceAddress"] = self.sourceAddress
        if self.destinationAddress != None:
            message["data"]["destinationAddress"] = self.destinationAddress
        if self.bssid != None:
            message["data"]["bssid"] = self.bssid
        if self.ssid != None:
            message["data"]["ssid"] = self.ssid
        if self.channel != None:
            message["data"]["channel"] = self.channel
        if self.frequencyMhz != None:
            message["data"]["frequencyMhz"] = self.frequencyMhz
        if self.signalStrength != None:
            message["data"]["signalStrength"] = self.signalStrength
        if self.snr != None:
            message["data"]["snr"] = self.snr
        if self.nodeType != None:
            message["data"]["nodeType"] = self.nodeType
        if self.standard != None:
            message["data"]["standard"] = self.standard
        return message



class BluetoothRecord(AbstractMessage):
    """The bluetooth_message MQTT topic"""
    def __init__(self, args):
        super().__init__(args)
        self.mqtt_topic = "bluetooth_message"
        self.messageType = self.__class__.__name__
        self.sourceAddress = None
        self.destinationAddress = None
        self.signalStrength = None
        self.txPower = None
        self.technology = None
        self.supportedTechnologies = None
        self.otaDeviceName = None
        self.channel = None

    def to_dict(self):
        message = super().to_dict()
        if self.sourceAddress != None:
            message["data"]["sourceAddress"] = self.sourceAddress
        if self.destinationAddress != None:
            message["data"]["destinationAddress"] = self.destinationAddress
        if self.signalStrength != None:
            message["data"]["signalStrength"] = self.signalStrength
        if self.txPower != None:
            message["data"]["txPower"] = self.txPower
        if self.technology != None:
            message["data"]["technology"] = self.technology
        if self.supportedTechnologies != None:
            message["data"]["supportedTechnologies"] = self.supportedTechnologies
        if self.otaDeviceName != None:
            message["data"]["otaDeviceName"] = self.otaDeviceName
        if self.channel != None:
            message["data"]["channel"] = self.channel
        return message



class DeviceStatus(AbstractMessage):
    """The device_status_message MQTT topic"""
    def __init__(self, args):
        super().__init__(args)
        self.mqtt_topic = "device_status_message"
        self.messageType = self.__class__.__name__
        self.batteryLevelPercent = None
        self.errorMessge = None

    def to_dict(self):
        message = super().to_dict()
        if self.batteryLevelPercent != None:
            message["data"]["batteryLevelPercent"] = self.batteryLevelPercent
        if self.errorMessge != None:
            message["data"]["error"]["errorMessge"] = self.errorMessge
        return message


class GnssRecord(AbstractMessage):
    """The gnss_message MQTT topic"""
    def __init__(self, args):
        super().__init__(args)
        self.mqtt_topic = "gnss_message"
        self.messageType = self.__class__.__name__
        self.groupNumber = None

    def to_dict(self):
        message = super().to_dict()
        if self.groupNumber != None:
            message["data"]["groupNumber"] = self.groupNumber
        return message
