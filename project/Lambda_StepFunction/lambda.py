# Lambda 1: serializeImageData
import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    key = event['s3_key']
    bucket = event['s3_bucket']
    s3.download_file(bucket, key, '/tmp/image.png')
    with open('/tmp/image.png', 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    return {
        'statusCode': 200,
        'body': {
            'image_data': image_data,
            's3_bucket': bucket,
            's3_key': key,
            'inferences': []
        }
    }

# Lambda 2: classifierLambda
import json
import boto3
import base64

runtime = boto3.client('sagemaker-runtime')

ENDPOINT = 'image-classification-2025-07-03-16-14-15-018'

def lambda_handler(event, context):
    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])

    # Call the SageMaker endpoint
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType='image/png',
        Body=image
    )

    # Read the inference result
    inferences = response['Body'].read().decode('utf-8')
    event['body']['inferences'] = json.loads(inferences)

    return {
        'statusCode': 200,
        'body': event['body']
    }

# Lambda 3: filterLowConfidence
import json

THRESHOLD = 0.93

def lambda_handler(event, context):
    inferences = event['body']['inferences']
    meets_threshold = max(inferences) > THRESHOLD
    if meets_threshold:
        return {
            'statusCode': 200,
            'body': event['body']
        }
    else:
        raise Exception('THRESHOLD_CONFIDENCE_NOT_MET')



# input json for step function
  {
    "s3_bucket": "sagemaker-us-east-1-156041407118",
    "s3_key": "test/bicycle_s_000030.png"
  }