import boto3
import ssb
import report
import datetime
import os


def lambda_handler(event, context):

    session = boto3.Session()
    sts = session.client('sts')
    lamb = session.client("lambda")
    s3 = session.client('s3')
    sns = session.client("sns")

    try:
        results = ssb.checks(session)
        results.sort(key=lambda x: x["title"])

        account = sts.get_caller_identity()["Account"]
        html = report.generate_report(account, results)

        report_func = os.environ["Report"].split(":")[-1]
        topic = os.environ["Topic"]
        bucket_name = os.environ['Bucket'][13:]

        object_name = f"result-{datetime.date.now().date().isoformat()}.html"
        

        try:
            encoded = bytes(html.encode('UTF-8'))
            s3.put_object(Bucket=bucket_name, Key=object_name, Body=encoded)

            lamb.invoke(FunctionName=report_func, InvocationType='Event')

            return {
            'statusCode': 200,
            "body": "upload success",
            }

        except Exception as e:
            sns.publish(TopicArn=topic, Message=f"""        
                리포트를 s3 버킷에 업로드 중 오류가 발생하였습니다.
                {e}
            """)

            return {
            'statusCode': 400,
            'body': f"upload fail\n {e}",
            "headers": {
                'Content-Type': 'text/html',
            }
            }


    except Exception as e:
        sns.publish(TopicArn=topic, Message=f"""        
            SSB 진단 중 오류가 발생하였습니다.
            {e}
        """)

        return {
            'statusCode': 400,
            'body': str(e),
            "headers": {
                'Content-Type': 'text/html',
            }
        }