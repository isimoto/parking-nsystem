import os

import boto3
import json

s3 = boto3.resource('s3')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('cars')

SRC_MAIL = "nsystem@example.jp"
DST_MAIL = "nsystem@example.jp"
REGION = "us-east-2"

def get_car(id):
    response = table.get_item(
        Key={
            'car_number': id
        }
    )
    return response['Item']
    
def send_email(source, to, subject, body):
    client = boto3.client('ses', region_name=REGION)

    response = client.send_email(
        Source=source,
        Destination={
            'ToAddresses': [
                to,
            ]
        },
        Message={
            'Subject': {
                'Data': subject,
            },
            'Body': {
                'Text': {
                    'Data': body,
                },
            }
        }
    )
    
    return response
    

def lambda_handler(event, context):
    
    confidence_threshold = 80
    
    # S3にアップされた画像の情報を取得する
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    # bucket_name = 'ibsnsystem-ohaio'
    # object_key = 'pi-ibs001/cars-short.jpg'
    # file_name = os.path.basename(object_key)
    
    # 画像をRekognitionで解析する
    rekognition = boto3.client('rekognition')
    response = rekognition.detect_text(Image={
        'S3Object': {
            'Bucket': bucket_name,
            'Name': object_key
        }
    })
    
    textDetections = response['TextDetections']
    for text in textDetections:
        confidence_score = text['Confidence']
        if confidence_score > confidence_threshold:
            print ('confidence_score:' + str(text['Confidence']))
            print ('Detected text:' + text['DetectedText'])
            
            # dtに車のナンバーを入れる
            dt = text['DetectedText']
            if "-" in dt: #4桁ナンバー
                try:
                    car = get_car(dt)
                    return car
                except KeyError:
                    email = "駐車場Nシステム"
                    message = "登録していない車両を検知しました。"
                    r = send_email(SRC_MAIL, DST_MAIL, email, message)
                    return r
            if " " in dt: #3桁ナンバー
                try:
                    car = get_car(dt)
                    return car
                except KeyError:
                    email = "駐車場Nシステム"
                    message = "登録していない車両を検知しました。"
                    r = send_email(SRC_MAIL, DST_MAIL, email, message)
                    return r
