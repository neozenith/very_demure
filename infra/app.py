#!/usr/bin/env python3

import aws_cdk as cdk
from very_demure_infra.frontend_stack import VeryDemureSecureFrontEndStack

app = cdk.App()
VeryDemureSecureFrontEndStack(app, "VeryDemureSecureFrontEndStack")
app.synth()
