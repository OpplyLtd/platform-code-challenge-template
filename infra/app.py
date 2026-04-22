"""CDK app entry point. Candidate adds new stacks here."""
import aws_cdk as cdk

from platform_substrate.hello_world_stack import HelloWorldStack


app = cdk.App()

HelloWorldStack(
    app,
    "HelloWorldStack",
    env=cdk.Environment(account="000000000000", region="eu-west-2"),
)

app.synth()
