from PIL import Image
import urllib.parse
import boto3
import io

s3 = boto3.client('s3')

def to_s3(img, bucket, key):
    print("attempting to upload {} from s3".format(key))
    buffer = io.BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)
    sent_data = s3.put_object(Body=buffer, Bucket= bucket, Key=key)

def lambda_handler(event, context):   
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        data = s3.get_object(Bucket=bucket, Key=key)
        content = data['Body'].read()
        image = Image.open(io.BytesIO(content))
        print(image.format, image.size, image.mode)
        if image.format == 'JPEG':
            #Remove the old extension if any
            new_key = key.split('.')[0]
            to_s3(image, bucket, 'out_' + new_key + '.png')
        else:
            print('Unknown format. So not converting the content')
        return
    except Exception as e:
        print(e)
        print(
            'Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(
                key, bucket))
        raise e

