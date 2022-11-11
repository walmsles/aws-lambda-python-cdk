from aws_cdk import RemovalPolicy, aws_logs
from aws_cdk.aws_sqs import Queue, QueueEncryption

from services.event_processor.infrastructure import EventProcessorConstruct
from tests.utils.base_infrastructure import BaseInfrastructure

EVENT_API_FUNCTION = "EventApiFunction"
EVENT_API_FUNCTION_ARN = "EventApiFunctionArn"
EVENT_MESSAGE_QUEUE = "EventMessageQueueUrl"
EVENT_STORE_TABLE = "EventStoreTable"
EVENT_STORE_TABLE_ARN = "EventStoreTableArn"


class EventProcessorIntegrationStack(BaseInfrastructure):
    def create_resources(self):
        # The EventProcessorFunction requires a Queue to be provided
        # It is a shared resource from the EventAPIConstruct
        #
        queue = Queue(
            self.stack,
            "MessageQueue",
            encryption=QueueEncryption.KMS_MANAGED,
            enforce_ssl=True,
        )
        event_function = EventProcessorConstruct(
            self.stack, "EventProcessorFunction", queue=queue
        )

        # Set expiry on Lambda log groups so they self delete when no longer needed
        #
        aws_logs.LogGroup(
            self.stack,
            "EventProcessorFunction-lg",
            log_group_name=f"/aws/lamdba/{event_function.function.function_name}",
            retention=aws_logs.RetentionDays.ONE_DAY,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.add_cfn_output(
            name=EVENT_API_FUNCTION,
            value=event_function.function.function_name,
            arn=event_function.function.function_arn,
        )

        self.add_cfn_output(name=EVENT_MESSAGE_QUEUE, value=queue.queue_url)

        self.add_cfn_output(
            name=EVENT_STORE_TABLE,
            value=event_function.table.table_name,
            arn=event_function.table.table_arn,
        )
