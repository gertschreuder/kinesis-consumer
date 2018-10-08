import boto3

from src.utils.config import Config


class Queue(object):
    def __init__(self):
        self.cfg = Config()
        self.sqsClient = boto3.client('sqs', region_name=self.cfg.AWSRegion,
                                      endpoint_url=self.cfg.SQSEndPoint)
        try:
            self.sqsClient.create_queue(QueueName=self.cfg.QueueName)
        except Exception:
            print('SQS Queue exists.')
        queues = self.sqsClient.list_queues(QueueNamePrefix=self.cfg.QueueName)
        self.queue_url = queues['QueueUrls'][0]

    def formatPayload(self, data):
        return {"retry": data}

    def put(self, payload):
        enqueue_response = self.sqsClient.send_message(QueueUrl=self.queue_url, MessageBody=self.formatPayload(payload))
