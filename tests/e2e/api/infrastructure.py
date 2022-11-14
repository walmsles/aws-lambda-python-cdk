from aws_cdk import RemovalPolicy, aws_logs

from services.event_api.infrastructure import EventApiConstruct
from tests.utils.base_infrastructure import BaseInfrastructure

EVENT_API_URL = "EventApiUrl"


class EndToEndApiStack(BaseInfrastructure):
    def create_resources(self):
        event_api = EventApiConstruct(self.stack, "Api")

        # Set expiry on Lambda log groups so they self delete when no longer needed
        #
        aws_logs.LogGroup(
            self.stack,
            "EventAPIFunction-lg",
            log_group_name=f"/aws/lamdba/{event_api.event_api.function.function_name}",
            retention=aws_logs.RetentionDays.ONE_DAY,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.add_cfn_output(name=EVENT_API_URL, value=event_api.api.url)
