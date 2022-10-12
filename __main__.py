import json
import pulumi
import pulumi_aws as aws


#A permission/role is needed for lambda to execute itself
iam_for_lambda = aws.iam.Role("iamForLambda", assume_role_policy="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }   
  ]
}
""",
inline_policies=[
    aws.iam.RoleInlinePolicyArgs(
      name="Cloudwatch_policy",
      policy=json.dumps({
          "Version": "2012-10-17",
          "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:*"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }],
      }),
    ),
    aws.iam.RoleInlinePolicyArgs(
        name="S3_Access_policy",
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "s3-object-lambda:*"
            ],
            "Resource": "*"
            }],
        }),
    )
])

#Define the details of lambda
func = aws.lambda_.Function("func",
    code=pulumi.FileArchive("./my-sourcecode-function/my-deployment-package.zip"),
    role=iam_for_lambda.arn,
    handler="lambda_function.lambda_handler",
    runtime="python3.8",
    layers=["arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p38-Pillow:4"],
    timeout=15)

#Lets create a Simple Storage Service
bucket = aws.s3.BucketV2("bucket", tags={
    "Org": "ebility"
})


#Update the bucket to be private and block public access
bucket_public_access_block = aws.s3.BucketPublicAccessBlock('BucketPublicBlock',
                                                            bucket=bucket.id,
                                                            block_public_acls=True,
                                                            block_public_policy=True,
                                                            ignore_public_acls=True,
                                                            restrict_public_buckets=True)


#Allow S3 to invoke or access the Lambda
allow_bucket = aws.lambda_.Permission("allowBucket",
    action="lambda:InvokeFunction",
    function=func.arn,
    principal="s3.amazonaws.com",
    source_arn=bucket.arn)

#Invoke the Lambda based on trigger from S3
bucket_notification = aws.s3.BucketNotification("bucketNotification",
    bucket=bucket.id,
    lambda_functions=[aws.s3.BucketNotificationLambdaFunctionArgs(
        lambda_function_arn=func.arn,
        events=["s3:ObjectCreated:*"],
        filter_prefix="input",
    )],
    opts=pulumi.ResourceOptions(depends_on=[allow_bucket]))

with open('./Readme.md') as f:
    pulumi.export('readme', f.read())