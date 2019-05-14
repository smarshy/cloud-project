import json
import boto3
import random
import string
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    #song_id_list - hardcoded for now, will be input from generated playlist
    song_id_list = ["A123456", "Dfr4532", "ASK23456"]
    #post_song_ids_to_queue(song_id_list)
    #song_id_list = get_messages_from_queue()
    song_list = retrieve_from_db(song_id_list)
    # sendSesEmail(song_list, "vatsala.swaroop@gmail.com")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def retrieve_from_db(song_id_list):
    result = []
    for song in song_id_list:
        response = table.get_item(Key={'SongID': song})
        result.append(response["item"])
    return result
    
def post_song_ids_to_queue(s_id_list):
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='cloud_project_song_id.fifo')
    song_id_list = ' '.join(s_id_list)
    response=queue.send_message(MessageBody='To be retrieved from dynamo', MessageAttributes={
    'song_id_list': {
        'StringValue': song_id_list,
        'DataType': 'String'
        }
    },
    MessageGroupId=''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]),
    MessageDeduplicationId=''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])
    )    
    return "IDs posted"
    

def sendSesEmail(dynamo_result, email):
    client = boto3.client("sns")
    # This address must be verified with Amazon SES.
    SENDER = "vatsala.swaroop@columbia.edu"
    
    # this address must be verified.
    RECIPIENT = email

    AWS_REGION = "us-east-1"
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # The subject line for the email.
    SUBJECT = "Amazon SES Test (SDK for Python)"
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                 "Your Playlist "
                )
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>Amazon SES Test (SDK for Python)</h1>
      <p>This email was sent with
        <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
        <a href='https://aws.amazon.com/sdk-for-python/'>
          AWS SDK for Python (Boto)</a>.</p>
    </body>
    </html>"""            
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Try to send the email.
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

    
def get_messages_from_queue():
    
    queue_url = "   https://sqs.us-east-1.amazonaws.com/854667354389/cloud_project_song_id.fifo"
    
    sqs = boto3.resource('sqs')
    client = boto3.client('sqs')
    queue = sqs.get_queue_by_name(QueueName='cloud_project_song_id.fifo')
    
    response = queue.receive_messages(MessageAttributeNames=['song_id_list'])
    print(response)
    
    receipt_handle = None
    song_id_list = []
    
    for r in response:
        song_id_list = r.message_attributes.get('song_id_list').get('StringValue')
        receipt_handle = r.receipt_handle
    
    if receipt_handle != None:
        resp = client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
    
    final_list = song_id_list.split()
    
    print("fetched_song_id_list", final_list)
    return final_list