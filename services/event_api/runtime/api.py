import json
from http import HTTPStatus
from typing import Any, Dict

import aws_lambda_powertools.event_handler.content_types as content_types
from adapters.service import EventService
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.event_handler.exceptions import InternalServerError
from aws_lambda_powertools.logging import Logger

app = APIGatewayRestResolver()
logger = Logger()

event_service = EventService()


@app.post("/events")
def post_event():
    transaction_id = app.current_event.request_context.request_id

    response = event_service.process_event(
        transaction_id,
        app.current_event.json_body,
    )
    logger.info(response)

    if response:
        res_obj = {"transaction_id": transaction_id}
        return Response(
            status_code=HTTPStatus.OK.value,
            body=json.dumps(res_obj),
            content_type=content_types.APPLICATION_JSON,
        )
    else:
        raise (InternalServerError("Processing failure"))


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context) -> Dict[str, Any]:
    return app.resolve(event, context)
