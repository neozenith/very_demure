#!/usr/bin/env python3
import os

import aws_cdk as cdk
from dotenv import load_dotenv
from very_demure_infra.frontend_stack import VeryDemureMoreSecureFrontEndStack

load_dotenv()

app = cdk.App()
VeryDemureMoreSecureFrontEndStack(
    app,
    "VeryDemureMoreSecureFrontEndStack",
    domain=os.getenv("DOMAIN"),
    acm_certificate_arn=os.getenv("ACM_CERTIFICATE_ARN"),
)
app.synth()
