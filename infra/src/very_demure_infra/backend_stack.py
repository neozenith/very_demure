# Third Party
import aws_cdk as cdk
from constructs import Construct


class VeryDemureBackendStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # TODO: implement a lambda function url for simple API for POCs.
