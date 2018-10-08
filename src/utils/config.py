import os


class Config:
    AWSProfile = "default"
    AWSRegion = "eu-west-1"

    SQSEndPoint = "http://localhost:4576"
    QueueName = "recovery-queue"

    DynamoDbEndPoint = "http://localhost:4569"
    HeartbeatTable = "DevHeartbeat"

    def __init__(self):
        if "AWS_Profile" in os.environ and os.environ["AWS_Profile"] is not None and os.environ["AWS_Profile"] is not "":
            self.AWSProfile = os.environ["AWS_Profile"]
        if "AWS_Region" in os.environ and os.environ["AWS_Region"] is not None and os.environ["AWS_Region"] is not "":
            self.AWSRegion = os.environ["AWS_Region"]

        if "SQS_EndPoint" in os.environ and os.environ["SQS_EndPoint"] is not None and os.environ["SQS_EndPoint"] is not "":
            self.DynamoDbEndPoint = os.environ["SQS_EndPoint"]
        if "Queue_Name" in os.environ and os.environ["Queue_Name"] is not None and os.environ["Queue_Name"] is not "":
            self.DynamoDbEndPoint = os.environ["Queue_Name"]

        if "DynamoDB_EndPoint" in os.environ and os.environ["DynamoDB_EndPoint"] is not None and os.environ["DynamoDB_EndPoint"] is not "":
            self.DynamoDbEndPoint = os.environ["DynamoDB_EndPoint"]
        if "DynamoDB_Table_Heartbeat" in os.environ and os.environ["DynamoDB_Table_Heartbeat"] is not None and os.environ["DynamoDB_Table_Heartbeat"] is not "":
            self.HeartbeatTable = os.environ["DynamoDB_Table_Heartbeat"]
