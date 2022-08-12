import boto3
import datetime
import os

def lambda_handler(event, context):

    s3 = boto3.client('s3', config=boto3.session.Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))
    sns= boto3.client("sns")

    topic = os.environ["Topic"]
    presigned = int(os.environ["Presigned"])
    bucket_name = os.environ["Bucket"][13:]

    object_name = f'result-{datetime.datetime.now().date().isoformat()}.html'


    try:
        response = s3.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=presigned * 60 * 60)        
        
        expired = datetime.datetime.now() + datetime.timedelta(hours=presigned)

        sns.publish(TopicArn=topic, Message=f"""        
        리포트 파일의 미리 서명된(pre-signed) url을 생성하였습니다.
        {expired.isoformat()} 까지 다운로드가 가능합니다.
        url이 길어서 일부만 링크되었을 수 있습니다. 그럴 경우, 아래 링크를 전부 복사하여 접속해주세요.

        {response}
        """)


        return {
            'statusCode': 200,
            "body": "Success",
            "headers": {
                'Content-Type': 'text/html',
            }
        }
        
    except Exception as e:

        sns.publish(TopicArn=topic, Message=f"""        
        리포트를 불러오는 중 오류가 발생하였습니다.

        {e}
        """)

        return {
            'statusCode': 400,
            "body": "Failed",
            "headers": {
                'Content-Type': 'text/html',
            }
        }