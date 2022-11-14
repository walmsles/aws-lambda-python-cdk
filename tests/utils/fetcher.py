import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple

import boto3
import requests as requests
from mypy_boto3_lambda import LambdaClient
from mypy_boto3_lambda.type_defs import InvocationResponseTypeDef
from requests import Request, Response
from requests.exceptions import RequestException
from retry import retry


def fetch_test_event(name: str) -> Any:
    path = Path(__file__).parent.parent.joinpath("events").joinpath(name)
    return json.loads(path.read_text())


def fetch_lambda_response(
    lambda_arn: str,
    payload: Optional[str] = None,
    client: Optional[LambdaClient] = None,
) -> Tuple[InvocationResponseTypeDef, datetime]:
    client = client or boto3.client("lambda")
    payload = payload or ""
    execution_time = datetime.utcnow()
    return (
        client.invoke(
            FunctionName=lambda_arn, InvocationType="RequestResponse", Payload=payload
        ),
        execution_time,
    )


@retry(RequestException, delay=2, jitter=1.5, tries=5)
def fetch_http_response(request: Request) -> Response:
    session = requests.Session()
    result = session.send(request.prepare())
    result.raise_for_status()
    return result
