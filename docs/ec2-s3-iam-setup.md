# EC2에서 S3 접근을 위한 IAM Role 설정 가이드

## 1단계: IAM 정책 생성

### 1-1. AWS Console에서 IAM 정책 생성

1. AWS Console 로그인
2. **IAM** 서비스로 이동
3. 왼쪽 메뉴에서 **Policies** 클릭
4. **Create policy** 버튼 클릭
5. **JSON** 탭 선택
6. 아래 JSON 붙여넣기 (YOUR_S3_BUCKET을 실제 버킷명으로 변경):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ImageUploadAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR_S3_BUCKET",
        "arn:aws:s3:::YOUR_S3_BUCKET/*"
      ]
    }
  ]
}
```

7. **Next: Tags** 클릭 (태그는 선택사항)
8. **Next: Review** 클릭
9. Policy name: `AIImageCommunityS3Policy` (또는 원하는 이름)
10. Description: `S3 access for AI Image Community uploads`
11. **Create policy** 클릭

---

## 2단계: IAM Role 생성

### 2-1. IAM Role 생성하기

1. IAM 콘솔에서 왼쪽 메뉴 **Roles** 클릭
2. **Create role** 버튼 클릭
3. **Trusted entity type**: **AWS service** 선택
4. **Use case**: **EC2** 선택
5. **Next** 클릭

### 2-2. 권한 연결

1. Permissions policies 검색창에 `AIImageCommunityS3Policy` 입력
2. 방금 생성한 정책 체크박스 선택
3. **Next** 클릭

### 2-3. Role 이름 지정

1. Role name: `AIImageCommunityEC2Role` (또는 원하는 이름)
2. Description: `EC2 role for AI Image Community S3 access`
3. **Create role** 클릭

---

## 3단계: EC2 인스턴스에 IAM Role 연결

### 3-1. EC2 Console에서 설정

1. **EC2** 서비스로 이동
2. 왼쪽 메뉴에서 **Instances** 클릭
3. AI Image Community API가 실행 중인 인스턴스 선택
4. **Actions** → **Security** → **Modify IAM role** 클릭
5. IAM role 드롭다운에서 `AIImageCommunityEC2Role` 선택
6. **Update IAM role** 클릭

### 3-2. 변경사항 적용 확인

인스턴스를 재시작할 필요는 없지만, 컨테이너는 재시작해야 합니다:

```bash
# EC2에 SSH 접속 후
cd /path/to/your/project

# 컨테이너 재시작
docker compose down
docker compose up -d
```

---

## 4단계: 검증 및 테스트

### 4-1. IAM Role 적용 확인

EC2 인스턴스에서 다음 명령어로 IAM Role이 정상 작동하는지 확인:

```bash
# 1. EC2 메타데이터에서 IAM Role 확인
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# 2. Role 이름이 출력되면, 해당 Role의 임시 자격증명 확인
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/AIImageCommunityEC2Role
```

정상이면 AccessKeyId, SecretAccessKey, Token이 출력됩니다.

### 4-2. 컨테이너 내부에서 boto3 테스트

```bash
# 컨테이너 접속
docker exec -it ai_image_community_api bash

# Python으로 S3 접근 테스트 (YOUR_S3_BUCKET을 실제 버킷명으로 변경)
python << 'EOF'
import boto3

try:
    s3 = boto3.client('s3', region_name='ap-northeast-2')

    # 버킷 목록 조회
    response = s3.list_buckets()
    print("✓ S3 연결 성공!")
    print(f"Buckets: {[b['Name'] for b in response['Buckets']]}")

    # 특정 버킷의 객체 목록 조회
    bucket_name = 'YOUR_S3_BUCKET'
    objects = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
    print(f"\n✓ {bucket_name} 버킷 접근 성공!")

except Exception as e:
    print(f"✗ 오류 발생: {e}")
EOF
```

### 4-3. 실제 이미지 업로드 테스트

API를 통해 이미지 업로드를 시도하고 다음을 확인:

```bash
# 컨테이너 로그 확인
docker logs -f ai_image_community_api
```

---

## 문제 해결 (Troubleshooting)

### 문제: "Unable to locate credentials" 오류

**원인**: IAM Role이 EC2 인스턴스에 제대로 연결되지 않음

**해결**:
1. EC2 Console에서 인스턴스의 IAM role이 올바르게 표시되는지 확인
2. 컨테이너를 재시작 (`docker compose restart`)
3. 인스턴스 메타데이터 서비스 확인:
   ```bash
   curl -v http://169.254.169.254/latest/meta-data/
   ```

### 문제: "Access Denied" 오류

**원인**: IAM 정책의 권한이 부족하거나 버킷 정책이 접근을 차단

**해결**:
1. IAM 정책에서 버킷 ARN이 정확한지 확인
2. S3 버킷 정책에서 접근 차단 규칙이 없는지 확인
3. S3 버킷의 "Block public access" 설정 확인

### 문제: ACL 관련 오류 ("AccessControlListNotSupported")

**원인**: S3 버킷이 "Bucket owner enforced" ACL 설정을 사용 중

**해결**:
코드가 이미 처리하고 있으므로, `.env.production`에서 ACL 설정 제거:
```bash
# AWS_S3_ACL=public-read  # 주석 처리 또는 빈 값으로
AWS_S3_ACL=
```

그리고 S3 버킷 정책에서 퍼블릭 읽기 권한 부여:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR_S3_BUCKET/uploads/images/*"
    }
  ]
}
```

---

## 보안 권장사항

1. **최소 권한 원칙**: IAM 정책은 필요한 최소 권한만 부여
2. **특정 경로만 허용**: `uploads/images/*` 경로만 접근 가능하도록 제한 가능
3. **정기 검토**: IAM 정책과 Role을 정기적으로 검토
4. **CloudTrail 활성화**: S3 접근 로그 모니터링

---

## 참고 자료

- [AWS IAM Roles for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
- [Using an IAM role to grant permissions to applications running on Amazon EC2 instances](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2.html)
- [Boto3 Credentials Configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
