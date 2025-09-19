### Lambda function 1 - Download and Serialize Image

import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket, key, '/tmp/image.png')
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }
    
### Lambda Function 2 - Classify Image

import json
import base64
import boto3

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2025-09-19-11-44-58-428"
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']["image_data"])

    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT, ContentType='image/png', Body=image
    )
    
    # Make a prediction:
    inferences = response["Body"].read()
    
    # We return the data back to the Step Function    
    event['body']["inferences"] = inferences

    return {
        'statusCode': 200,
        'body': event['body']
    }

### Lambda Function 3 - Filter Inference

import json

THRESHOLD = .85


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = json.loads(event['body']['inferences'])
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) > THRESHOLD
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event['body']
    }


