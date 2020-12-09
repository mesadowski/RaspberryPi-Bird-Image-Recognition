
import boto3
import datetime

CONFIDENCE = 60
WEBSITE_BUCKET = 'mike-bird-website'
BIRD_TOPIC = 'arn:aws:sns:us-east-1:389195416133:bird-topic'
SQUIRREL_TOPIC = 'arn:aws:sns:us-east-1:389195416133:squirrel-topic'
# list of labels to ignore
IGNORE = ['Bird','Bird Feeder','Animal', 'Mammal', 'Chair', 'Furniture', \
            'Bench', 'Grass', 'Plant', 'Lawn','Lamp','Hydrant', \
            'Fire Hydrant', 'Lamp Post', 'Tree', 'Conifer', 'Water', 'Spruce', \
            'Concrete','Letterbox','Mailbox','Aircraft','Vehicle','Transportation', \
            'Airplane', 'Fir','Abies','Cross','Symbol','Hat','Ceiling Fan', \
            'Light Fixture', 'Appliance','Outdoors']  

def detect_labels(bucket, key, min_confidence=CONFIDENCE):
    client=boto3.client('rekognition')
    
    dt = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MinConfidence=min_confidence)
    
    outstring = '' 
    primary = ''
    print(response['Labels'])
    for Label in response['Labels']:
        if not (Label['Name'] in IGNORE):
            if primary == '':
                primary = Label['Name']
            outstring += str(Label['Name']) + ' (Confidence ' + str(Label['Confidence']) + ')\r\n'
            
    if outstring != '':
        outstring = 'Detected  labels for photo at time ' + dt + '\r\n' + outstring + ' in photo ' + key
        print(outstring)
    else:
        print('No labels detected')

    return primary,outstring
    
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
        primary,label_text = detect_labels(bucket, key)
        #print(labels)
        s3_resource = boto3.resource('s3')
        if ('Squirrel' in label_text) or ('Rodent' in label_text) :
            send_to_sns(SQUIRREL_TOPIC,label_text)
        elif label_text != '':     #we'll assume it's a bird, since we already ignored other items which aren't interesting
            send_to_sns(BIRD_TOPIC,label_text)
        
            #if it's a bird pic, move the picture to the website bucket 
            new_path = 'birdpics/_'+key
            old_path = bucket+'/'+key
            print(old_path,new_path)
            s3_resource.Object(WEBSITE_BUCKET,new_path).copy_from(CopySource=old_path)
            
        #delete the original picture
        print('deleting file: ',bucket+key)
        s3_resource.Object(bucket,key).delete()
            
        return label_text
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e
