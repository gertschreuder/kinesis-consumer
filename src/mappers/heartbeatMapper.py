class Heartbeat(object):
    def clear(self):
        self.providerId = None
        self.id = None
        self.status = None
        self.desc = None

    def __init__(self, data):
        self.clear()
        if "ProviderId" in data:
            self.providerId = data["ProviderId"]
        if "Id" in data and str(data["Id"]).isdigit():
            self.id = int(data["Id"])
        if "Status" in data:
            self.status = data["Status"]
        if "Description" in data:
            self.desc = data["Description"]
