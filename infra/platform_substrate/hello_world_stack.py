"""HelloWorldStack — a single Lambda, deployed to LocalStack to verify the
candidate's deploy loop. Kept minimal; candidate can remove, keep as reference,
or extend.
"""
from pathlib import Path

from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from constructs import Construct


LAMBDA_SOURCE = Path(__file__).resolve().parent.parent / "lambdas" / "hello_world"


class HelloWorldStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        _lambda.Function(
            self,
            "HelloWorldFunction",
            function_name="hello-world",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.handler",
            code=_lambda.Code.from_asset(str(LAMBDA_SOURCE)),
            log_retention=logs.RetentionDays.ONE_DAY,
        )
