import json
import io
import os
import base64
import ast
import datetime
import time
import requests
import boto3

from processing.pdf_processor import Doc_Processor

s3 = boto3.client('s3',region_name='us-east-1', 
                     aws_access_key_id=os.environ['AWS_KEY'], 
                     aws_secret_access_key=os.environ['AWS_SECRET'])

def get_secret(secret_name):
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(response["SecretString"])
    return secret

def handle_body(body):
    #simple error handler for bad param json
    #attempts to reconstruct. if failure, report
    restruct = ""
    for t in range(0, len(body)):
        if body[t]=="}" and t<len(body)-1 and body[t+1]!=",":
            restruct+=str(body[t])+","
        else:
            restruct+=str(body[t])
    restruct=[restruct]
    restruct=list(ast.literal_eval(restruct[0]))
    
    tmplist=[]
    for c in restruct:
        tmp = ast.literal_eval(str(c))
        if type(tmp)==tuple:
            tmp=tmp[0]    
        tmplist.append(tmp)
    
    cleaned_params = {}
    for i in tmplist:
        for k,v in i.items():
            if not k in cleaned_params.keys():
                cleaned_params[k]=v
    
    return cleaned_params


def lambda_handler(event, context):
    
    try:
        secrets = get_secret("lambda/file-processing-creds")
        bucket = secrets["AWS_S3_BUCKET_NAME"]
        api_url = secrets["API_CALLBACK_URL"]

    #------------------------------------------------------------------Load SQS Message Event---------------------------------------------------------------------------------------
        #params from SQS message
        try:
            params = json.loads(event['Records'][0]['body'])
        except Exception as err:
            if type(err).__name__=="JSONDecodeError":
                try:
                    #Attempt to fix
                    params = handle_body(event['Records'][0]['body'])
                except Exception as err:
                    #Log Event
                    return 0

        bucket = params['bucket']
        key = params['key']
        record_id = params['record_id']
        metadata = params['metadata']

        #------------------------------------------------------------------File Load---------------------------------------------------------------------------------------
        #Load file S3
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
        except:
            return 0
        
        #Load file bytes
        try:
            file = io.BytesIO(response['Body'].read())
        except Exception as err:
            #Log Event
            return 0
        
        #Null File, Report and Remove
        if file.getbuffer().nbytes==0:
            #Delete file from the queue. No sense in keeping an empty doc
            s3.delete_object(Bucket=bucket, Key=key)
            return 0
        
        #------------------------------------------------------------------Processing---------------------------------------------------------------------------------------
        process_params = metadata["process_params"]
        processor = Doc_Processor(process_params)
        processed_docs = processor.process(file)

        for doc in processed_docs:
            file_name = doc['id']
            folder_name = doc["folder_name"]
     
            new_key = os.path.join(folder_name, file_name)
            
            #Upload to S3
            s3.upload_file(doc['pdf'], Bucket=bucket, Key=new_key)

            #Send message back to API for metadata update
            metadata = {
                "file_name": file_name,
                "object_key": new_key,
                "url": f"https://{bucket}.s3.amazonaws.com/{new_key}",
                "mime_type": "application/pdf",
                "description": doc.get("description",""),
                "tags": ["split"]
                }

            requests.post(api_url, json=metadata)

    except Exception as err:
        #Log Event
        return 0