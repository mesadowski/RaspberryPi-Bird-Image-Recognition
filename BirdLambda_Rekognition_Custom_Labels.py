import boto3
import datetime

BIRD_TOPIC = 'arn:aws:sns:us-east-1:153104479668:bird-results'
SQUIRREL_TOPIC = 'arn:aws:sns:us-east-1:153104479668:squirrel'
REKOGNITION_MODEL = 'arn:aws:rekognition:us-east-1:153104479668:project/Birds/version/Birds.2020-11-26T14.11.34/1606417894474'
CONFIDENCE = 70

# list of labels to ignore
IGNORE = ['Bird Feeder','Animal', 'Mammal', 'Chair', 'Furniture', \
            'Bench', 'Grass', 'Plant', 'Lawn','Lamp','Hydrant', \
            'Fire Hydrant', 'Lamp Post', 'Tree', 'Conifer', 'Water']  

def detect_labels(bucket, key, min_confidence=CONFIDENCE):
    client=boto3.client('rekognition')
    
    dt = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

    response = client.detect_custom_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MinConfidence=min_confidence,
        ProjectVersionArn=REKOGNITION_MODEL)
        
    outstring = '' 
    print(response)
    for Label in response['CustomLabels']:
        if not (Label['Name'] in IGNORE):
            outstring += str(Label['Name']) + ' (Confidence ' + str(Label['Confidence']) + ')\r\n'
            
    if outstring != '':
        outstring = 'Detected  labels for photo at time ' + dt + '\r\n' + outstring + ' in photo ' + key
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
        elif labels != '' :
            send_to_sns(BIRD_TOPIC,labels)
            
        return labels
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
