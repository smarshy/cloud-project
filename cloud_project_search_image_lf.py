import json
import boto3
from botocore.vendored import requests

def lambda_handler(event, context):
    requestBody = json.loads(event['body'])
    filename = requestBody['image_name']
    
    bucket='cloud-project-imagebucket'
    client=boto3.client('rekognition')
    print("loaded client")
    response = client.recognize_celebrities(Image={'S3Object':{'Bucket':bucket,'Name':filename}})
    
    #print(response)
    celebrity = response['CelebrityFaces'][0]['Name']
    result = {
        'statusCode':'200',
        'body':"{\"result\": \"" + celebrity + "\"}",
        'headers': {
            "Content-Type" : "application/json",
            "Access-Control-Allow-Origin" : "*",
            "Allow" : "GET, OPTIONS, POST",
            "Access-Control-Allow-Methods" : "GET, OPTIONS, POST",
            "Access-Control-Allow-Headers" : "*"
        }
    }
    return result