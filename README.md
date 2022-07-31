# SSB Self-Test App

본 문서에서는 배포된 lambda 함수들의 구현 로직과 코드를 AWS Severless Application Repository에 package 및 publish하는 방법에 대하여 안내합니다.

애플리케이션의 내용과 사용 방법에 대한 자세한 안내는 워크샵을 참고해주세요. 

## Workshop

워크샵 링크는 이후 업데이트될 예정입니다.

## Requirement

- AWS Account 및 배포에 필요한 권한을 가진 IAM User
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) 설치 및 구성
- [AWS Serverless Application Model](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) (AWS SAM)

## Package & Publish

### Package

Package는 작성한 코드, README, 라이센스 파일 등을 AWS S3에 업로드하고, yaml 형식의 template 파일을 CloudFormation 용 yaml 파일로 변환하는 과정입니다.

새로 publish를 하는 경우가 아니라 기존 애플리케이션을 업데이트하는 경우에는 `template.yaml`에서 Metadata의 SemanticVersion을 변경해주세요.

또한, 아래 명령어를 통하여 package를 진행할 수 있습니다. package가 정상적으로 되지 않을 경우 명령어에 `--force-upload`를 추가해주세요.

```
sam package \
 --template-file template.yaml \
 --output-template-file packaged.yaml \
 --s3-bucket {S3 bucket name} \
```

또한, 위에 명시한 S3 버킷의 리소스 정책에 아래 내용을 추가해주어야 Serverless Application Repository를 통하여 퍼블릭하게 배포가 가능합니다.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "serverlessrepo.amazonaws.com"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::{bucket_name}/*",
            "Condition": {
                "StringEquals": {
                    "aws:SourceAccount": {accountID}
                }
            }
        }
    ]
}
```

### Publish

Serverless Application Repository에 배포하는 방법입니다. 아래 명령어를 통하여 배포가 가능하며, `--region ap-northeast-2`와 같은 방식으로 배포 리전을 특정할 수 있습니다.

```
sam publish --template packaged.yaml
```

또는, Serverless Application Repository의 [내 애플리케이션](https://ap-northeast-2.console.aws.amazon.com/serverlessrepo/home?region=ap-northeast-2#/published-applications)에서 packaged.yaml 파일을 콘솔을 통하여 업로드하여 publish도 가능합니다.

## How it works

날짜는 모두 Asia/Seoul를 기준으로 설정되어 있습니다.
이 값은 `template.yaml`의 lambda 함수의 환경 변수을 통하여 설정할 수 있습니다. 

### entry

생성된 API Endpoint로 접속할 경우, `entry`의 `lambda_function`이 실행됩니다.

위 함수에서, 
1. email subscription이 존재하는지 확인
2. s3 버킷에 temp 파일의 최종 수정 시간을 통하여 마지막 API 호출로부터 5분이상 경과했는지 확인
3. ssb function을 호출 후, temp 파일 업데이트

를 수행합니다.

lambda 함수 생성 시, 
1. 리포트가 저장되어 있는 S3 버킷 ARN
2. SNS Topic의 ARN
3. ssb Lambda 함수의 ARN

을 환경 변수로 미리 설정해주어야 합니다. 이 값은 `template.yaml`에 이미 설정되어 있습니다.


### ssb

`ssb`의 `lambda_function`에서는 AWS SSB의 항목을 체크하고, 결과를 html 형식의 리포트 파일로 생성하여 s3 버킷에 저장합니다. 리포트 파일은 `result-YYYY-MM-DD.html` 형식의 이름을 가지며, 일 단위로 저장됩니다. 하루에 2회 이상 리포트를 생성할 경우, 나중에 생성된 리포트로 덮어 씌워집니다.

lambda 함수 생성 시, 
1. 리포트가 저장되어 있는 S3 버킷 ARN
2. SNS Topic의 ARN
3. report Lambda 함수의 ARN

을 환경 변수로 미리 설정해주어야 합니다. 이 값은 `template.yaml`에 이미 설정되어 있습니다.

구체적인 동작 방식은 [링크](/ssb/README.md)를 참고해주세요.

### report

`report`의 `lambda_function`에서는 `ssb`를 통하여 s3 버킷에 저장된 html 형식의 리포트 파일에 엑세스 할 수 있는 pre-signed URL을 생성하여, 배포 시 구독한 이메일로 발송합니다.

lambda 함수 생성 시, 
1. 리포트가 저장되어 있는 S3 버킷 ARN
2. SNS Topic의 ARN
3. pre-signed URL의 만료 시간

을 환경 변수로 미리 설정해주어야 합니다. 이 값은 `template.yaml`에 이미 설정되어 있습니다.

AWS Python API인 boto3에서 `generate_presign_url`을 사용할 때, `SignatureDoesNotMatch`가 발생합니다. 이는, 아래와 같이 config와 signature_version을 추가하여 해결합니다. ([출처](https://github.com/boto/boto3/issues/2989))

```python
s3 = boto3.client('s3', config=boto3.session.Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))

s3.generate_presigned_url('get_object',
                            Params={'Bucket': bucket_name,
                                    'Key': object_name},
                            ExpiresIn=presigned * 60 * 60)
```