# A Minimal program to spin stack to cater Image transformation from JPEG to PNG

The stack is provisioned using Pulumi.

## Following resources are provisioned
* A lambda with python 3.8 runtime
  * The lambda uses a layer to avoid dependency library compilation issues.
  * Source of the layer is https://github.com/keithrozario/Klayers
  * Lambda uses a assume role to execute itself, and a inline policy to write to S3
  * Access to Cloudwatch is also given to log the messages
* S3 bucket with public access disabled.
  * A trigger is configured for BucketNotification for the event OnObjectCreate with a 
    prefix of `input`

### Following are the reference docs used
* https://www.pulumi.com/registry/packages/aws/
* https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html
* https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
* https://stackoverflow.com/questions/57197283/aws-lambda-cannot-import-name-imaging-from-pil
* 
* S3 object lambda is not used as its for GET operation