# EC2 Docker 배포 가이드

이 가이드는 AWS EC2에 Docker Compose를 사용하여 미디어 플랫폼을 배포하는 방법을 설명합니다.

## 📋 목차

1. [EC2 인스턴스 생성](#1-ec2-인스턴스-생성)
2. [서버 초기 설정](#2-서버-초기-설정)
3. [프로젝트 배포](#3-프로젝트-배포)
4. [도메인 및 SSL 설정](#4-도메인-및-ssl-설정)
5. [모니터링 및 관리](#5-모니터링-및-관리)

---

## 1. EC2 인스턴스 생성

### 1.1 AWS 콘솔에서 EC2 인스턴스 시작

1. **AWS Management Console** → **EC2** → **인스턴스 시작**

2. **AMI 선택**
   - Ubuntu Server 22.04 LTS (HVM), SSD Volume Type

3. **인스턴스 유형 선택**
   - 최소: `t3.small` (2 vCPU, 2GB RAM)
   - 권장: `t3.medium` (2 vCPU, 4GB RAM)
   - 프로덕션: `t3.large` 이상

4. **키 페어 생성/선택** ⭐ 중요!

   SSH 접속을 위한 키 페어를 생성합니다:

   - **새 키 페어 생성** 클릭
   - **키 페어 이름**: 예) `media-platform-key`
   - **키 페어 유형**: RSA
   - **프라이빗 키 파일 형식**: `.pem` (macOS/Linux) 또는 `.ppk` (Windows PuTTY 사용 시)
   - **키 페어 생성** 클릭

   ⚠️ **중요**:
   - `.pem` 파일이 자동으로 다운로드됩니다 (예: `media-platform-key.pem`)
   - **이 파일은 재다운로드가 불가능**하므로 안전한 곳에 보관하세요!
   - 권장 저장 위치:
     - Windows: `C:\Users\우창호\.ssh\media-platform-key.pem`
     - macOS/Linux: `~/.ssh/media-platform-key.pem`

5. **네트워크 설정**
   - VPC: 기본값 또는 커스텀 VPC
   - 퍼블릭 IP 자동 할당: 활성화
   - 보안 그룹 설정:
     - SSH (22) - 내 IP만 허용
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0

6. **스토리지 설정**
   - 최소: 20GB
   - 권장: 30GB 이상 (gp3 타입)

7. **인스턴스 시작**

### 1.2 Elastic IP 할당 (선택사항, 권장)

고정 IP 주소를 위해 Elastic IP를 할당합니다:

1. **EC2** → **Elastic IP** → **Elastic IP 주소 할당**
2. 생성된 IP를 인스턴스에 연결

---

## 2. 서버 초기 설정

### 2.1 EC2 인스턴스 접속

#### 키 파일 및 IP 주소 확인

1. **키 파일**: EC2 생성 시 다운로드한 `.pem` 파일 (예: `media-platform-key.pem`)
2. **퍼블릭 IP**: AWS Console → EC2 → 인스턴스 → 퍼블릭 IPv4 주소 복사

#### 접속 방법

**Windows (PowerShell 또는 CMD):**
```bash
# 예시: 키 파일이 Downloads 폴더에 있고, EC2 IP가 54.180.123.45인 경우
ssh -i "C:\Users\우창호\Downloads\media-platform-key.pem" ubuntu@54.180.123.45
```

**macOS/Linux:**
```bash
# 1. 키 파일 권한 설정 (처음 한 번만)
chmod 400 ~/Downloads/media-platform-key.pem

# 2. SSH 접속
ssh -i ~/Downloads/media-platform-key.pem ubuntu@54.180.123.45
```

**접속 성공 시:**
```
Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.15.0-1028-aws x86_64)
...
ubuntu@ip-172-31-xx-xx:~$
```

#### 접속 문제 해결

**"Permission denied" 오류:**
```bash
# Windows는 해당 없음
# macOS/Linux: 키 파일 권한 확인
chmod 400 your-key.pem
```

**"Connection refused" 또는 "Connection timed out":**
- EC2 보안 그룹에서 SSH(22) 포트가 내 IP에 열려있는지 확인
- EC2 인스턴스가 실행 중인지 확인

### 2.2 자동 설정 스크립트 실행

```bash
# 설정 스크립트 다운로드
wget https://raw.githubusercontent.com/your-repo/main/deploy/ec2-setup.sh
# 또는 프로젝트에서 직접 복사

# 실행 권한 부여
chmod +x ec2-setup.sh

# 스크립트 실행 (sudo 필요)
sudo bash ec2-setup.sh
```

이 스크립트는 다음을 수행합니다:
- ✅ 시스템 패키지 업데이트
- ✅ Docker 및 Docker Compose 설치
- ✅ 방화벽(UFW) 설정
- ✅ Fail2ban 설치 (SSH 보안)
- ✅ 프로젝트 디렉토리 생성

### 2.3 로그아웃 후 재접속

Docker 그룹 권한 적용을 위해 로그아웃 후 다시 접속합니다:

```bash
exit
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

### 2.4 Docker 설치 확인

```bash
docker --version
docker compose version
```

---

## 3. 프로젝트 배포

### 3.1 프로젝트 코드 업로드

#### 방법 1: Git Clone (권장)

```bash
cd /home/ubuntu/app
git clone https://github.com/your-username/1team-project.git .
```

#### 방법 2: SCP로 직접 업로드

```bash
# 로컬에서 실행 (Windows PowerShell 또는 macOS/Linux 터미널)
scp -i "your-key.pem" -r /path/to/1team-project ubuntu@your-ec2-ip:/home/ubuntu/app
```

### 3.2 환경변수 설정

```bash
cd /home/ubuntu/app

# .env 파일 생성
cp .env.docker .env

# .env 파일 편집
vim .env  # 또는 nano .env
```

**중요 설정 항목:**

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-public-ip

# Database Settings
DB_NAME=media_platform
DB_USER=postgres
DB_PASSWORD=strong-database-password-here
DB_HOST=db
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://redis:6379/0

# CORS Settings
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

**보안 팁:**
- `SECRET_KEY`: Python에서 생성
  ```bash
  python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- `DB_PASSWORD`: 강력한 비밀번호 사용 (대소문자, 숫자, 특수문자 포함)

### 3.3 Docker Compose 배포

```bash
cd /home/ubuntu/app

# 전체 스택 빌드 및 시작
docker compose up -d --build

# 로그 확인 (실시간)
docker compose logs -f

# 특정 서비스 로그만 확인
docker compose logs -f web
```

### 3.4 배포 확인

```bash
# 컨테이너 상태 확인
docker compose ps

# 모든 컨테이너가 healthy 상태인지 확인
# NAMES                           STATUS
# media_platform_nginx            Up (healthy)
# media_platform_web              Up (healthy)
# media_platform_celery_worker    Up (healthy)
# media_platform_celery_beat      Up (unhealthy)
# media_platform_db               Up (healthy)
# media_platform_redis            Up (healthy)
```

### 3.5 슈퍼유저 생성

```bash
docker compose exec web python manage.py createsuperuser
```

### 3.6 브라우저에서 접속

- **대시보드**: http://your-ec2-public-ip/
- **API 문서**: http://your-ec2-public-ip/api/docs/
- **Admin**: http://your-ec2-public-ip/admin/

---

## 4. 도메인 및 SSL 설정

### 4.1 도메인 DNS 설정

도메인 등록 업체(가비아, AWS Route 53 등)에서:

1. A 레코드 추가:
   - 호스트: `@` 또는 `your-domain.com`
   - 값: EC2 Elastic IP 주소

2. A 레코드 추가 (www):
   - 호스트: `www`
   - 값: EC2 Elastic IP 주소

### 4.2 Let's Encrypt SSL 인증서 발급

```bash
# Certbot 설치
sudo apt-get install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 이메일 입력 및 약관 동의
# 자동으로 nginx 설정 업데이트
```

### 4.3 자동 갱신 설정

```bash
# Certbot은 자동으로 갱신 크론잡을 설정합니다
# 수동으로 테스트:
sudo certbot renew --dry-run
```

### 4.4 HTTPS 리다이렉트 확인

브라우저에서 `http://your-domain.com` 접속 시 자동으로 `https://your-domain.com`으로 리다이렉트되는지 확인합니다.

---

## 5. 모니터링 및 관리

### 5.1 유용한 Docker 명령어

```bash
# 컨테이너 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f web

# 컨테이너 재시작
docker compose restart web

# 데이터베이스 마이그레이션
docker compose exec web python manage.py migrate

# Django 쉘 접속
docker compose exec web python manage.py shell

# 컨테이너 내부 Bash 접속
docker compose exec web bash

# 정적 파일 재수집
docker compose exec web python manage.py collectstatic --noinput
```

### 5.2 데이터베이스 백업

```bash
# PostgreSQL 데이터베이스 백업
docker exec media_platform_db pg_dump -U postgres media_platform > backup_$(date +%Y%m%d).sql

# 백업 복원
docker exec -i media_platform_db psql -U postgres media_platform < backup_20250102.sql
```

### 5.3 자동 백업 스크립트

```bash
# 백업 스크립트 생성
cat > /home/ubuntu/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# DB 백업
docker exec media_platform_db pg_dump -U postgres media_platform > $BACKUP_DIR/db_$TIMESTAMP.sql

# 미디어 파일 백업
tar -czf $BACKUP_DIR/media_$TIMESTAMP.tar.gz -C /home/ubuntu/app media/

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/ubuntu/backup.sh

# 크론잡 설정 (매일 새벽 3시)
(crontab -l 2>/dev/null; echo "0 3 * * * /home/ubuntu/backup.sh") | crontab -
```

### 5.4 시스템 리소스 모니터링

```bash
# 디스크 사용량
df -h

# 메모리 사용량
free -h

# CPU 사용량
top

# Docker 리소스 사용량
docker stats
```

### 5.5 로그 관리

```bash
# Docker 로그 크기 제한 (docker-compose.yml에 추가)
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 6. 업데이트 및 재배포

### 6.1 자동 배포 스크립트 사용

```bash
cd /home/ubuntu/app
bash deploy/deploy.sh
```

### 6.2 수동 재배포

```bash
cd /home/ubuntu/app

# 최신 코드 가져오기
git pull origin main

# 컨테이너 중지
docker compose down

# 새 이미지 빌드 및 시작
docker compose up -d --build

# 상태 확인
docker compose ps
docker compose logs -f web
```

---

## 7. 문제 해결

### 7.1 컨테이너가 unhealthy 상태

```bash
# 로그 확인
docker compose logs web

# 헬스체크 비활성화 (임시)
# Dockerfile에서 HEALTHCHECK 주석 처리 후 재빌드
```

### 7.2 포트 80/443이 이미 사용 중

```bash
# 포트 사용 프로세스 확인
sudo lsof -i :80
sudo lsof -i :443

# Apache 등 다른 웹서버 중지
sudo systemctl stop apache2
sudo systemctl disable apache2
```

### 7.3 디스크 공간 부족

```bash
# Docker 정리
docker system prune -a --volumes

# 로그 파일 삭제
sudo rm -rf /var/lib/docker/containers/*/*-json.log
```

---

## 8. 보안 체크리스트

- [ ] SSH 포트 변경 (기본 22 → 다른 포트)
- [ ] SSH 비밀번호 로그인 비활성화
- [ ] Fail2ban 활성화
- [ ] 방화벽(UFW) 활성화
- [ ] `.env` 파일 권한 설정: `chmod 600 .env`
- [ ] PostgreSQL 외부 접근 차단 (docker-compose.yml에서 포트 노출 제거)
- [ ] Redis 외부 접근 차단
- [ ] SSL/HTTPS 설정
- [ ] `DEBUG=False` 설정
- [ ] 강력한 `SECRET_KEY` 및 `DB_PASSWORD` 사용
- [ ] 정기 백업 설정
- [ ] CloudWatch 또는 모니터링 도구 설정

---

## 9. 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [AWS EC2 사용 설명서](https://docs.aws.amazon.com/ec2/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Django 배포 체크리스트](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
