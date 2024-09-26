# Third Party
import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment
from constructs import Construct


class VeryDemureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for website hosting
        website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            website_index_document="index.html",
            public_read_access=False,  # Allow public read access
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # CloudFront distribution for S3 bucket
        distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
        )

        # Deploy website files to S3 bucket
        s3_deployment.BucketDeployment(
            self,
            "DeployWebsite",
            sources=[s3_deployment.Source.asset("../docs")],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # Output the CloudFront distribution domain
        cdk.CfnOutput(
            self,
            "CloudFrontURL",
            value=distribution.domain_name,
            description="The URL of the website hosted via CloudFront",
        )
