---
title: "What is AWS CDK?"
layout: post
---

AWS Cloud Development Kit (CDK) is an infrastructure as code (IaC) tool that allows users to define resource stacks using popular programming languages and then deploy those stacks using AWS CloudFormation. CDK is a command line interface (cli) tool that can be downloaded to a user's development machine or CI/CD systems. The cdk cli tool provides functionality to create new projects, check differences between the deployed stack and the local configuration, synthesize the cdk code into CloudFormation script, and deploy directly from the machine running the tool. CDK is a purpose-built tool built on top of AWS cloudformation to provide enhanced functionality than native CloudFormation. Using fully featured programming languages allows users to create complex logic and conditions that can sometimes be required when creating resource stacks. At runtime, CDK can look up and resolve dynamic values that should not or could not be statically defined. 

### Basic Concepts

- Constructs
    - Constructs are the building block of CDK.
    - Constructs can range from single resources provided by AWS to complicated custom collections of resources created to work together.
    - The constructs created by AWS are defined in the AWS Construct Library.
    - There are 3 levels of constructs
        - L1
            - Low-level construct with a 1-to-1 mapping to the corresponding CloudFormation resource
            - L1 resource names start with **Cfn**
        - L2
            - Higher-level construct that allows for resource creation with enhanced functionality
            - Assists with resource creation by providing defaults and boilerplates
        - L3
            - High-level construct that allows for common tasks that require multiple resources to be easily completed
    - For more information about constructs, check out the docs [https://docs.aws.amazon.com/cdk/v2/guide/constructs.html](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html)
- Stacks
    - Deployable collection of resources
    - CDK stacks get synthesized into CloudFormation stacks using the **cdk synth** command
    - Stacks can be nested using the NestedStack construct
    - For more information about stacks, check out the docs [https://docs.aws.amazon.com/cdk/v2/guide/stacks.html](https://docs.aws.amazon.com/cdk/v2/guide/stacks.html)
- App
    - Container for one or many stacks
    - Stacks inside of the same app can reference resources in one another
    - Stacks can be deployed individually within an app. This is helpful when defining multiple environments
    - For more information about the app, check out the docs [https://docs.aws.amazon.com/cdk/v2/guide/apps.html](https://docs.aws.amazon.com/cdk/v2/guide/apps.html)
- Environments
    - Environments specify the AWS account and region that a stack should be associated to
    - Environments are not required for stacks; however, if it’s not explicitly provided, then a stack is considered environment-agnostic
    - For more information about environments, check out the docs [https://docs.aws.amazon.com/cdk/v2/guide/environments.html](https://docs.aws.amazon.com/cdk/v2/guide/environments.html)
- Bootstrapping
    - Bootstrapping is the process of configuring an account and region to use CDK
    - Bootstrapping must be run the first time that that CDK is used in an account and environment; however, subsequent cdk runs do not need to bootstrap
    - Bootstrapping is account and region-specific, so it must be run in all regions in a particular account you wish to use CDK with
    - CDK creates a CloudFormation script in the specific region to deploy the CDKToolkit
    - For more information about bootstrapping, check out the docs [https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)

### Commands

There are many commands available using the cdk cli tool. To use the cdk tool you must first install it on your machine. Additionally, you will need an AWS account, the aws cli and a profile already set up on the local machine. For information about the aws cli please see the aws cli documentation  [https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html). For information about how to install the cdk cli tool and additional information about the following commands, see the cdk documentation [https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html).

- list - Lists the stacks in the App
    
    ```bash
    cdk list --profile <profileName>
    ```
    
- synth - Synthesizes cdk code into CloudFormation scripts in the cdk.out folder
    
    ```bash
    cdk synth <stackName> --profile <profileName>
    ```
    
- bootstrap - Bootstraps an account and region by using cloudformation to deploy the CDKToolkit
    
    ```bash
    cdk bootstrap --profile <profileName>
    ```
    
- deploy - Synthesizes and deploys cdk stacks to AWS
    
    ```bash
    cdk deploy <stackName> --profile <profileName>
    ```
    
- destroy - Destroys the specified cdk stack
    
    ```bash
    cdk destroy <stackName> --profile <profileName>
    ```
    
- diff - Checks the state of the current configuration against the configuration hosted in the account
    
    ```bash
    cdk diff <stackName> --profile <profileName>
    ```
    
- init - Initializes a new cdk app
    
    ```bash
    cdk init --language <languageName> --profile <profileName>
    ```
    

CDK is a powerful tool with a lot more features than have been covered in this post. I highly recommend you read through the docs and work through some examples to get hands-on with CDK. The CDK workshop provides some great examples to get you hands-on with CDK ([https://cdkworkshop.com/](https://cdkworkshop.com/)).

CDK is a great option for DevOps engineers who would need more functionality out of their IaC tooling and developers who would feel more comfortable keeping their IaC stacks closer to their code. IaC is extremely important for running applications in the cloud, and AWS CDK is a great option to have in your tech stack.