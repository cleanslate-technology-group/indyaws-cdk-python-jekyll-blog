---
title: "Host your Jekyll Blog with AWS CDK"
layout: post
---

Are you interested in creating a blog? Jekyll is a static site generator that makes it easy to create a blog and create blog posts using markdown language. Once you create your blog, AWS is a great option for hosting it. AWS is the leading cloud provider in the market today and has all the tools you’d need to host your blog and more. We discussed options for creating a blog in an earlier post; you should check it out [https://blog.cleanslatetg.cloud/start-a-blog/](https://blog.cleanslatetg.cloud/start-a-blog/).

There are several ways that infrastructure can be deployed to AWS, from creating things by hand in the AWS console to using the AWS SDK for your programming language of choice AWS provides multiple options for creating resources. One great option that is a hybrid of IaC and programming is AWS CDK. CDK is an IaC tool that allows users to create and manage infrastructure stacks easily and to define resources using their preferred programming language. We discussed CDK in depth in a previous post. If you’d like to know more about CDK, you should check out the About AWS CDK post: [https://blog.cleanslatetg.cloud/about-aws-cdk/](https://blog.cleanslatetg.cloud/about-aws-cdk/). For this example, we will create our Jekyll static site in AWS using CDK with Python. 

## Tech Stack

### Source Control

- GitHub
    - Users will need to create and host a repo on GitHub
    - The provided example code is hosted on GitHub
        - [https://github.com/cleanslate-technology-group/indyaws-cdk-python-jekyll-blog](https://github.com/cleanslate-technology-group/indyaws-cdk-python-jekyll-blog)
    - GitHub was chosen for this project for several reasons. Users can create free accounts and private repos, a large community of users already using GitHub, and GitHub integrations work well with AWS CodePipeline.
    - This application can be hosted using another source control service but be aware that if you choose to use a different source control, you may need to modify the CDK code to use an external CI/CD system other than CodePipeline.

### Blog Infrastructure

- Route 53
    - Route 53 is where you will purchase and host the domain for your blog
    - The domain will need to be purchased and available before running CDK
- Amazon Certificate Manager (ACM)
    - AWS provides free SSL certificates that, if integrated with AWS Route 53, can be automatically renewed without any intervention by the user
    - ACM will be used to create the necessary SSL certs that will be used for HTTPS traffic to the static site CloudFront distribution.
- S3
    - Two S3 buckets will be required to host the static site and static media. This could be one single bucket; however, splitting out the media files from the static site makes it a little easier to perform CloudFront invalidations, and some Jekyll templates expect media files to be separate from the site content.
    - Static Site files
        - Public bucket configured as a static website
    - Media Files
        - A private bucket that uses a CloudFront OAI for access
- CloudFront
    - Distribution for the static site
        - Hosts the static Jekyll files
        - Uses the Route 53 domains and ACM certs to handle web traffic
    - Distribution for the media files
        - Hosts files with the CloudFront URL

### CI/CD

- CodeStar Connection (GitHub)
    - A connection that allows for AWS CodePipeline to connect to the user's GitHub repo. This connection allows CodePipeline to deploy on check-in to a specified branch.
- CodeBuild
    - CodeBuild is a build system that allows for the Jekyll site files to be created and to perform the invalidation of a CloudFront distribution. The Jeykll static site files are passed to different stages in CodePipeline as artifacts.
- CodePipeline
    - A CI/CD Pipeline is used to orchestrate the generation of static blog files, deployment of files to S3 and invalidation of CloudFront resources.

## Creating your Blog

### Prerequisites

- Create an AWS account to host the blog
- Purchase a domain using Route 53 for the Blog URL
- Install the AWS CLI
- Create an AWS CLI profile
- Install AWS CDK
- Install Python 3

### Steps

1. Create a private GitHub repository for your blog
2. Clone the repo [https://github.com/cleanslate-technology-group/indyaws-cdk-python-jekyll-blog](https://github.com/cleanslate-technology-group/indyaws-cdk-python-jekyll-blog) into your repo
3. Find a Jekyll theme you’d like to use (if you don’t want to use the theme provided in the cloned repo)
    - For more info about Jekyll themes, see the Jekyll docs [https://jekyllrb.com/docs/themes/](https://jekyllrb.com/docs/themes/)
4. (Optional) - In the blog folder, delete all of the files and replace them with the desired Jekyll template files
5. In the infrastructure folder, activate the Python virtual environment
    
    ```bash
    # Mac or Linux 
    source .venv/bin/activate
    
    # Windows
    # .venv\Scripts\activate.bat
    ```
    
6. Install the requirements in the requirements.txt file
    
    ```bash
    pip install -r requirements.txt
    ```
    
7. Bootstrap the AWS Account & Region
    
    ```bash
    cdk bootstrap --profile <profileName>
    ```
    
8. At the root of your repository, create .env file. This file will be used to provide environment variables to the CDK script
    
    ```bash
    touch .env
    ```
    
9. Populate the .env file with the following values
    
    ```bash
    AWS_ACCOUNT_NUMBER=<AWS_ACCOUNT_NUMBER>
    AWS_REGION=<AWS_REGION>
    DOMAIN_NAME=<DOMAIN_NAME>
    BASE_DOMAIN=<BASE_DOMAIN>
    REPO_OWNER=<REPO_OWNER>
    REPO_NAME=<REPO_NAME>
    REPO_BRANCH=<REPO_BRANCH>
    ```
    
    - AWS_ACCOUNT_NUMBER - This is the account number of the AWS account used to host the blog. This will be used to create an environment in CDK
    - AWS_REGION - The region in the AWS account that the blog will be deployed to. This will be used to create an environment in CDK
    - DOMAIN_NAME - This is the domain name that you want your blog to have (excluding www. The www record will be added automatically). Example: blog.supercoolsite.com
    - BASE_DOMAIN - This is the root domain you purchased on Route 53. This should not contain any subdomains. If you are not using subdomains for your blog, then the value of the DOMAIN_NAME and BASE_DOMAIN will be the same. Example: supercoolsite.com
    - REPO_OWNER - Name of the owner of your repository. It will either be your GitHub username if you are hosting the repo from your GitHub user or will be the name of the GitHub organization that owns the repository.
    - REPO_NAME - Name of your repository
    - REPO_BRANCH - Branch that will be used by CI/CD to detect commits and deploy from. I would recommend using the main branch.
10. Commit and publish the changes to your repository up to your remote main branch 
11. Deploy the CDK stack using the deploy command
    
    ```bash
    cdk deploy --profile <profileName>
    ```
    
12. After the deployment has finished, login to your AWS accounts management console, then select the region that you deployed the blog into
13. Using the search bar at the top of the management console, search for and select “CodePipeline”
14. Once in the CodePipline service, you will see the pipeline that was created by CDK for the blog. This is where you can see the progress of your blog deployments in the future. The first run of the CodePipeline will fail because you have to finish configuring the link between your AWS account and GitHub. 
15. In the left-hand menu, under CodePipeline, select ********************Setting —> Connections********************
16. On the connections, click on the pending connection named ************************************jekyll-static-site************************************
17. Once on the jekyll-static-site connection page, click the button to finish setting up the connection. Walk through the prompts to complete the setup.
18. After the connection setup has been completed, you can return to CodePipeline. Select the pipeline for the blog and press the ******************************Release Changes****************************** button to force a new deployment.
19. After the deployment has been completed, you should be able to see your blog at the domain name you provided in the .env file.
20. Your blog is now published. You can post new articles to your blog by following the steps specified by your Jekyll theme. Once your new article is ready to be published, you can automatically deploy it by simply checking in your changes to the branch specified for the **REPO_BRANCH** variable in the .env file.

Happy Blogging!