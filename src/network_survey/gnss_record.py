from .args import Args
from .network_survey import AbstractMessage

class GnssRecord(AbstractMessage):
    """The gnss_message MQTT topic"""
    def __init__(self, args : Args):
        super().__init__(args)
        self.mqtt_topic = "gnss_message"
        self.messageType = self.__class__.__name__
        self.groupNumber = None

    def to_dict(self):
        message = super().to_dict()
        if self.groupNumber != None:
            message["data"]["groupNumber"] = self.groupNumber
        return message
