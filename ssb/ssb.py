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

    s = time.time()
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

    print(title, time.time() - s)

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

    s = time.time()

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
  

    print(title, time.time() - s)

    return ret

def check03(session):

    s = time.time()

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
            if user[report_cols["MFA"]] == "true":
                # utils.print_pass(f"User <{user[0]}> enables MFA")
                pass
            else:
                code = "Warning"
                # utils.print_fail(f"User <{user[0]}> does not enable MFA")

            ret["tables"][0]["rows"].append([user[0], user[report_cols["MFA"]], user[report_cols["ACCESS_KEY1"]], user[report_cols["ACCESS_KEY2"]]])

        ret["alerts"].append({
            "level": text.test3_1[code]["level"],
            "msg": text.test3_1[code]["msg"],
            "title": text.test3_1["title"]
        })

        # print("03-2 Checcking a password policy")
        code = "Error"
        try:
            policy = iam.get_account_password_policy()
            # utils.print_pass("Set strong password policy to protect account")
            code = "Success"
            

        except botocore.exceptions.ClientError as error :
            if error.response['Error']['Code'] == 'NoSuchEntity':
                # utils.print_fail("No password policy")
                code = "Warning"
            else:
                # utils.print_error(error.response["Error"]["Message"])
                code = "Error"
                errorMsg = error.response["Error"]["Message"]

    except botocore.exceptions.ClientError as error:
        # utils.print_error(error.response["Error"]["Message"])
        code = "Error"
        errorMsg = error.response["Error"]["Message"]

    ret["alerts"].append({
        "level": text.test3_2[code]["level"],
        "msg": text.test3_2[code]["msg"] + [{"text":errorMsg, "link": ""}],
        "title": text.test3_2["title"]
    })

    print(title, time.time() - s)

    return ret

def check04(session):

    s = time.time()

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
            # utils.print_fail("No user exists to access console")
            code = "NO_USER"

        
        for user in users:
            attached = iam.list_attached_user_policies(UserName=user["UserName"])["AttachedPolicies"]
            inline = iam.list_user_policies(UserName=user["UserName"])["PolicyNames"]

            if len(attached) == 0:
                # utils.print_pass(f"User <{user['UserName']}> is not attached policies")
                pass
            else:
                # utils.print_fail(f"User <{user['UserName']}> is attached policies")
                code = "Warning"

            if len(inline) == 0:
                # utils.print_pass(f"User <{user['UserName']}> is not embedded policies")
                pass
            else:
                # utils.print_fail(f"User <{user['UserName']}> is embedded policies")
                code = "Warning"

            # if len(attached) or len(inline):
            #     ret["alerts"].append({"level":"Danger", "msg":[{"text":f"{user['UserName']}에 정책이 직접 할당 되어있습니다.", "link":""}]})

            ret["tables"][0]["rows"].append([user["UserName"], len(attached), len(inline)])


    except botocore.exceptions.ClientError as error:
        # utils.print_error(error.response["Error"]["Message"])
        code = "Error"
        errorMsg = error.response["Error"]["Message"]

    ret["alerts"].append({
        "level": text.test4[code]["level"],
        "msg": text.test4[code]["msg"] + [{"text":errorMsg, "link": ""}],
        "title": text.test4['title']
    })

    print(title, time.time() - s)

    return ret

def check05(session):

    s = time.time()

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
            # utils.print_fail("No trails exists")
            code = "NO_TRAIL"
            code_multi_region = "NO_TRAIL"

        for trail in trails:
            # print(trail["TrailARN"])
            if(trail["IsMultiRegionTrail"]):
                # utils.print_pass("Multi region trail: True")
                multi_region += 1
            else:
                # utils.print_fail("Multi region trail: False")
                code_multi_region = "Warning"

            status = cloudtrail.get_trail_status(Name=trail["TrailARN"])
            if(status["IsLogging"]):
                # utils.print_pass("logging: True")
                logging += 1

            else:
                # utils.print_fail("logging: False")
                # append_alert(ret, "Danger", [[f"{trail['TrailARN']}가 logging되고 있지 않습니다.", ""]])
                code = "Warning"

            append_table(ret, 0, [trail["TrailARN"], trail["IsMultiRegionTrail"], status["IsLogging"]])
        
        if code != "NO_TRAIL" and logging == 0:
            code = "ALL_OFF"

        if code != "NO_TRAIL" and multi_region == 0:
            code_multi_region = "NO_MULTI"

    except botocore.exceptions.ClientError as error:
        errorMsg = error.response["Error"]["Message"]
        code = "Error"



    ret["alerts"].append({
        "level": text.test5_1[code]["level"],
        "msg": text.test5_1[code]["msg"] + [{"text":errorMsg, "link":""}],
        "title": text.test5_1["title"]
    })

    if code != "Error":
        ret["alerts"].append({
            "level": text.test5_2[code_multi_region]["level"],
            "msg": text.test5_2[code_multi_region]["msg"] + [{"text":errorMsg, "link":""}],
            "title": text.test5_2["title"]
        })

    print(title, time.time() - s)

    return ret

def check06(session):

    s = time.time()
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

        account_id = sts.get_caller_identity()["Account"]
        account_policy = s3control.get_public_access_block(AccountId=account_id)["PublicAccessBlockConfiguration"]

        for key, val in account_policy.items():
            if val:
                pass
            else:
                code = "Warning"

        append_table(ret, 0, ["Account 설정", "일부 허용" if code == "Warning" else "차단"])

        ret["alerts"].append({
            "title": text.test6_1["title"],
            "level": text.test6_1[code]["level"],
            "msg": text.test6_1[code]["msg"]
        })

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
            # utils.print_pass(error.response["Error"]["Message"])
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

    
    print(title, time.time() - s)

    return ret

def check07(session):

    s = time.time()

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


    print(title, time.time() - s)

    return ret

def check08(session):

    s = time.time()
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

    print(title, time.time() - s)

    return ret

def check09(session):
    s = time.time()
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
        # utils.print_pass("Trusted Advisor is enabled")
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
    print(title, time.time() - s)

    return ret

def check10(session):
    s = time.time()
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
            # utils.print_fail("GuardDuty is disabled")
            code = "Warning"

        for detector in detectors:
            detector = guardDuty.get_detector(DetectorId=detector)
            status = detector["Status"] 
            if status == "ENABLED":
                # utils.print_pass("GuardDuty is enabled")
                # append_alert(ret, "Success", [["GuardDuty가 활성화되어 있습니다.", ""]])
                pass

            else:
                # utils.print_fail("GuardDuty is disabled")
                code = "Warning"


    except botocore.exceptions.ClientError as error:
        errorMsg = error.response["Error"]["Message"]
        code = "Error"

    ret["alerts"].append({
        "title": text.test10["title"],
        "level": text.test10[code]["level"],
        "msg": text.test10[code]["msg"] + [{"text":errorMsg, "link":""}]
    })

    print(title, time.time() - s)

    return ret


async def generate_async_check(check, session, _executor):

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(_executor, check, session)
    return response
    


async def async_checks(session, _executor, tests):

    checks = [check01, check02, check03, check04, check05, check06, check07, check08, check09, check10]

    task_list = [asyncio.ensure_future(generate_async_check(checks[i-1], session, _executor)) for i in tests]
    

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
    print(time.time() - s)

    return result


if __name__ == "__main__":
    import boto3
    session = boto3.Session()

    print(check08(session))
