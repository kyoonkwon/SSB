test1 = {
    # [Warning] 대체 연락처 정보가 모두 입력되어있는지 확인

    "title": "[Test01] 대체 연락처 정보 입력 여부",

    "Success": {
        "level": "Success",
        "msg": [{"text": "대체 연락처 정보가 모두 입력되어 있습니다. 정확한 정보인지 확인해주세요.", "link": ""}]
    },

    "Warning": {
        "level": "Warning",
        "msg": [{"text": "일부 연락처 정보가 누락되어 있습니다. 연락처 정보를 등록해주세요.", "link": ""}]
    },

    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    },

    "Info": {
        "level": "Info",
        "msg": [
            {"text":"루트 계정을 포함한", "link":""},
            {"text": "연락처 정보 확인", "link": "https://us-east-1.console.aws.amazon.com/billing/home?region=us-east-1#/account"}
        ]
    }
}

test2_1 = {
    # [Danger] 1일 이내에 루트 계정 엑세스가 존재하는지 확인

    "title": "[Test02-1] 루트 계정 엑세스 여부",

    "Success": {
        "level": "Success",
        "msg": [{"text": "1일 이내에 루트 계정으로 엑세스한 기록이 없습니다.", "link": ""}]
    },

    "Danger": {
        "level": "Danger",
        "msg": [{"text": "1일 이내에 루트 계정으로 엑세스한 기록이 존재합니다. 루트 계정으로 직접 AWS의 서비스를 이용하지 마세요.", "link": ""}]
    },

    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }
}

test2_2 = {
    # [Danger] 루트 계정에 MFA가 설정되어 있는지 확인
    "title": "[Test02-2] 루트 계정 MFA 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [{"text": "루트 계정에 MFA가 설정되어 있습니다.", "link": ""}]
    },

    "Danger": {
        "level": "Danger",
        "msg": [
            {"text": "루트 계정에 MFA가 설정되어 있지 않습니다. 링크를 통해 설정해주세요.", "link": ""},
            {"text": "(루트 계정 MFA 설정)", "link": "https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_credentials_mfa_enable_virtual.html#enable-virt-mfa-for-root"}
        ]
    },

    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test2_3 = {
    # [Danger] 루트 계정에 Access Key가 생성되어 있는지 확인

    "title": "[Test02-3] 루트 계정 Access Key 생성 여부",

    "Success": {
        "level": "Success",
        "msg": [{"text": "루트 계정에 Access Key가 생성되어 있지 않습니다.", "link": ""}]
    },

    "Danger": {
        "level": "Danger",
        "msg": [
        {"text": "루트 계정에 Access Key가 생성되어 있습니다. 루트 계정의 Access Key를 삭제해주세요.", "link": ""},
        {"text": "(Access Key 삭제)", "link": "https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_root-user.html#id_root-user_manage_delete-key"}
        ]
    },

    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }
}

test3_1 = {
    # [Warning] IAM User에 MFA 설정이 되어있는지 확인

    "title": "[Test03-1] IAM User MFA 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "모든 IAM User에 MFA 설정이 되어있습니다.", "link": ""}
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
            {"text": "일부 IAM User에 MFA 설정이 되어있지 않습니다.", "link": ""}
        ]
    },

    "NO_USER": {
        "level": "Warning",
        "msg": [
            {"text": "IAM User가 존재하지 않습니다.", "link": ""},
            {"text": "루트 계정을 사용하는 것이 아닌, IAM Role로 엑세스하는 경우 경고를 무시하셔도 좋습니다.", "link": ""},
        ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test3_2 = {
    # [Warning] Password 정책이 있는지 확인

    "title": "[Test03-2] 패스워드 정책 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "패스워드 정책이 설정되어 있습니다.", "link": ""}
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
            {"text": "패스워드 정책이 설정되어있지 않습니다.", "link": ""}
        ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test4 = {
    # [Warning] IAM User에 Policy를 직접 할당했는지

    "title": "[Test04] IAM User에 Policy 할당 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "IAM User에 Policy가 직접 할당되어 있지 않습니다.", "link": ""}
        ]
    },

    "NO_USER": {
        "level": "Warning",
        "msg": [
            {"text": "IAM User가 존재하지 않습니다.", "link": ""},
            {"text": "루트 계정을 사용하는 것이 아닌, IAM Role로 엑세스하는 경우 경고를 무시하셔도 좋습니다.", "link": ""},
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
            {"text": "특정 IAM User에 Policy가 직접 할당되어 있습니다. IAM Group을 통해 할당해주세요.", "link": ""}
        ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test5_1 = {
    # [Danger] CloudTrail이 켜져있는지

    "title": "[Test05-1] CloudTrail이 켜져있는지 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "CloudTrail 모두 켜져있습니다.", "link": ""}
        ]
    },

    "NO_TRAIL": {
        "level": "Danger",
        "msg": [
                {"text": "Trail이 존재하지 않습니다.", "link":""}, 
                {"text":"CloudTrail을 켜주세요.", "link": "https://docs.aws.amazon.com/ko_kr/prescriptive-guidance/latest/aws-startup-security-baseline/acct-07.html"}
            ]
    },

    "ALL_OFF": {
        "level": "Danger",
        "msg": [
            {"text": "모든 CloudTrail이 꺼져있습니다. 보안을 위해 CloudTrail의 로깅을 켜주세요.", "link": ""}
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
            {"text": "일부 CloudTrail이 꺼져있습니다. 보안을 위해 CloudTrail의 로깅을 켜주세요.", "link": ""}
        ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test5_2 = {
    # [Danger] CloudTrail이 Multi-region으로 설정되어 있는지

    "title": "[Test05-2] CloudTrail이 Multi-region으로 설정되어 있는지 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "CloudTrail 모두 Multi-region 설정되어 있습니다.", "link": ""}
        ]
    },

    "NO_TRAIL": {
        "level": "Danger",
        "msg": [
                {"text": "Trail이 존재하지 않습니다.", "link":""}, 
                {"text":"CloudTrail을 켜주세요.", "link": "https://docs.aws.amazon.com/ko_kr/prescriptive-guidance/latest/aws-startup-security-baseline/acct-07.html"}
            ]
    },

    "NO_MULTI": {
        "level": "Warning",
        "msg": [
            {"text": "모든 CloudTrail이 Multi-region으로 설정되어 있지 않습니다.", "link": ""}
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
            {"text": "일부 CloudTrail이 Multi-region으로 설정되어 있지 않습니다.", "link": ""}
        ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}


test6_1 = {
    # [Danger] Account의 S3 퍼블릭 엑세스 설정 확인

    "title": "[Test06-1] Account의 S3 퍼블릭 엑세스 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "Account의 S3 퍼블릭 엑세스 설정이 블록되어 있습니다.", "link": ""}
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
                {"text": "Account의 일부 퍼블릭 엑세스 설정이 허용되어 있습니다. 보안을 위해 가급적 차단해주세요.", "link":""}, 
            ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test6_2 = {
    # [Danger] Bucket의 S3 퍼블릭 엑세스 설정 확인

    "title": "[Test06-2] Bucket의 S3 퍼블릭 엑세스 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "모든 버킷의 S3 퍼블릭 엑세스 설정이 블록되어 있습니다.", "link": ""}
        ]
    },

    "Danger": {
        "level": "Danger",
        "msg": [
                {"text": "일부 버킷의 퍼블릭 엑세스 설정이 허용되어 있습니다. 보안을 위해 가급적 차단해주세요.", "link":""}, 
            ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test7 = {
    # [Warning] 비용 알람 및 루트 계정 엑세스 알람

    "title": "[Test07] 비용 알람 및 루트 계정 엑세스 알람 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "알람이 켜져있습니다. 비용 및 루트 계정 알람인지 확인해 주세요.", "link": ""}
        ]
    },

    "NO_ALARM": {
        "level": "Warning",
        "msg": [
                {"text": "알람이 설정되어있지 않습니다. 보안을 위해 알람을 설정해주세요.", "link":""}, 
            ]
    },
    
    "Info": {
        "level": "Info",
        "msg": [
                {"text": "워크샵", "link": "https://catalog.workshops.aws/startup-security-baseline/en-US/b-securing-your-account/7-configurealarms"},
                {"text": "을 통하여 비용 및 루트 계정 알람을 설정할 수 있습니다.", "link": ""}
            ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test8 = {
    # [Warning] VPC, Subnet, Security Group

    "title": "[Test08] VPC, Subnet, Security Group 사용",

    "Warning": {
        "level": "Warning",
        "msg": [
            {"text": "EC2 Global View 서비스", "link": "https://us-east-1.console.aws.amazon.com/ec2globalview/home"},
            {"text": "를 통해 전체 리전별 VPC/Subnet/SG/ EC2 현황을 확인할 수 있으며 사용하지 않는 리소스 등이 있다면 검토 후 삭제하는 것을 권유드립니다.", "link": ""}
        ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test9 = {
    # [Warning] Trusted Advisor 설정 여부

    "title": "[Test09] Trusted Advisor 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "Trusted Advisor가 작동 중 입니다.", "link": ""}
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
                {"text": "Trusted Advisor가 꺼져있습니다.", "link":""}, 
            ]
    },

    "Subscribe": {
        "level": "Warning",
        "msg": [
                {"text": "Basic Support 플랜의", "link":""},
                {"text": "Trusted Advisor", "link":"https://aws.amazon.com/ko/premiumsupport/knowledge-center/trusted-advisor-intro/"},
                {"text": "에서는 콘솔을 통하여만 확인이 가능합니다. Business Support 이상의 Support Plan 을 이용하시면 Trusted Advisor 에서 더 다양한 지표들에 대해 점검하고 조치 가이드를 받으실 수 있습니다.", "link":""}, 
            ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}

test10 = {
    # [Warning] GuardDuty 설정 여부

    "title": "[Test10] GuardDuty 설정 여부",

    "Success": {
        "level": "Success",
        "msg": [
            {"text": "GuardDuty가 작동 중 입니다.", "link": ""}
        ]
    },

    "Warning": {
        "level": "Warning",
        "msg": [
                {"text": "GuardDuty가 꺼져있습니다.", "link":""}, 
            ]
    },
    
    "Error": {
        "level": "Error",
        "msg": [{"text":"진단 중 에러가 발생하였습니다.", "link": ""}]
    }

}
