import botocore.exceptions
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

import sys, os
sys.path.append(os.path.dirname(__file__))
import text

# def append_alert(ret, alert, title):
#     ret["alerts"].append({
#         "level": alert["level"],
#         "msg": alert["msg"],
#         "title": title
#     })

def append_table(ret, num, row):
    ret["tables"][num]["rows"].append(row)


def check01(session):

    """
        check01 - 대체 연락처 정보를 등록하였는지 확인
        사용 API - get_alternate_contact
        체크 기준 
            - [Success] billing, security, operations에 모두 연락처 존재
            - [Warning] 그 외 경우
    
    """

    
    title = "01 Accurate Information"
    account = session.client('account')

    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["계정 타입", "이름", "이메일", "전화번호"],
                "rows": []
            }
        ]
    }

    level = "Success"
    errorMsg = ""
    
    for t in ["BILLING", "SECURITY", "OPERATIONS"]:
        try:
            contact = account.get_alternate_contact(AlternateContactType=t)["AlternateContact"]
            ret["tables"][0]["rows"].append([t, contact["Name"], contact["EmailAddress"], contact["PhoneNumber"]])

        except botocore.exceptions.ClientError as error :
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                level = "Warning"
                ret["tables"][0]["rows"].append([t, "", "정보 없음", ""])      
            else:
                errorMsg = error.response["Error"]["Message"]
                level = "Error"
    
    
    ret["alerts"].append({
        "level": text.test1["Info"]["level"],
        "msg": text.test1["Info"]["msg"]
    })

    ret["alerts"].append({
        "level": text.test1[level]["level"],
        "msg": text.test1[level]["msg"] + [{"text":errorMsg, "link": ""}],
        "title": text.test1["title"]
    })


    return ret

def check02(session):

    """
        check02 - 루트 유저에 관련된 사항 체크
        사용 API - get_credential_report
        
        check02-1 - 루트 유저 사용 체크
        체크 기준
            - [Success] 루트 유저의 Password, access key을 1일 내에 사용하지 않음
            - [Danger] 그 외 경우

        check02-2 - 루트 유저 MFA 설정 체크
        체크 기준
            - [Success] 루트 유저에 MFA가 설정되어 있음
            - [Danger] 그 외 경우

        check02-3 - 루트 유저 엑세스키 체크
        체크 기준
            - [Success] 루트 유저에 access key가 존재하지 않음
            - [Danger] 그 외 경우
    
    """

    

    title = "02 Protect Root User"
    iam = session.client('iam')

    def check_root_access(date):
        if date == "N/A" or date=="no_information":
            return timedelta(9999)

        return datetime.utcnow() - datetime.fromisoformat(date[:-6])

    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["최근접속일", "MFA 설정", "Access Key1", "Access Key2"],
                "rows": []
            }
        ]
    }

    report_cols={
            "PASSWORD_LAST_USED": 4,
            "MFA": 7,
            "ACCESS_KEY1": 8,
            "ACCESS_KEY1_LAST_USED": 10,
            "ACCESS_KEY2": 13,
            "ACCESS_KEY2_LAST_USED": 15
        }

    
    try:
        response = iam.get_credential_report()
        report = response["Content"].decode('ascii').split()
        root_report = report[1].split(",")

        # print("02-1 Checking root user access")
        last_accessed = min(check_root_access(root_report[report_cols["PASSWORD_LAST_USED"]]), \
            check_root_access(root_report[report_cols["ACCESS_KEY1_LAST_USED"]]),\
                check_root_access(root_report[report_cols["ACCESS_KEY2_LAST_USED"]]))
        code = "Error"
        if last_accessed > timedelta(1):
            code = "Success"
        else:
            code = "Danger"

        ret["alerts"].append({
            "level": text.test2_1[code]["level"],
            "msg": text.test2_1[code]["msg"],
            "title": text.test2_1["title"]
        })

        # print("02-2 Checking root user MFA enabled")
        if root_report[report_cols["MFA"]] == "true":
            code = "Success"
        else:
            code = "Danger"
    
        ret["alerts"].append({
            "level": text.test2_2[code]["level"],
            "msg": text.test2_2[code]["msg"],
            "title": text.test2_2["title"]
        })


        # print("02-3 Checking no access key for root user")
        if root_report[report_cols["ACCESS_KEY1"]] == "false" and \
            root_report[report_cols["ACCESS_KEY2"]] == "false":
            code = "Success"
        else:
            code = "Danger"

        ret["tables"][0]["rows"].append([f"{last_accessed.days}일 전", root_report[report_cols["MFA"]], root_report[report_cols["ACCESS_KEY1"]], root_report[report_cols["ACCESS_KEY2"]]])

        ret["alerts"].append({
            "level": text.test2_3[code]["level"],
            "msg": text.test2_3[code]["msg"],
            "title": text.test2_3["title"]
        })

    except botocore.exceptions.ClientError as error :
        ret["alerts"].append({
            "title": text.test2_3["title"],
            "level": "Error",
            "msg": text.test2_3["Error"]["msg"] + [{"text": error.response["Error"]["Message"], "link":""}]
        })
  


    return ret

def check03(session):

    """
        check03 - IAM 유저에 관련된 사항 체크
        사용 API - get_credential_report, get_account_password_policy
        
        check03-1 - IAM 유저 MFA 설정 체크
        체크 기준
            - [Success] 모든 IAM 유저에 MFA가 설정되어 있음
            - [NO_USER Warning] IAM 유저가 생성되어 있지 않음
            - [Warning] 그 외 경우

        check03-2 - 패스워드 정책 설정 체크
        체크 기준
            - [Success] 패스워드 정책이 설정되어 있음
            - [Warning] 그 외 경우
    
    """

    title = "03 Create Users for Human Identities"
    iam = session.client('iam')
    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["IAM User", "MFA 설정", "Access Key1", "Access Key2"],
                "rows": []
            }
        ]
    }

    report_cols={
        "PASSWORD_LAST_USED": 4,
        "MFA": 7,
        "ACCESS_KEY1": 8,
        "ACCESS_KEY1_LAST_USED": 10,
        "ACCESS_KEY2": 13,
        "ACCESS_KEY2_LAST_USED": 15
    }

    errorMsg = ""
    

    try:
        response = iam.get_credential_report()
        report = response["Content"].decode('ascii').split()
        users = list(map(lambda x: x.split(","), report[2:]))

        code = "Success"
        # print("03-1 Checking MFA setting for users")
        if(len(users) == 0):
            code = "NO_USER"

        for user in users:
            ret["tables"][0]["rows"].append([user[0], user[report_cols["MFA"]], user[report_cols["ACCESS_KEY1"]], user[report_cols["ACCESS_KEY2"]]])
            if user[report_cols["MFA"]] != "true":
                code = "Warning"

        ret["alerts"].append({
            "level": text.test3_1[code]["level"],
            "msg": text.test3_1[code]["msg"],
            "title": text.test3_1["title"]
        })

        # print("03-2 Checcking a password policy")
        code = "Error"
        try:
            policy = iam.get_account_password_policy()
            code = "Success"
            

        except botocore.exceptions.ClientError as error :
            if error.response['Error']['Code'] == 'NoSuchEntity':
                code = "Warning"
            else:
                code = "Error"
                errorMsg = error.response["Error"]["Message"]

    except botocore.exceptions.ClientError as error:
        code = "Error"
        errorMsg = error.response["Error"]["Message"]

    ret["alerts"].append({
        "level": text.test3_2[code]["level"],
        "msg": text.test3_2[code]["msg"] + [{"text":errorMsg, "link": ""}],
        "title": text.test3_2["title"]
    })


    return ret

def check04(session):

    """
        check04 - IAM User와 Group 체크
        사용 API - list_users, list_attached_user_policies, list_user_policies
        
        체크 기준
            - [Success] 모든 IAM 유저에 policy(관리형 정책, 인라인 정책)가 직접 할당되어 있지 않음
            - [NO_USER Warning] IAM 유저가 생성되어 있지 않음
            - [Warning] 그 외 경우
    
    """

    title = "04 Use User Groups"
    iam = session.client('iam')
    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["IAM User", "Attached policies", "Inline policies"],
                "rows": []
            }
        ]
    }

    code = "Success"
    errorMsg = ""

    try:
        users = iam.list_users()["Users"]

        if(len(users) == 0):
            code = "NO_USER"

        
        for user in users:
            attached = iam.list_attached_user_policies(UserName=user["UserName"])["AttachedPolicies"]
            inline = iam.list_user_policies(UserName=user["UserName"])["PolicyNames"]
            ret["tables"][0]["rows"].append([user["UserName"], len(attached), len(inline)])

            if len(attached) > 0:
                code = "Warning"

            if len(inline) > 0:
                code = "Warning"


    except botocore.exceptions.ClientError as error:
        code = "Error"
        errorMsg = error.response["Error"]["Message"]

    ret["alerts"].append({
        "level": text.test4[code]["level"],
        "msg": text.test4[code]["msg"] + [{"text":errorMsg, "link": ""}],
        "title": text.test4['title']
    })

    return ret

def check05(session):

    """
        check05 - CloudTrail 체크
        사용 API - describe_trails, get_trail_status
        
        check05-1 - CloudTrail이 켜져있는지 체크
        체크 기준
            - [Success] 모든 CloudTrail이 켜져 있음
            - [NO_TRAIL Danger] CloudTrail이 없음
            - [ALL_OFF Danger] 모든 CloudTrail이 꺼져있음
            - [Warning] 일부 CloudTrail이 꺼져있음

        check05-2 - CloudTrail이 multi-region인지 체크
        체크 기준
            - [Success] 모든 CloudTrail이 multi-region으로 설정됨
            - [NO_TRAIL Danger] CloudTrail이 없음
            - [NO_MULTI Warning] 모든 CloudTrail이 multi-region으로 설정되지 않음
            - [Warning] 일부 CloudTrail이 multi-region으로 설정되지 않음
    
    """
    

    title = "05 Turn CloudTrail On"
    cloudtrail = session.client('cloudtrail')

    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["Trail", "multi region", "logging"],
                "rows": []
            }
        ]
    }

    code = "Success"
    code_multi_region = "Success"
    logging = 0
    multi_region = 0
    errorMsg = ""

    try:

        trails = cloudtrail.describe_trails()["trailList"]

        if len(trails) == 0:
            code = "NO_TRAIL"
            code_multi_region = "NO_TRAIL"

        for trail in trails:

            # Test5-1 logging status check
            status = cloudtrail.get_trail_status(Name=trail["TrailARN"])
            if(status["IsLogging"]):
                logging += 1
            else:
                code = "Warning"

            # Test5-2 multi-region check
            if(trail["IsMultiRegionTrail"]):
                multi_region += 1
            else:
                code_multi_region = "Warning"

            append_table(ret, 0, [trail["TrailARN"], trail["IsMultiRegionTrail"], status["IsLogging"]])
        
        if code != "NO_TRAIL" and logging == 0:
            code = "ALL_OFF"

        if code != "NO_TRAIL" and multi_region == 0:
            code_multi_region = "NO_MULTI"

    except botocore.exceptions.ClientError as error:
        errorMsg = error.response["Error"]["Message"]
        code = "Error"

    # Test 5-1
    ret["alerts"].append({
        "level": text.test5_1[code]["level"],
        "msg": text.test5_1[code]["msg"] + [{"text":errorMsg, "link":""}],
        "title": text.test5_1["title"]
    })

    # Test 5-2
    if code != "Error":
        ret["alerts"].append({
            "level": text.test5_2[code_multi_region]["level"],
            "msg": text.test5_2[code_multi_region]["msg"] + [{"text":errorMsg, "link":""}],
            "title": text.test5_2["title"]
        })


    return ret

def check06(session):

    """
        check06 - S3 체크
        사용 API - get_caller_identity, get_public_access_block, list_buckets
        
        check06-1 - 계정의 퍼블릭 엑세스 차단 여부
        체크 기준
            - [Success] 모든 퍼블릭 엑세스가 차단되어 있음
            - [Warning] 일부 퍼블릭 엑세스가 허용되어 있음

        check06-2 - 개별 버킷들의 퍼블릭 엑세스 차단 여부
        체크 기준
            - [Success] 모든 버킷의 퍼블릭 엑세스가 차단되어 있음
            - [Danger] 일부 버킷의 퍼블릭 엑세스가 허용되어 있음
    
    """
    
    title = "06 Prevent Public Access to Private S3 Buckets"

    s3 = session.client('s3')
    s3control = session.client('s3control')
    sts = session.client('sts')

    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["이름", "퍼블릭 엑세스"],
                "rows": []
            }
        ]
    }
    code = "Success"
    errorMsg = ""

    try:

        # Test6-1 Account setting
        account_id = sts.get_caller_identity()["Account"]
        account_policy = s3control.get_public_access_block(AccountId=account_id)["PublicAccessBlockConfiguration"]

        for _, val in account_policy.items():
            if val == False:
                code = "Warning"

        append_table(ret, 0, ["Account 설정", "일부 허용" if code == "Warning" else "차단"])

        ret["alerts"].append({
            "title": text.test6_1["title"],
            "level": text.test6_1[code]["level"],
            "msg": text.test6_1[code]["msg"]
        })

        # Test6-2 Individual buckets
        code_bucket = "Success"
        errorMsg_bucket = ""
        buckets = s3.list_buckets()["Buckets"]

        _executor = ThreadPoolExecutor(20)

        async def run(bucket):
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(_executor, lambda: get_pab(bucket))
            return response

        async def execute():
            task_list = [asyncio.ensure_future(run(bucket["Name"])) for bucket in buckets]
            done, _ = await asyncio.wait(task_list)
            results = [d.result() for d in done]
            return results

        def get_pab(bucket):
            try:
                status = s3.get_public_access_block(Bucket=bucket)
                for _, val in status["PublicAccessBlockConfiguration"].items():
                    if val == False:
                        return bucket, False
                return bucket, True
            except:
                return bucket, True


        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(execute())
        loop.close()

        for bucket, status in results:
            if status == False:
                code_bucket = "Danger"
                append_table(ret, 0, [bucket, "일부 허용"])                
        

        if code == "Warning":
            ret["alerts"].append({
                "level":text.test6_2[code_bucket]["level"],
                "msg": text.test6_2[code_bucket]["msg"] + [{"text":errorMsg_bucket, "link":""}],
                "title": text.test6_2['title']
            })

    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
            ret["alerts"].append({
                "title": text.test6_1["title"],
                "level": text.test6_1["Success"]["level"],
                "msg": text.test6_1["Success"]["msg"]
            })
        else:
            code = "Error"
            ret["alerts"].append({
                "title": text.test6_1["title"],
                "level": text.test6_1[code]["level"],
                "msg": text.test6_1[code]["msg"] + [{"text":error.response["Error"]["Message"], "link":""}]
            })

    return ret

def check07(session):

    """
        check07 - 비용 알람 및 루트 계정 엑세스 알람 확인
        사용 API - describe_regions, describe_alarms
        
        체크 기준
            - [Success] CloudWatch 알람이 설정되어 있음(비용과 루트 계정인지 체크 X)
            - [NO_ALARM Warning] CloudWatch 알람이 설정되어 있지 않음
    
    """    

    title = "07 Configure Alarms"
    alarms_tot = []
    
    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["리전", "이름"],
                "rows": []
            }
        ]
    }

    regions = sorted(list(map(lambda x: x["RegionName"], session.client("ec2").describe_regions()["Regions"])))
    _executor = ThreadPoolExecutor(20)

    async def run(region):
        loop = asyncio.get_running_loop()
        cloudwatch = session.client("cloudwatch", region_name=region)
        response = await loop.run_in_executor(_executor, cloudwatch.describe_alarms)
        return response

    async def execute():
        task_list = [asyncio.ensure_future(run(region)) for region in regions]
        done, _ = await asyncio.wait(task_list)

        results = [d.result() for d in done]
        return results

    code = "Success"
    try:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(execute())
        loop.close()

        for result in results:
            for alarm in result["MetricAlarms"]:
                arn = alarm["AlarmArn"].split(":")
                region = arn[3]
                name = arn[6]
                alarms_tot.append((region, name))
            

        for alarm in alarms_tot:
            append_table(ret, 0, [alarm[0], alarm[1]])


        if len(alarms_tot) == 0:
            code = "NO_ALARM"
        else:
            code = "Success"

    except botocore.exceptions.ClientError as error:
        code = "Error"
        errorMsg = error.response["Error"]["Message"]

    ret["alerts"].append({
        "level": text.test7[code]["level"],
        "msg": text.test7[code]["msg"],
        "title": text.test7["title"]
    })
    
    ret["alerts"].append({
        "level": text.test7["Info"]["level"],
        "msg": text.test7["Info"]["msg"],
        "title": text.test7["title"]
    })



    return ret

def check08(session):

    """
        check08 - 리전 별 사용 중인 VPC, Subnets를 ENI 정보를 바탕으로 체크
        사용 API - describe_regions, describe_network_interfaces, describe_vpcs, describe_subnets
        
        체크 기준
            - [Warning] 불필요한 항목을 진단할 수 없어서 EC2 global view 링크만 추가적으로 안내
    
    """  

    
    title = "08 Delete unused VPCs, Subnets & Security Groups"

    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["리전", "사용 중인 VPC 수", "생성된 VPC 수 (default 값)", "사용 중인 서브넷 수", "생성된 서브넷 수 (default 값)"],
                "rows": []
            }
        ]
    }
    
    regions = sorted(list(map(lambda x: x["RegionName"], session.client("ec2").describe_regions()["Regions"])))
    _executor = ThreadPoolExecutor(20)

    async def run(region):
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(_executor, count_vpcs, region)
        return response

    async def execute():
        task_list = [asyncio.ensure_future(run(region)) for region in regions]
        done, _ = await asyncio.wait(task_list)

        results = [d.result() for d in done]
        return results


    def count_vpcs(region):
        ec2 = session.client("ec2", region_name=region)

        vpcs_using = set()
        subnets_using = set()

        for eni in ec2.describe_network_interfaces()["NetworkInterfaces"]:
            if eni["Status"] == "in-use":
                vpcs_using.add(eni["VpcId"])
                subnets_using.add(eni["SubnetId"])
        
        vpcs_exist = len(ec2.describe_vpcs()["Vpcs"])
        subnets = ec2.describe_subnets()["Subnets"]
        subnet_exist = len(subnets)
        subnets_default = 0
        for subnet in subnets:
            if subnet["DefaultForAz"]:
                subnets_default += 1

        return [region, len(vpcs_using), f"{vpcs_exist} (1)", len(subnets_using), f"{subnet_exist}({subnets_default})"]


    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(execute())
        loop.close()

        results.sort(key=lambda x:x[0])
        for row in results:
            append_table(ret, 0, row)

    except Exception as error:
        print(error)

    ret["alerts"].append({
        "level": text.test8["Warning"]["level"],
        "msg": text.test8["Warning"]["msg"],
        "title": text.test8["title"]
    })


    return ret

def check09(session):

    """
        check09 - Trusted Advisor가 켜져있는지 체크
        사용 API - describe_trusted_advisor_checks
        
        체크 기준
            - [Success] Trusted Advisor가 켜져 있음
            - [Subscribe Warning] Business Support 이상의 Support Plan에서만 API를 통하여 상태가 확인 가능함
            - [Warning] Trusted Advisor가 꺼져 있음

    """  
    
    title = "09 Enable AWS Trusted Advisor"

    support = session.client('support', region_name='us-east-1')
    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": ["Trusted Advisor 상태"],
                "rows": []
            }
        ]
    }
    code = "Warning"
    errorMsg = ""

    try:
        support.describe_trusted_advisor_checks(language="en")
        code = "Success"
        append_table(ret, 0, ["켜져 있음"])

    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "SubscriptionRequiredException":
            code = "Subscribe"
            
        else:
            errorMsg = error.response["Error"]["Message"]
            code = "Error"

    ret["alerts"].append({
        "title": text.test9["title"],
        "level": text.test9[code]["level"],
        "msg": text.test9[code]["msg"] + [{"text":errorMsg, "link":""}]
    })

    return ret

def check10(session):

    """
        check10 - GuardDuty가 켜져 있는지 체크
        사용 API - list_detectors, get_detector
        
        체크 기준
            - [Success] GuardDuty가 켜져 있음
            - [Warning] GuardDuty가 꺼져 있음

    """  
    
    title = "10 Enable GuardDuty"
    guardDuty = session.client("guardduty", region_name='ap-northeast-2')
    ret = {
        "title": title,
        "alerts":[],
        "tables": [
            {
                "cols": [],
                "rows": []
            }
        ]
    }
    code = "Success"
    errorMsg = ""

    try:
        detectors = guardDuty.list_detectors()["DetectorIds"]
        if len(detectors) == 0:
            code = "Warning"

        for detector in detectors:
            detector = guardDuty.get_detector(DetectorId=detector)
            status = detector["Status"] 
            if status != "ENABLED":
                code = "Warning"


    except botocore.exceptions.ClientError as error:
        errorMsg = error.response["Error"]["Message"]
        code = "Error"

    ret["alerts"].append({
        "title": text.test10["title"],
        "level": text.test10[code]["level"],
        "msg": text.test10[code]["msg"] + [{"text":errorMsg, "link":""}]
    })


    return ret


async def generate_async_check(idx, check, session, _executor):

    loop = asyncio.get_running_loop()
    s = time.time()
    response = await loop.run_in_executor(_executor, check, session)
    print(f"test{idx:02d}: {time.time() - s:.2}s")
    return response
    


async def async_checks(session, _executor, tests):

    checks = [check01, check02, check03, check04, check05, check06, check07, check08, check09, check10]

    task_list = [asyncio.ensure_future(generate_async_check(i, checks[i-1], session, _executor)) for i in tests]
    

    done, _ = await asyncio.wait(task_list)
    results = [d.result() for d in done]

    return results

def checks(session, tests=[1,2,3,4,5,6,7,8,9,10]):

    _executor = ThreadPoolExecutor(10)

    try:
        iam = session.client('iam')
        iam.generate_credential_report()
    except:
        pass

    s = time.time()
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(async_checks(session, _executor, tests))
    print(f"---------------\ntotal: {time.time() - s:.2}s")

    return result


if __name__ == "__main__":
    import boto3
    session = boto3.Session()

    print(check08(session))
