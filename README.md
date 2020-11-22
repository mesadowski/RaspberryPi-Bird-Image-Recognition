# RaspberryPi-Bird-Image-Recogition
Image Recognition using Raspberry Pi and AWS Rekognition.  See my blog at mikesml.com for further details.

BirdLambda.py is a Python AWS Lambda function. To set up the Lambda in AWS follow the instruction on the blog mikesml.com

s3_send_bird_pic_crop.py is a Python program that runs in an infinite loop on a Raspberry Pi. It looks for new photos, and sends them to an S3 bucket. You need boto (the AWS Python SDK) installed, and also need AWS credentials stored in the credentials file in your .aws folder on the Pi.  The Raspbery Pi should have a camera connected and also have PI-TIMOLO running. See https://github.com/pageauc/pi-timolo. 

config.py is a sample PI-TIMOLO config file.  Yours will probably need to be adjusted for your situation, but you can start with this.
