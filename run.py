# Import all the libraries needed to get started:
from lookoutvision.image import Image
from lookoutvision.manifest import Manifest
from lookoutvision.metrics import Metrics
from lookoutvision.lookoutvision import LookoutForVision

import glob
import logging
import boto3
from botocore.exceptions import ClientError
import datetime
import csv
import re
import os
from time import sleep

session = boto3.Session(region_name='us-east-1')
ssm = session.client('ssm')
s3 = session.client('s3')

response = ssm.get_parameter(
    Name = 'anomaly_threshold'
)

anomaly_threshold = float(response['Parameter']['Value'])


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def save_result(product_id, is_anomaly, reinspection_needed):
    output_filename = str(product_id) + ".csv"

    with open('./tmp/' + output_filename, 'w', newline='') as csvfile:
        fieldnames = ['product_id', 'is_anomaly', 'reinspection_needed', \
                      'year', 'month', 'day', 'hour', 'minute', 'second']
        csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        now = datetime.datetime.now()

        csvwriter.writeheader()
        csvwriter.writerow({'product_id': product_id, \
                            'is_anomaly': is_anomaly, \
                            'reinspection_needed': reinspection_needed, \
                            'year'      : now.year, \
                            'month'     : now.month, \
                            'day'       : now.day, \
                            'hour'      : now.hour, \
                            'minute'    : now.minute, \
                            'second'    : now.second})

    with open("./tmp/" + output_filename, "rb") as f:
        s3.upload_fileobj(f, "lookout-for-vision-workshop", 'result/' + output_filename)


image_list = glob.glob("images/*")
image_list.sort()
#print(image_list[0:3])

l4v = LookoutForVision(project_name="lookout-for-vision-small")

regex = re.compile(r'\d+')

for image_path in image_list:
    prediction = l4v.predict(local_file=image_path)
    print(prediction)
    
    filename = os.path.basename(image_path)
    product_id = (regex.findall(filename))[0]
    print(id)
    
    is_anomaly = prediction['IsAnomalous']
    confidence = prediction['Confidence']
    reinspection_needed = False
    if confidence <= anomaly_threshold:
        reinspection_needed = True
    save_result(product_id, is_anomaly, reinspection_needed)
    #sleep(1)





#result = l4v.predict(local_file="./images/134111_normal.jpeg")

#print(result) 
