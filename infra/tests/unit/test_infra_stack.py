import aws_cdk as core
import aws_cdk.assertions as assertions
from very_demure_infra.very_demure_stack import InfraStack


# example tests. To run these tests, uncomment this file along with the example
# resource in infra/infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = InfraStack(app, "infra")
    template = assertions.Template.from_stack(stack)  # noqa: F841


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
