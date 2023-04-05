from .args import Args
from .network_survey import AbstractMessage

class BluetoothRecord(AbstractMessage):
    """The bluetooth_message MQTT topic"""
    def __init__(self, args : Args):
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


