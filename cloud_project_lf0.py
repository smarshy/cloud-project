import json
import boto3
import os
from contextlib import closing

import uuid

lec_client = boto3.client('lex-runtime')
polly_client = boto3.client('polly')

bucketName = 'cloud-project-audiobucket'

def lambda_handler(event, context):

    print(event)
    requestBody = json.loads(event['body'])
    requestBody = requestBody['message']['content']['text']
    
    '''
    response = lec_client.post_text(
        botAlias = 'DiningConciergeBot_One',
        botName = 'DiningConciergeBot',
        userId =  "123",
        inputText = event['messages'][0]['unstructured']['text']
        )
    '''
    
    recordId = str(uuid.uuid4())
    
    responseText = requestBody
    
    response = polly_client.synthesize_speech(
        OutputFormat='mp3',
        Text = responseText,
        VoiceId = 'Joanna'
    )
    
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = os.path.join("/tmp/", recordId)
            with open(output, "ab") as file:
                file.write(stream.read())
                
    s3 = boto3.client('s3')
    s3.upload_file('/tmp/' + recordId, bucketName, recordId + ".mp3")
        
    result = {
        'statusCode':'200',
        'body':"{\"result\": {\"text\" : \"" + responseText + "\", \"s3_uuid\" : \"" + recordId + "\" }}",
        'headers': {
            "Content-Type" : "application/json",
            "Access-Control-Allow-Origin" : "*",
            "Allow" : "GET, OPTIONS, POST",
            "Access-Control-Allow-Methods" : "GET, OPTIONS, POST",
            "Access-Control-Allow-Headers" : "*"
        }
    }
    
    print(result)
    return result