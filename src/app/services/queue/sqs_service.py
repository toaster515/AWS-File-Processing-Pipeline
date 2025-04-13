import boto3
from flask import current_app

class SQSservice:
    def __init__(self):
        self.sqs = boto3.client(
            "sqs",
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"]
        )
        self.queue_url = current_app.config["AWS_SQS_QUEUE_URL"]

    def send_message(self, message_body):
        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message_body
        )
        return response.get("MessageId")
