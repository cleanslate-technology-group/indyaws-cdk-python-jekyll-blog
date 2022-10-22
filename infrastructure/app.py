#!/usr/bin/env python3
import os
import aws_cdk as cdk
from dotenv import load_dotenv
from infrastructure.infrastructure_stack import InfrastructureStack

# Load environment variables from the .env file it it exists
load_dotenv()

# Create the CDK App
app = cdk.App()

# Create the Stack for the Static Blog
InfrastructureStack(app,
    "JekyllStaticBlog",
    env=cdk.Environment(
        account=os.getenv('AWS_ACCOUNT_NUMBER'), 
        region=os.getenv('AWS_REGION')
    ),
    domain_name=os.getenv('DOMAIN_NAME'),
    base_domain=os.getenv('BASE_DOMAIN'),
    repo_owner=os.getenv('REPO_OWNER'),
    repo_name=os.getenv('REPO_NAME'),
    repo_branch=os.getenv('REPO_BRANCH')
)

app.synth()
