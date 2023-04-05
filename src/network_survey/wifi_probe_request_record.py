from .network_survey import AbstractMessage
from .args import Args

class WifiProbeRequestRecord(AbstractMessage):
    """The 80211_probe_request_message MQTT topic"""
    def __init__(self, args : Args):
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

