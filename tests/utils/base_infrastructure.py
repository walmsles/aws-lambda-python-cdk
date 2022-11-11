import json
import logging
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Dict
from uuid import uuid4

import boto3
from aws_cdk import App, CfnOutput, Environment, Stack
from mypy_boto3_cloudformation import CloudFormationClient

from tests.utils.constants import CDK_OUT_PATH, SOURCE_CODE_ROOT_PATH
from tests.utils.provider import InfrastructureProvider

logger = logging.getLogger(__name__)


class BaseInfrastructure(InfrastructureProvider):
    RANDOM_STACK_VALUE: str = f"{uuid4()}"

    def __init__(self) -> None:
        self.feature_path = Path(
            sys.modules[self.__class__.__module__].__file__
        ).parent  # absolute path to feature
        self.feature_name = self.feature_path.parts[-1].replace(
            "_", "-"
        )  # logger, tracer, event-handler, etc.
        self.stack_name = f"test-{self.feature_name}-{self.RANDOM_STACK_VALUE}"
        self.stack_outputs: Dict[str, str] = {}

        # NOTE: CDK stack account and region are tokens, we need to resolve earlier
        self.session = boto3.Session()
        self.cfn: CloudFormationClient = self.session.client("cloudformation")
        self.account_id = self.session.client("sts").get_caller_identity()["Account"]
        self.region = self.session.region_name

        self.app = App()
        self.stack = Stack(
            self.app,
            self.stack_name,
            env=Environment(account=self.account_id, region=self.region),
        )

        # NOTE: Introspect feature details to generate CDK App (_create_temp_cdk_app method), Synth and Deployment
        self._feature_infra_class_name = self.__class__.__name__
        self._feature_infra_module_path = self.feature_path / "infrastructure"
        self._feature_infra_file = self.feature_path / "infrastructure.py"
        self._handlers_dir = self.feature_path / "handlers"
        self._cdk_out_dir: Path = CDK_OUT_PATH / self.feature_name
        self._stack_outputs_file = self._cdk_out_dir / "stack_outputs.json"

        if not self._feature_infra_file.exists():
            raise FileNotFoundError(
                "You must have your infrastructure defined in 'tests/e2e/<feature>/infrastructure.py'."
            )

    def _create_temp_cdk_app(self):
        """Autogenerate a CDK App with our Stack so that CDK CLI can deploy it

        This allows us to keep our BaseInfrastructure while supporting context lookups.
        """
        # cdk.out/tracer/cdk_app_v39.py
        temp_file = self._cdk_out_dir / "cdk_app_test.py"

        if temp_file.exists():
            # no need to regenerate CDK app since it's just boilerplate
            return temp_file

        # Convert from POSIX path to Python module: tests.e2e.tracer.infrastructure
        infra_module = str(
            self._feature_infra_module_path.relative_to(SOURCE_CODE_ROOT_PATH)
        ).replace(os.sep, ".")

        code = f"""
        from {infra_module} import {self._feature_infra_class_name}
        stack = {self._feature_infra_class_name}()
        stack.create_resources()
        stack.app.synth()
        """

        if not self._cdk_out_dir.is_dir():
            self._cdk_out_dir.mkdir(parents=True, exist_ok=True)

        with temp_file.open("w") as fd:
            fd.write(textwrap.dedent(code))

        # allow CDK to read/execute file for stack deployment
        temp_file.chmod(0o755)
        return temp_file

    def _sync_stack_name(self, stack_output: Dict):
        """Synchronize initial stack name with CDK final stack name

        When using `cdk synth` with context methods (`from_lookup`),
        CDK can initialize the Stack multiple times until it resolves
        the context.

        Parameters
        ----------
        stack_output : Dict
            CDK CloudFormation Outputs, where the key is the stack name
        """
        self.stack_name = list(stack_output.keys())[0]

    def _read_stack_output(self):
        content = Path(self._stack_outputs_file).read_text()
        outputs: Dict = json.loads(content)
        self._sync_stack_name(stack_output=outputs)

        # discard stack_name and get outputs as dict
        self.stack_outputs = list(outputs.values())[0]
        return self.stack_outputs

    def create_resoures(self):
        pass

    def delete(self) -> None:
        """Delete CloudFormation Stack"""
        logger.debug(f"Deleting stack: {self.stack_name}")
        self.cfn.delete_stack(StackName=self.stack_name)

    def deploy(self) -> Dict[str, str]:
        """Synthesize and deploy a CDK app, and return its stack outputs

        NOTE: It auto-generates a temporary CDK app to benefit from CDK CLI lookup features

        Returns
        -------
        Dict[str, str]
            CloudFormation Stack Outputs with output key and value
        """
        stack_file = self._create_temp_cdk_app()
        synth_command = (
            f"npx cdk synth --app 'python {stack_file}' -o {self._cdk_out_dir}"
        )
        deploy_command = (
            f"npx cdk deploy --app '{self._cdk_out_dir}' -O {self._stack_outputs_file} "
            "--require-approval=never --method=direct"
        )

        # CDK launches a background task, so we must wait
        subprocess.check_output(synth_command, shell=True)
        subprocess.check_output(deploy_command, shell=True)
        return self._read_stack_output()

    def add_cfn_output(self, name: str, value: str, arn: str = ""):
        """Create {Name} and optionally {Name}Arn CloudFormation Outputs.

        Parameters
        ----------
        name : str
            CloudFormation Output Key
        value : str
            CloudFormation Output Value
        arn : str
            CloudFormation Output Value for ARN
        """
        CfnOutput(self.stack, f"{name}", value=value)
        if arn:
            CfnOutput(self.stack, f"{name}Arn", value=arn)
