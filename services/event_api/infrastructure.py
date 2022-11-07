import builtins
from pathlib import Path
from typing import Optional

from aws_cdk import Duration
from aws_cdk.aws_apigateway import LambdaIntegration, RestApi
from aws_cdk.aws_lambda import Architecture, Runtime, Tracing
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk.aws_s3 import BlockPublicAccess, Bucket, BucketEncryption, LifecycleRule
from aws_cdk.aws_sqs import Queue
from constructs import Construct


class EventFunctionConstruct(Construct):
    def __init__(
        self,
        scope: "Construct",
        id: builtins.str,
        *,
        bucket: Optional[Bucket] = None,
        queue: Optional[Queue] = None,
    ) -> None:
        """
        EventApiConstruct
        -----------------
        Component Construct for EventAPI inbound service responsible for validating the inbound event, storing in s3
        and submitting meta-data into SNS for downstream processing.

        Parameters
        ----------
        bucket : allow the bucket to be associated with the EVentAPI service to be injected,
            if None is provided one will be created.
        queue  : Allow the SQS Queue for use by EventApi Lambda to be injected, if None provided one will be created.
        """
        super().__init__(scope, id)

        # Bucket may be provided to this construct if required.  If not one will be created
        if bucket is None:
            # Store events for 7 days then remove
            life_cycles = [
                LifecycleRule(
                    expiration=Duration.days(7),
                )
            ]
            # Create Event Store Bucket
            bucket = Bucket(
                self,
                "EventStore",
                encryption=BucketEncryption.KMS_MANAGED,
                bucket_key_enabled=True,
                block_public_access=BlockPublicAccess.BLOCK_ALL,
                lifecycle_rules=life_cycles,
            )

        runtime_path = str(Path(__file__).parent.joinpath("runtime").resolve())
        print(f"Lambda path: {runtime_path}")

        function = PythonFunction(
            self,
            "LambdaFunction",
            runtime=Runtime.PYTHON_3_9,
            entry=str(Path(__file__).parent.joinpath("runtime").resolve()),
            index="api.py",
            handler="lambda_handler",
            architecture=Architecture.X86_64,
            tracing=Tracing.ACTIVE,
            environment={
                "EVENT_BUCKET": bucket.bucket_name,
            },
        )

        # Grant bucket read/write
        bucket.grant_read_write(function)

        self.bucket = bucket
        self.queue = queue
        self.function = function


class EventApiConstruct(Construct):
    def __init__(
        self,
        scope: "Construct",
        id: builtins.str,
        *,
        bucket: Optional[Bucket] = None,
        queue: Optional[Queue] = None,
    ) -> None:
        """
        EventApiConstruct
        -----------------
        Component Construct for EventAPI inbound service responsible for validating the inbound event, storing in s3
        and submitting meta-data into SNS for downstream processing.

        Parameters
        ----------
        bucket : allow the bucket to be associated with the EVentAPI service to be injected,
            if None is provided one will be created.
        queue  : Allow the SQS Queue for use by EventApi Lambda to be injected, if None provided one will be created.
        """
        super().__init__(scope, id)

        event_function: EventFunctionConstruct = EventFunctionConstruct(
            self, "EventFunction", bucket=bucket, queue=queue
        )

        # Bind to REST API V1
        api = RestApi(self, "EventApi")
        events = api.root.add_resource("events")
        events.add_method(
            "POST", LambdaIntegration(event_function.function, proxy=True)
        )
