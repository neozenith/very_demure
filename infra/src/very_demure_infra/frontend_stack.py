# Third Party
import aws_cdk as cdk
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3deploy
from constructs import Construct


class VeryDemureFrontEndStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Basic Stack with public bucket content and public Website Hosting on the bucket.

        my_bucket = s3.Bucket(
            self,
            "site_bucket",
            # bucket_name=self._site_domain_name,
            encryption=s3.BucketEncryption.S3_MANAGED,
            website_index_document="index.html",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            public_read_access=True,  # Allow public read access
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,  # Allow public access, block ACL modifications
        )

        s3deploy.BucketDeployment(
            self, "DeployFiles", sources=[s3deploy.Source.asset("../dist")], destination_bucket=my_bucket
        )
        distribution = cloudfront.Distribution(
            self,
            "myDist",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3StaticWebsiteOrigin(my_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
        )

        # Output the CloudFront URL
        cdk.CfnOutput(
            self,
            "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="The URL of the CloudFront distribution",
        )


class VeryDemureSecureFrontEndStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # WIP: Implement more secure implementation so that:
        # - direct access to bucket is not available (this could allow exploits to blow up my billing)
        # - Add Lambda@Edge Authentication too so that JWT tokens must be provided for secured/protected routes.

        my_bucket = s3.Bucket(
            self,
            "site_bucket",
            # bucket_name=self._site_domain_name,
            encryption=s3.BucketEncryption.S3_MANAGED,
            # website_index_document="index.html",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        # Deploy static website files to the S3 bucket
        s3deploy.BucketDeployment(
            self, "DeployFiles", sources=[s3deploy.Source.asset("../dist")], destination_bucket=my_bucket
        )

        # Define Object Access Control
        oac = cloudfront.S3OriginAccessControl(
            self,
            "MyOAC",
            signing=cloudfront.Signing.SIGV4_NO_OVERRIDE,
        )

        # Configure the S3 Origin defined with the OAC
        s3_origin = origins.S3BucketOrigin.with_origin_access_control(
            my_bucket,
            origin_access_control=oac,
            origin_access_levels=[
                cloudfront.AccessLevel.READ,
                cloudfront.AccessLevel.WRITE,
                cloudfront.AccessLevel.DELETE,
            ],
        )

        # CloudFront distribution for the private S3 bucket with OAC
        distribution = cloudfront.Distribution(
            self,
            "myDist",
            default_behavior=cloudfront.BehaviorOptions(
                origin=s3_origin, viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            default_root_object="index.html",
        )

        # Output the CloudFront distribution URL
        cdk.CfnOutput(
            self,
            "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="The URL of the CloudFront distribution",
        )
