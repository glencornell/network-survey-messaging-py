from .args import Args
from .network_survey import AbstractMessage

class DeviceStatus(AbstractMessage):
    """The device_status_message MQTT topic"""
    def __init__(self, args : Args):
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


