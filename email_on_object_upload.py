from __future__ import print_function
import json
import urllib
import boto3

print('Loading function')

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')
    s3_resource = boto3.resource('s3')
    object_acl = s3_resource.ObjectAcl(bucket, key)
    response = object_acl.put(ACL='public-read')
    object_link = s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key})

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

    me = "sample@gmail.com"
    you = "other_sample@gmail.com"
    text = "Hi DJ!\nHow are you?\nAn image with the name: {} was uploaded to your bucket: {}\nHere is a link to this new image: {}".format(key, bucket, object_link)

    send_ses(me, "S3 Bucket Event", text, you)

    return response['ContentType']


def send_ses(from_addr,
             subject,
             body,
             recipient,
             attachment=None,
             filename=''):
    """Send an email via the Amazon SES service.

    Example:
      send_ses('me@example.com, 'greetings', "Hi!", 'you@example.com)

    Return:
      If 'ErrorResponse' appears in the return message from SES,
      return the message, otherwise return an empty '' string.
    """
    dests = {'ToAddresses': [recipient]}
    msg = {'Subject': {'Data': subject}, 'Body': {'Text': {'Data': body}}}

    ses = boto3.client('ses')
    result = ses.send_email(Source=from_addr, Destination=dests, Message=msg)
    return result if 'ErrorResponse' in result else ''
