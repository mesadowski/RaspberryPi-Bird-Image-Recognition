import boto3
import datetime
import os
import time
from PIL import Image,ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

bucket='my-bird-bucket-custom'
file_path='/home/pi/pi-timolo/media/motion/'
crop_path='/home/pi/pi-timolo/media/cropped/'
bucket_prefix = 'new-bird-images/'

def put_in_bucket(bucket,file,file_path,bucket_prefix):
    s3 = boto3.resource('s3')
    dt = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    new_file_name = dt+'.jpg'
    result = s3.Bucket(bucket).upload_file(file_path+file,bucket_prefix+new_file_name)
    return result

def crop_it(file,file_path):
    im = file_path+file
    uncropped = Image.open(im)
    #uncropped.show()
    s = uncropped.size
    width = s[0]
    height = s[1]
    left = width*0.3
    top = height*0.3
    right = width*0.7
    bottom = height*0.7
    cropped = uncropped.crop((left, top, right, bottom))
    cropped_file_name = 'crop-'+file
    cropped.save(crop_path+cropped_file_name)
    cropped.close()
    #cropped.show()
    return cropped_file_name
    
if __name__ == "__main__":
    while (True):
        filelist = os.listdir(file_path)
        for f in filelist:
            try:
                time.sleep(1)   # try to ensure that the file has been released
                cropped_file_name = crop_it(f,file_path)
                result = put_in_bucket(bucket,cropped_file_name,crop_path,bucket_prefix)
                os.remove(file_path+f)
                os.remove(crop_path+cropped_file_name)
            except Exception as e:
                print(e)
                print("OS or cropping error")
                raise e   
            time.sleep(2)
