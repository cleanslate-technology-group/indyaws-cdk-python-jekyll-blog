from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    aws_route53 as rt53,
    aws_route53_targets as targets,
    aws_codestarconnections as codestar,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
    aws_codestarnotifications as notifications,
    aws_iam as iam,
    aws_sns as sns,
    RemovalPolicy,
)
from constructs import Construct
import pip

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, domain_name: str,base_domain:str, repo_owner: str, repo_name: str, repo_branch: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket for the Static Site
        static_bucket = s3.Bucket(
            self,'static-site-bucket',
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(block_public_acls=False,block_public_policy=False,ignore_public_acls=False,restrict_public_buckets=False),
            website_index_document="index.html",
            website_error_document="404.html",
            public_read_access=True
        )

        static_bucket.add_lifecycle_rule(
            enabled=True,
            expired_object_delete_marker=True,
            abort_incomplete_multipart_upload_after=Duration.days(10),
            noncurrent_versions_to_retain=5,
            noncurrent_version_expiration=Duration.days(60)
        )

        # Create an S3 bucket for temp media resource
        media_bucket = s3.Bucket(
            self,'media-bucket',
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        media_bucket.add_lifecycle_rule(
            enabled=True,
            expired_object_delete_marker=True,
            abort_incomplete_multipart_upload_after=Duration.days(10),
            noncurrent_versions_to_retain=5,
            noncurrent_version_expiration=Duration.days(60)
        )

        # Lookup Route53 Hosted Zone
        hz = rt53.HostedZone.from_lookup(self,
            "hosted_zone",
            domain_name = base_domain
        )

        # Create ACM Cert & DNS Validation
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_certificatemanager/Certificate.html
        acm_static_site_cert = acm.Certificate(self,"ACMStaticSiteCert",
            domain_name=domain_name,
            subject_alternative_names=[f"www.{domain_name}"],
            validation=acm.CertificateValidation.from_dns(hz)
        )
        
        # Create CloudFront OAI
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/OriginAccessIdentity.html
        cf_oai = cloudfront.OriginAccessIdentity(self, "OAI", comment="access to static site media bucket")

        # Create CloudFront Distribution 
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront/Distribution.html
        cf_distro = cloudfront.Distribution(self,'distro',
            enabled= True,
            certificate=acm_static_site_cert,
            comment="Distro to host the static site",
            domain_names= [
                domain_name,
                f"www.{domain_name}"
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                origin=origins.S3Origin(
                    origin_path="/",
                    bucket=static_bucket
                )
            ),
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2018,
            http_version=cloudfront.HttpVersion.HTTP2_AND_3
        )

        media_distro = cloudfront.Distribution(self,'mediaDistro',
            enabled= True,
            comment="Distro to host the media for the static site",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                origin=origins.S3Origin(
                    origin_access_identity=cf_oai,
                    origin_path="/",
                    bucket=media_bucket
                )
            ),
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2018,
            http_version=cloudfront.HttpVersion.HTTP2_AND_3
        )

        # Create Route 53 record for CloudFront Distro
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_route53/ARecord.html

        # Route 53 record for apex record
        rt53.ARecord(self,"CFAliasRecord",
            zone=hz,
            target=rt53.RecordTarget.from_alias(targets.CloudFrontTarget(cf_distro)),
            record_name=f"{domain_name}"
        )
        
        # Route 53 record to for www 
        rt53.ARecord(self,"CfWWWAliasRecord",
            zone=hz,
            target=rt53.RecordTarget.from_alias(targets.CloudFrontTarget(cf_distro)),
            record_name=f"www.{domain_name}"
        )

        # Create CodeStar Connection for GitHub integration
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codestarconnections/CfnConnection.html

        # Note: This connection will be created in a pending state and must be completed on the AWS Console
        codestar_github_connection = codestar.CfnConnection(self,"GithubConnection",
            connection_name="jekyll-static-site",
            provider_type="GitHub"
        )

        # Create CodePipeline for CI/CD
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codepipeline/Pipeline.html

        # Create the pipeline
        pipeline = codepipeline.Pipeline(self,"pipeline",
            pipeline_name="static-blog",
        )

        # Apply a removal policy to destroy the S3 artifacts bucket when the pipeline is destroyed
        pipeline.apply_removal_policy(RemovalPolicy.DESTROY)

        # Stage: Pull repo from Github
        source_artifact = codepipeline.Artifact()
        source_stage = pipeline.add_stage(stage_name="Source")
        source_stage.add_action(cp_actions.CodeStarConnectionsSourceAction(
            action_name="Github-Source",
            owner=repo_owner,
            repo=repo_name,
            connection_arn=codestar_github_connection.get_att("ConnectionArn").to_string(),
            branch=repo_branch,
            output=source_artifact
        ))

        # Stage: Build Static Site and push to artifact
        build_artifact = codepipeline.Artifact()
        build_jekyll_site = codebuild.PipelineProject(
            scope=self,
            id="BuildJekyllSite",
            build_spec=codebuild.BuildSpec.from_object(
                dict(
                    version="0.2",
                    phases={
                        "install":{
                            "commands": [
                                "cd blog",
                                "gem install jekyll bundler -v 4.2.2",
                                "bundle install"
                            ]
                        },
                        "build": {
                            "commands": [
                                "JEKYLL_ENV=production bundle exec jekyll build"
                            ]
                        }
                    },
                    artifacts={
                        "files": ["**/*"],
                        "base-directory": "blog/_site",
                        "name": "jekyll-static-blog-$(date +%Y-%m-%d)",
                    },
                )
            ),
        )
        build_stage = pipeline.add_stage(stage_name="Build-Site")
        build_stage.add_action(cp_actions.CodeBuildAction(
            action_name="Build-Static-Site",
            project=build_jekyll_site,
            input=source_artifact,
            run_order=1,
            outputs=[build_artifact]
        ))

        # Stage: Deploy static site from artifact created in build stage
        deploy_stage = pipeline.add_stage(stage_name="Deploy-Site")
        
        # Action: Move media asset files from temp media bucket to static-site bucket

        # Action: Deploy Static Site code from build artficat to S3 origin bucket
        deploy_stage.add_action(cp_actions.S3DeployAction(
            bucket=static_bucket,
            input=build_artifact,
            action_name="Deploy-To-S3",
            run_order=1
        ))

        # Stage: Create invalidation in cloudfront to force it to recache files from origin
        cf_invalidate_iam_role = iam.Role(
            scope=self,
            id="invalidationRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
        )

        cf_invalidate_iam_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[
                    f"arn:aws:cloudfront::{self.account}:distribution/{cf_distro.distribution_id}"
                ],
                actions=["cloudfront:CreateInvalidation"],
            )
        )

        cloudfront_invalidate = codebuild.PipelineProject(
            scope=self,
            id="CloudFrontInvalidateProject",
            role=cf_invalidate_iam_role,
            build_spec=codebuild.BuildSpec.from_object(
                dict(
                    version="0.2",
                    phases={
                        "build": {
                            "commands": [
                                f"aws cloudfront create-invalidation --distribution-id '{cf_distro.distribution_id}' --paths '/*'"
                            ]
                        }
                    },
                )
            ),
        )

        update_cf_stage = pipeline.add_stage(stage_name="Update-Cloudfront")
        update_cf_stage.add_action(cp_actions.CodeBuildAction(
            action_name="Invalidate-CloudFront",
            project=cloudfront_invalidate,
            input=build_artifact,
            run_order=1
        ))

        # Create SNS Topic for Deployment 
        # deployment_sns_topic = sns.Topic(self,"deployment_sns_topic",
        #     topic_name="jekyll-blog-deployment",
        #     display_name="jekyll-blog-deployment")

        # Add a rule to the codepipeline to allow it to publish to the SNS Topic
        # deployment_notification_rule = notifications.NotificationRule(self,
        #     "deployment_notification_rule",
        #     source=pipeline,
        #     events=["codepipeline-pipeline-pipeline-execution-failed",
        #         "codepipeline-pipeline-pipeline-execution-succeeded",
        #         "codepipeline-pipeline-pipeline-execution-started",
        #         "codepipeline-pipeline-pipeline-execution-canceled"],
        #     targets=[deployment_sns_topic])