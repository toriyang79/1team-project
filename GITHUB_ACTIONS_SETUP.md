# GitHub Actions 자동 배포 설정 가이드

이 가이드는 GitHub Actions를 사용하여 EC2 서버에 자동으로 배포하는 방법을 설명합니다.

## 1. GitHub Secrets 설정

GitHub 저장소의 **Settings** > **Secrets and variables** > **Actions**로 이동하여 다음 Secrets를 추가하세요:

### 필수 Secrets

| Secret 이름 | 설명 | 예시 값 |
|------------|------|--------|
| `EC2_SSH_KEY` | EC2 접속용 SSH 개인키 (PEM 파일 내용) | `-----BEGIN RSA PRIVATE KEY-----\n...` |
| `EC2_HOST` | EC2 서버 IP 주소 | `15.165.73.247` |
| `SECRET_KEY` | Django SECRET_KEY (프로덕션용) | 랜덤 문자열 (50자 이상) |
| `ALLOWED_HOSTS` | Django ALLOWED_HOSTS | `15.165.73.247,yourdomain.com` |
| `DB_NAME` | 데이터베이스 이름 | `media_platform` |
| `DB_USER` | 데이터베이스 사용자 | `postgres` |
| `DB_PASSWORD` | 데이터베이스 비밀번호 | 강력한 비밀번호 |
| `CORS_ALLOWED_ORIGINS` | CORS 허용 도메인 | `http://yourdomain.com,https://yourdomain.com` |

### 선택 Secrets (이메일 기능 사용 시)

| Secret 이름 | 설명 |
|------------|------|
| `EMAIL_HOST_USER` | 이메일 발신 주소 |
| `EMAIL_HOST_PASSWORD` | 이메일 계정 비밀번호 또는 앱 비밀번호 |

---

## 2. EC2_SSH_KEY 설정 방법

### Step 1: PEM 파일 내용 복사
```bash
cat likelion.pem
```

### Step 2: GitHub Secrets에 추가
1. 출력된 전체 내용을 복사합니다 (-----BEGIN RSA PRIVATE KEY----- 부터 -----END RSA PRIVATE KEY----- 까지)
2. GitHub 저장소의 Settings > Secrets and variables > Actions로 이동
3. "New repository secret" 클릭
4. Name: `EC2_SSH_KEY`
5. Value: 복사한 PEM 파일 내용 전체 붙여넣기
6. "Add secret" 클릭

---

## 3. SECRET_KEY 생성 방법

Django 프로덕션 환경용 SECRET_KEY를 생성합니다:

```python
# Python을 실행하여 새로운 SECRET_KEY 생성
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

또는 온라인 생성기 사용:
- https://djecrety.ir/

생성된 키를 `SECRET_KEY` Secret에 저장하세요.

---

## 4. EC2 서버 초기 설정

배포가 작동하려면 EC2 서버에서 다음을 확인하세요:

### 보안 그룹 설정
EC2 보안 그룹에서 다음 포트를 열어야 합니다:
- **22** (SSH) - GitHub Actions 접속용
- **80** (HTTP) - 웹 서비스용
- **443** (HTTPS) - SSL 사용 시

### EC2 인스턴스 확인사항
```bash
# EC2 서버에 SSH 접속
ssh -i likelion.pem ubuntu@15.165.73.247

# Docker 설치 확인 (없으면 자동 설치됨)
docker --version
docker compose version

# 앱 디렉토리 생성
sudo mkdir -p /home/ubuntu/app
sudo chown ubuntu:ubuntu /home/ubuntu/app
```

---

## 5. 배포 실행

### 자동 배포 (Push 시)
다음 브랜치에 push하면 자동으로 배포됩니다:
- `main`
- `feature/common_backend`

```bash
git add .
git commit -m "배포 설정 완료"
git push origin feature/common_backend
```

### 수동 배포
GitHub 저장소의 **Actions** 탭에서:
1. "Deploy to EC2" 워크플로우 선택
2. "Run workflow" 클릭
3. 브랜치 선택 후 실행

---

## 6. 배포 확인

### GitHub Actions에서 확인
1. GitHub 저장소의 **Actions** 탭으로 이동
2. 실행 중인 워크플로우 클릭
3. 각 단계의 로그 확인

### EC2 서버에서 확인
```bash
# EC2 서버 접속
ssh -i likelion.pem ubuntu@15.165.73.247

# 앱 디렉토리로 이동
cd /home/ubuntu/app

# 컨테이너 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f web

# 서비스 테스트
curl http://localhost
```

### 브라우저에서 확인
```
http://15.165.73.247
```

---

## 7. 트러블슈팅

### 배포가 실패하는 경우

**1. SSH 연결 실패**
- EC2 보안 그룹에서 SSH 포트(22) 확인
- EC2 인스턴스가 실행 중인지 확인
- `EC2_SSH_KEY` Secret이 올바른지 확인

**2. Docker 관련 오류**
```bash
# EC2 서버에서 Docker 재시작
sudo systemctl restart docker

# Docker 그룹에 사용자 추가
sudo usermod -aG docker ubuntu
# 로그아웃 후 다시 로그인 필요
```

**3. .env 파일 오류**
- GitHub Secrets가 모두 설정되었는지 확인
- Secret 이름이 정확한지 확인

**4. 컨테이너가 시작되지 않는 경우**
```bash
# 로그 확인
docker compose logs

# 특정 서비스 로그
docker compose logs web
docker compose logs db

# 컨테이너 재시작
docker compose restart
```

---

## 8. 주요 명령어

### 로컬에서
```bash
# 변경사항 커밋 및 푸시 (자동 배포 트리거)
git add .
git commit -m "배포"
git push origin feature/common_backend
```

### EC2 서버에서
```bash
# 컨테이너 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f

# 컨테이너 재시작
docker compose restart

# 컨테이너 중지
docker compose down

# 컨테이너 시작
docker compose up -d

# 특정 컨테이너 접속
docker compose exec web bash

# 디스크 정리
docker system prune -f
```

---

## 9. 롤백 방법

배포 후 문제가 발생한 경우:

### 방법 1: 이전 커밋으로 롤백
```bash
# 이전 커밋 확인
git log --oneline

# 특정 커밋으로 롤백
git revert <commit-hash>
git push origin feature/common_backend
```

### 방법 2: 서버에서 직접 롤백
```bash
# EC2 서버 접속
ssh -i likelion.pem ubuntu@15.165.73.247

# 백업에서 데이터베이스 복구
cd /home/ubuntu/backups
docker exec -i media_platform_db psql -U postgres media_platform < db_backup_YYYYMMDD_HHMMSS.sql
```

---

## 10. 보안 권장사항

1. **SECRET_KEY**: 절대 코드에 하드코딩하지 마세요
2. **DB_PASSWORD**: 강력한 비밀번호 사용
3. **DEBUG**: 프로덕션에서는 항상 `False`
4. **ALLOWED_HOSTS**: 실제 도메인만 포함
5. **SSH Key**: GitHub Secrets에만 저장, 절대 공개하지 마세요
6. **.env 파일**: Git에 커밋하지 마세요 (.gitignore에 포함됨)

---

## 참고 자료

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Django 배포 가이드](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
