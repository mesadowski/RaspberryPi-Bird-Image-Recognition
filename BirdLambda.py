

import boto3
import datetime

BIRD_TOPIC = 'arn:aws:sns:us-east-1:153104479668:bird-results'
SQUIRREL_TOPIC = 'arn:aws:sns:us-east-1:153104479668:squirrel'
IGNORE = ['Bird Feeder','Animal', 'Mammal', 'Chair', 'Furniture', 'Bench', 'Grass', 'Plant', 'Lawn']   # list of labels to ignore

def detect_labels(bucket, key, min_confidence=50):
    client=boto3.client('rekognition')
    
    dt = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MinConfidence=min_confidence)
    
    outstring = '' 
    for Label in response['Labels']:
        if not (Label['Name'] in IGNORE):
            outstring += str(Label['Name']) + ' (Confidence ' + str(Label['Confidence']) + ')\r\n'
            
    if outstring != '':
        outstring = 'Detected custom labels for photo at time ' + dt + '\r\n' + outstring
        print(outstring)
    else:
        print('No labels detected')

    return outstring
    
def send_to_sns(topic_arn,msg):

    # Create an SNS client
    sns = boto3.client('sns')

    # Publish labels as a message to the SNS topic
    response = sns.publish(TopicArn=topic_arn,Message=msg)  
    return response

def lambda_handler(event, context):

    # Get the S3 bucket name and file from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print('bucket =',bucket)
    print('key =',key)
    
    try:
        # Call rekognition DetectLabels API to detect labels in S3 object
        labels = detect_labels(bucket, key)
        #print(labels)
        if ('Squirrel' in labels) or ('Rodent' in labels) :
            send_to_sns(SQUIRREL_TOPIC,labels)
        elif "Bird" in labels:
            send_to_sns(BIRD_TOPIC,labels)
            
        return labels
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
