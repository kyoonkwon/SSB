import boto3
import datetime
import os

def lambda_handler(event, context):

    resource = boto3.resource('s3')
    bucket_name = os.environ["Bucket"][13:]
    bucket = resource.Bucket(bucket_name)
    lamb = boto3.client('lambda')

    sns = boto3.client("sns")
    topic = os.environ["Topic"]
    
    subscriptions = sns.list_subscriptions_by_topic(TopicArn = topic)["Subscriptions"]
    endpoints = list(map(lambda x: x["Endpoint"], subscriptions))

    for sub in subscriptions:
        if sub["SubscriptionArn"] != "PendingConfirmation":
            break
    else:
        return {
            'statusCode': 400,
            "body": f"이메일로 발송된 topic을 먼저 subscribe 해주세요. {endpoints}",
            "headers": {
                'Content-Type': 'text/html;charset=UTF-8',
            }
        }

    flag = True
    last_modified = datetime.datetime.now(datetime.timezone.utc)
    try:
        last_modified = bucket.Object("temp").get()["LastModified"]
        if datetime.datetime.now(datetime.timezone.utc) - last_modified < datetime.timedelta(minutes=5):
            flag = False

    except Exception as e:
        print(e)
    
    if flag:

        ssb_func = os.environ["SSB"].split(":")[-1]
        lamb.invoke(FunctionName=ssb_func, InvocationType='Event')
        
        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket_name, Key="temp", Body='')
        
        return {
            'statusCode': 200,
            "body": f"""레포트를 생성 중 입니다. 생성 후, 이메일을 통하여 리포트 URL이 발송됩니다.
            {endpoints}
            """,
            "headers": {
                'Content-Type': 'text/html;charset=UTF-8',
            }
        }
    
    else:
        return {
            'statusCode': 400,
            "body": f"API를 너무 자주 호출하였습니다. {(last_modified + datetime.timedelta(minutes=5)).astimezone()} 이후 다시 호출해 주세요.",
            "headers": {
                'Content-Type': 'text/html;charset=UTF-8',
            }
        }