import builtins
import typing
from pathlib import Path

from aws_cdk import Environment, IStackSynthesizer, Stack
from constructs import Construct

from services.event_api.infrastructure import EventApiConstruct
from services.event_processor.infrastructure import EventProcessorConstruct

CDK_PACKAGE_PATH = Path(__file__).parent


class AppStack(Stack):
    def __init__(
        self,
        scope: typing.Optional[Construct] = None,
        id: typing.Optional[builtins.str] = None,
        *,
        analytics_reporting: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[
            typing.Union[Environment, typing.Dict[str, typing.Any]]
        ] = None,
        stack_name: typing.Optional[builtins.str] = None,
        synthesizer: typing.Optional[IStackSynthesizer] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        termination_protection: typing.Optional[builtins.bool] = None
    ) -> None:
        super().__init__(
            scope,
            id,
            analytics_reporting=analytics_reporting,
            description=description,
            env=env,
            stack_name=stack_name,
            synthesizer=synthesizer,
            tags=tags,
            termination_protection=termination_protection,
        )

        event_construct = EventApiConstruct(self, "EventApi")
        EventProcessorConstruct(
            self, "EventProcessor", queue=event_construct.event_api.queue
        )
