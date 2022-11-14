import builtins
from pathlib import Path

from aws_cdk.aws_dynamodb import Attribute, AttributeType, Table, TableEncryption
from aws_cdk.aws_lambda import Architecture, Runtime, Tracing
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk.aws_sqs import Queue
from constructs import Construct


class EventProcessorConstruct(Construct):
    def __init__(
        self,
        scope: "Construct",
        id: builtins.str,
        *,
        queue: Queue,
    ) -> None:
        """
        EventApiConstruct
        -----------------
        Component Construct for EventAPI inbound service responsible for validating the inbound event, storing in s3
        and submitting meta-data into SNS for downstream processing.

        Parameters
        ----------
        queue  : The message queue to be used as the trigger for the lambda function
        """
        super().__init__(scope, id)

        self.table = Table(
            self,
            "EventStore",
            partition_key=Attribute(name="message_id", type=AttributeType.STRING),
            encryption=TableEncryption.AWS_MANAGED,
        )

        self.function = PythonFunction(
            self,
            "LambdaFunction",
            runtime=Runtime.PYTHON_3_9,
            entry=str(Path(__file__).parent.joinpath("runtime").resolve()),
            index="processor.py",
            handler="lambda_handler",
            architecture=Architecture.X86_64,
            tracing=Tracing.ACTIVE,
            environment={
                "EVENT_STORE": self.table.table_name,
            },
        )
        self.function.add_event_source(
            SqsEventSource(
                queue,
                batch_size=10,
            )
        )
        self.table.grant_write_data(self.function)
