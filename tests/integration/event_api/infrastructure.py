from aws_cdk import RemovalPolicy, aws_logs

from services.event_api.infrastructure import EventFunctionConstruct
from tests.utils.base_infrastructure import BaseInfrastructure


class EventApiIntegrationStack(BaseInfrastructure):
    def create_resources(self):
        event_function = EventFunctionConstruct(self.stack, "EventIntegrationFunction")

        # Set expiry on Lambda log groups so they self delete when no longer needed
        #
        aws_logs.LogGroup(
            self.stack,
            "EventAPIFunction-lg",
            log_group_name=f"/aws/lamdba/{event_function.function.function_name}",
            retention=aws_logs.RetentionDays.ONE_DAY,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.add_cfn_output(
            name="EventApiFunction",
            value=event_function.function.function_name,
            arn=event_function.function.function_arn,
        )
        self.add_cfn_output(
            name="EventStoreBucket",
            value=event_function.bucket.bucket_name,
            arn=event_function.bucket.bucket_arn,
        )

        self.add_cfn_output(
            name="EventMessageQueueUrl", value=event_function.queue.queue_url
        )
