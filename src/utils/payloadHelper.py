import json

from src.mappers.heartbeatMapper import Heartbeat


class PayloadHelper(object):
    def __init__(self):
        self.heartbeat = None
        self.messageTimeStamp = None

    def map(self, data):

        self.meta(data)
        self.resolveStatus(data)

        return self

    def meta(self, data):
        if "MessageId" in data:
            k, t = data["MessageId"].split("_TS")
            self.resolveMessageId(k)
            self.resolveTimeStamp(t)

    def resolveMessageId(self, data):
        self.messageId = data.split(":")[1]

    def resolveTimeStamp(self, data):
        self.messageTimeStamp = data.split(":")[1]

    def resolveStatus(self, data):
        if "Status" in data and data["Status"] is not None:
            self.heartbeat = Heartbeat(data["Status"])
        return self.heartbeat
