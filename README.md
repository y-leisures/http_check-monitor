## README

### aws Secrets Manager
[update\-secret — AWS CLI 1\.18\.173 Command Reference](https://docs.aws.amazon.com/cli/latest/reference/secretsmanager/update-secret.html#examples)

- [Secrets Manager](https://console.aws.amazon.com/secretsmanager/home?region=us-east-1#/secret?name=TwitterApiTokenForBms#secret-details-sample-code-section)


```shell script
$ jq "." t.json
{
  "CONSUMER_KEY": "T8Z2uhJp04bJKubLLkLkXyqhZ",
  "CONSUMER_SECRET": "j7biL6IlNEY2prJIZHJHBGBPYeQJqBVbzPtXc56q6LT4Dn90Ez",
  "ACCESS_TOKEN_KEY": "1323518374341570561-zuPgnPE5kyzNWL9u7AeUmI2lThfZx5",
  "ACCESS_TOKEN_SECRET": "TglShdJmTRGrq2bCuvGDruoIhmQn305bS6XTjxUI5Tm0Y"
}

$ aws --region us-east-1 --profile serverless secretsmanager update-secret --secret-id TwitterApiTokenForBms --secret-string file://t.json
{
    "ARN": "arn:aws:secretsmanager:us-east-1:949140100595:secret:TwitterApiTokenForBms-Nbm5Y6",
    "Name": "TwitterApiTokenForBms",
    "VersionId": "3d906a32-3545-4586-af14-e490ca398ec5"
}
```


```python
# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/

import boto3
import base64
from botocore.exceptions import ClientError


def get_secret():

    secret_name = "TwitterApiTokenForBms"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    # Your code goes here.

```

--------

## sam - serverless application model


```
# 今回はhello-worldテンプレートを使ってみる。
$ sam init --name bms-monitor --runtime python3.8 --dependency-manager pip --app-template hello-world

# こっちのテンプレートも使える。
$ sam init --name bms-monitor2 --runtime python3.8 --dependency-manager pip --app-template step-functions-sample-app
```


## Link

### Sam

- [\[アップデート\]AWS SAMのデプロイが簡単になりました \| Developers\.IO](https://dev.classmethod.jp/articles/aws-sam-simplifies-deployment/)

### Doc for sam
- [Tutorial: Deploying a Hello World application \- AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html)

    ```
    $ aws cloudformation delete-stack --stack-name sam-app --region region
    ```

- [AWS SAMでLambdaのPolicyとRoleを両方設定すると、Roleが優先されてハマった話 \| Developers\.IO](https://dev.classmethod.jp/articles/aws-sam-policy-role-used/)
- [sam deploy \- AWS Serverless Application Model](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html)
- [serverless\-application\-model/2016\-10\-31\.md at master · aws/serverless\-application\-model](https://github.com/aws/serverless-application-model/blob/master/versions/2016-10-31.md#properties)
- [【小ネタ】AWS SAMでLambda関数を作成する場合はCloudWatch LogsのLog Groupも同時に作った方がいいという話 \| Developers\.IO](https://dev.classmethod.jp/articles/should-create-cloudwatch-logs-log-group-when-creating-lambda-with-aws-sam/)

#### Using AWS Lambda with Amazon CloudWatch Events
[Using AWS Lambda with Amazon CloudWatch Events \- AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents.html)

Monitoringに使うにはこっちを理解する必要がある。

- [AWS SAM template for a CloudWatch Events application \- AWS Lambda](https://docs.aws.amazon.com/lambda/latest/dg/with-scheduledevents-example-use-app-spec.html)

### AWS lambda templates

[aws/aws\-sam\-cli\-app\-templates](https://github.com/aws/aws-sam-cli-app-templates)

-------------
## Log

`sam build`が毎回必要なことを理解していなかった様子。

```shell script
(misc) ~/P/r/bms-monitor ❯❯❯ sam build --use-container
Starting Build inside a container
Building codeuri: hello_world/ runtime: python3.8 metadata: {} functions: ['HelloWorldFunction']

Fetching amazon/aws-sam-cli-build-image-python3.8 Docker container image......
Mounting /Users/yuokada/PycharmProjects/raspberrypiLab/bms-monitor/hello_world as /tmp/samcli/source:ro,delegated inside runtime container

Build Succeeded

Built Artifacts  : .aws-sam/build
Built Template   : .aws-sam/build/template.yaml

Commands you can use next
=========================
[*] Invoke Function: sam local invoke
[*] Deploy: sam deploy --guided

Running PythonPipBuilder:ResolveDependencies
Running PythonPipBuilder:CopySource


(misc) ~/P/r/bms-monitor ❯❯❯ sam local invoke "HelloWorldFunction" -e events/event.json
Invoking app.lambda_handler (python3.8)
Skip pulling image and use local one: amazon/aws-sam-cli-emulation-image-python3.8:rapid-1.8.0.

Mounting /Users/yuokada/PycharmProjects/raspberrypiLab/bms-monitor/.aws-sam/build/HelloWorldFunction as /var/task:ro,delegated inside runtime container
START RequestId: 2fe0c162-1d47-1f24-40bb-6ea06ea8d6ca Version: $LATEST
END RequestId: 2fe0c162-1d47-1f24-40bb-6ea06ea8d6ca
REPORT RequestId: 2fe0c162-1d47-1f24-40bb-6ea06ea8d6ca  Init Duration: 616.38 ms        Duration: 14.73 ms      Billed Duration: 100 ms Memory Size: 128 MB     Max Memory Used: 24 MB

{"statusCode":200,"body":"{\"message\": \"hello world! monitor is http://b-ms.info/\"}"}


(misc) ~/P/r/bms-monitor ❯❯❯ sam deploy
Uploading to sam-app/e39caa2ff451d32f1077d85614851503  8606301 / 8606301.0  (100.00%)

        Deploying with following values
        ===============================
        Stack name                 : bms-monitor-by-sam
        Region                     : us-east-1
        Confirm changeset          : False
        Deployment s3 bucket       : aws-sam-cli-managed-default-samclisourcebucket-1l90wfgmezt26
        Capabilities               : ["CAPABILITY_IAM"]
        Parameter overrides        : {}

Initiating deployment
=====================
HelloWorldFunction may not have authorization defined.
Uploading to sam-app/f82eda367423e52d1c33984c491f017d.template  1251 / 1251.0  (100.00%)

Waiting for changeset to be created..

CloudFormation stack changeset
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
Operation                                 LogicalResourceId                         ResourceType                              Replacement
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
* Modify                                  HelloWorldFunction                        AWS::Lambda::Function                     False
* Modify                                  ServerlessRestApi                         AWS::ApiGateway::RestApi                  False
---------------------------------------------------------------------------------------------------------------------------------------------------------------------

Changeset created successfully. arn:aws:cloudformation:us-east-1:949140100595:changeSet/samcli-deploy1604815032/025f53e4-51a4-45ac-90fe-b0069a75aa7e


2020-11-08 14:57:26 - Waiting for stack create/update to complete

CloudFormation events from changeset
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
ResourceStatus                            ResourceType                              LogicalResourceId                         ResourceStatusReason
---------------------------------------------------------------------------------------------------------------------------------------------------------------------
UPDATE_IN_PROGRESS                        AWS::Lambda::Function                     HelloWorldFunction                        -
UPDATE_COMPLETE                           AWS::Lambda::Function                     HelloWorldFunction                        -
UPDATE_COMPLETE                           AWS::CloudFormation::Stack                bms-monitor-by-sam                        -
UPDATE_COMPLETE_CLEANUP_IN_PROGRESS       AWS::CloudFormation::Stack                bms-monitor-by-sam                        -
---------------------------------------------------------------------------------------------------------------------------------------------------------------------

CloudFormation outputs from deployed stack
----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Outputs
----------------------------------------------------------------------------------------------------------------------------------------------------------------------
Key                 HelloWorldFunctionIamRole
Description         Implicit IAM Role created for Hello World function
Value               arn:aws:iam::949140100595:role/bms-monitor-by-sam-HelloWorldFunctionRole-LH5RG0MW4TJT

Key                 HelloWorldApi
Description         API Gateway endpoint URL for Prod stage for Hello World function
Value               https://nlkydzoro7.execute-api.us-east-1.amazonaws.com/Prod/hello/

Key                 HelloWorldFunction
Description         Hello World Lambda Function ARN
Value               arn:aws:lambda:us-east-1:949140100595:function:bms-monitor-by-sam-HelloWorldFunction-BED6UGMLG1JG
----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Successfully created/updated stack - bms-monitor-by-sam in us-east-1
```

----

```shell script
(misc) ~/P/r/bms-monitor ❯❯❯ sam deploy
Uploading to sam-app/0a72ee41e374611ed230a35909d2e875  8606618 / 8606618.0  (100.00%)

        Deploying with following values
        ===============================
        Stack name                 : bms-monitor-by-sam
        Region                     : us-east-1
        Confirm changeset          : False
        Deployment s3 bucket       : aws-sam-cli-managed-default-samclisourcebucket-1l90wfgmezt26
        Capabilities               : ["CAPABILITY_IAM"]
        Parameter overrides        : {}

Initiating deployment
=====================
Uploading to sam-app/999d39dd1b14b5b70e75a3b40ab1cced.template  1031 / 1031.0  (100.00%)

Waiting for changeset to be created..

CloudFormation stack changeset
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Operation                                          LogicalResourceId                                  ResourceType                                       Replacement
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+ Add                                              CheckWebsitePeriodicallyFunEvent1Permission        AWS::Lambda::Permission                            N/A
+ Add                                              CheckWebsitePeriodicallyFunEvent1                  AWS::Events::Rule                                  N/A
+ Add                                              CheckWebsitePeriodicallyFunRole                    AWS::IAM::Role                                     N/A
+ Add                                              CheckWebsitePeriodicallyFun                        AWS::Lambda::Function                              N/A
- Delete                                           CheckWebsitePeriodicallyFunctionEvent1Permission   AWS::Lambda::Permission                            N/A
- Delete                                           CheckWebsitePeriodicallyFunctionEvent1             AWS::Events::Rule                                  N/A
- Delete                                           CheckWebsitePeriodicallyFunctionRole               AWS::IAM::Role                                     N/A
- Delete                                           CheckWebsitePeriodicallyFunction                   AWS::Lambda::Function                              N/A
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Changeset created successfully. arn:aws:cloudformation:us-east-1:949140100595:changeSet/samcli-deploy1604822932/4c0a24ed-f6a3-47dc-aa91-b133b3fa6108


2020-11-08 17:09:06 - Waiting for stack create/update to complete

CloudFormation events from changeset
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
ResourceStatus                                     ResourceType                                       LogicalResourceId                                  ResourceStatusReason
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CREATE_IN_PROGRESS                                 AWS::IAM::Role                                     CheckWebsitePeriodicallyFunRole                    Resource creation Initiated
CREATE_IN_PROGRESS                                 AWS::IAM::Role                                     CheckWebsitePeriodicallyFunRole                    -
CREATE_COMPLETE                                    AWS::IAM::Role                                     CheckWebsitePeriodicallyFunRole                    -
CREATE_IN_PROGRESS                                 AWS::Lambda::Function                              CheckWebsitePeriodicallyFun                        -
CREATE_COMPLETE                                    AWS::Lambda::Function                              CheckWebsitePeriodicallyFun                        -
CREATE_IN_PROGRESS                                 AWS::Lambda::Function                              CheckWebsitePeriodicallyFun                        Resource creation Initiated
CREATE_IN_PROGRESS                                 AWS::Events::Rule                                  CheckWebsitePeriodicallyFunEvent1                  Resource creation Initiated
CREATE_IN_PROGRESS                                 AWS::Events::Rule                                  CheckWebsitePeriodicallyFunEvent1                  -
CREATE_COMPLETE                                    AWS::Events::Rule                                  CheckWebsitePeriodicallyFunEvent1                  -
CREATE_IN_PROGRESS                                 AWS::Lambda::Permission                            CheckWebsitePeriodicallyFunEvent1Permission        Resource creation Initiated
CREATE_IN_PROGRESS                                 AWS::Lambda::Permission                            CheckWebsitePeriodicallyFunEvent1Permission        -
CREATE_COMPLETE                                    AWS::Lambda::Permission                            CheckWebsitePeriodicallyFunEvent1Permission        -
UPDATE_COMPLETE_CLEANUP_IN_PROGRESS                AWS::CloudFormation::Stack                         bms-monitor-by-sam                                 -
DELETE_IN_PROGRESS                                 AWS::Lambda::Permission                            CheckWebsitePeriodicallyFunctionEvent1Permission   -
DELETE_IN_PROGRESS                                 AWS::Events::Rule                                  CheckWebsitePeriodicallyFunctionEvent1             -
DELETE_COMPLETE                                    AWS::Lambda::Permission                            CheckWebsitePeriodicallyFunctionEvent1Permission   -
DELETE_COMPLETE                                    AWS::Events::Rule                                  CheckWebsitePeriodicallyFunctionEvent1             -
DELETE_IN_PROGRESS                                 AWS::Lambda::Function                              CheckWebsitePeriodicallyFunction                   -
DELETE_IN_PROGRESS                                 AWS::IAM::Role                                     CheckWebsitePeriodicallyFunctionRole               -
DELETE_COMPLETE                                    AWS::Lambda::Function                              CheckWebsitePeriodicallyFunction                   -
UPDATE_COMPLETE                                    AWS::CloudFormation::Stack                         bms-monitor-by-sam                                 -
DELETE_COMPLETE                                    AWS::IAM::Role                                     CheckWebsitePeriodicallyFunctionRole               -
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

CloudFormation outputs from deployed stack
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Outputs
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Key                 CheckWebsitePeriodicallyFun
Description         CheckWebsite Periodically Lambda Function ARN
Value               arn:aws:lambda:us-east-1:949140100595:function:bms-monitor-by-sam-CheckWebsitePeriodicallyFun-ZUJKQI44GQK4

Key                 CheckWebsitePeriodicallyIamRole
Description         Implicit IAM Role created for CheckWebsitePeriodically function
Value               arn:aws:iam::949140100595:role/bms-monitor-by-sam-CheckWebsitePeriodicallyFunRole-QCSI4H0WP6A7
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Successfully created/updated stack - bms-monitor-by-sam in us-east-1

```