# EC2 배포 시 도메인 설정 가이드

## 1단계: 도메인 구입 및 DNS 설정

### 도메인 구입처
- **국내**: 가비아, 호스팅케이알, 카페24
- **해외**: Namecheap, GoDaddy, Google Domains
- **AWS**: Route 53 (AWS 통합 사용 시 추천)

### DNS 레코드 설정

도메인 관리 페이지에서 다음 레코드를 추가:

```
타입: A 레코드
호스트: @ (또는 root)
값: YOUR_EC2_PUBLIC_IP
TTL: 3600

타입: A 레코드
호스트: www
값: YOUR_EC2_PUBLIC_IP
TTL: 3600
```

**예시:**
- 도메인: `example.com`
- EC2 IP: `54.180.123.45`

```
A 레코드: @ → 54.180.123.45
A 레코드: www → 54.180.123.45
```

---

## 2단계: EC2 배포 전 파일 수정

### 2-1. Nginx 설정 수정

파일: `deploy/nginx/default.conf`

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # 여기를 수정!
    charset utf-8;

    # 나머지는 그대로...
}
```

**실제 예시:**
```nginx
server {
    listen 80;
    server_name mediaplatform.com www.mediaplatform.com;
    charset utf-8;
```

### 2-2. .env 파일 수정

EC2에서 `.env` 파일 생성 후:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,54.180.123.45

# CORS Settings
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

**실제 예시:**
```bash
SECRET_KEY=django-insecure-pr0d-k3y-ch4ng3-th1s-t0-r4nd0m-50-ch4r4ct3rs
DEBUG=False
ALLOWED_HOSTS=mediaplatform.com,www.mediaplatform.com,54.180.123.45

CORS_ALLOWED_ORIGINS=https://mediaplatform.com,https://www.mediaplatform.com
```

---

## 3단계: EC2에서 배포

### 3-1. EC2 접속
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 3-2. 프로젝트 클론
```bash
git clone https://github.com/your-username/common_backend.git
cd common_backend
```

### 3-3. .env 파일 생성
```bash
# 프로덕션 템플릿 복사
cp .env.production.example .env

# 파일 수정 (nano 또는 vi 사용)
nano .env
```

수정 내용:
- `your-domain.com` → 실제 도메인으로 변경
- `SECRET_KEY` → 랜덤한 50자 이상의 문자열로 변경
- `DB_PASSWORD` → 강력한 비밀번호로 변경
- 기타 이메일, AWS 설정 등

### 3-4. Nginx 설정 수정
```bash
nano deploy/nginx/default.conf
```

`server_name` 부분을 실제 도메인으로 수정

### 3-5. Docker Compose 실행
```bash
# 컨테이너 빌드 및 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 마이그레이션 실행
docker-compose exec web python manage.py migrate

# Static 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# Superuser 생성
docker-compose exec web python manage.py createsuperuser
```

---

## 4단계: 도메인 접속 테스트

### HTTP 접속 확인 (30분~2시간 대기 후)
```
http://your-domain.com
http://www.your-domain.com
```

DNS 전파에는 시간이 걸리므로 즉시 안 될 수 있습니다.

### DNS 전파 확인
```bash
# Linux/Mac
nslookup your-domain.com

# 또는
dig your-domain.com
```

결과에 EC2 IP가 나와야 합니다.

---

## 5단계: SSL 인증서 설치 (HTTPS 설정)

### 5-1. Certbot으로 SSL 인증서 발급

```bash
# Nginx 컨테이너 중지
docker-compose stop nginx

# Certbot 설치
sudo apt update
sudo apt install -y certbot

# SSL 인증서 발급
sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  --email your-email@example.com \
  --agree-tos
```

### 5-2. Nginx SSL 설정 추가

파일: `deploy/nginx/default.conf`

기존 설정 위에 추가:

```nginx
# HTTP를 HTTPS로 리다이렉트
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS 설정
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    charset utf-8;

    # SSL 인증서
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # SSL 보안 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Max upload size
    client_max_body_size 100M;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Serve static files
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Serve media files
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy all other requests to Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Websocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 5-3. Docker Compose에 SSL 볼륨 추가

파일: `docker-compose.yml`

nginx 서비스에 볼륨 추가:

```yaml
  nginx:
    image: nginx:alpine
    container_name: media_platform_nginx
    restart: unless-stopped
    volumes:
      - ./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deploy/nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro  # 이 줄 추가!
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    networks:
      - media_platform_network
```

### 5-4. Nginx 재시작

```bash
# 컨테이너 재시작
docker-compose up -d nginx

# 로그 확인
docker-compose logs nginx
```

### 5-5. .env 파일에서 CORS 업데이트

```bash
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### 5-6. SSL 자동 갱신 설정

```bash
# Crontab 편집
sudo crontab -e

# 매일 자정에 인증서 갱신 시도
0 0 * * * certbot renew --quiet --pre-hook "docker-compose -f /home/ubuntu/common_backend/docker-compose.yml stop nginx" --post-hook "docker-compose -f /home/ubuntu/common_backend/docker-compose.yml start nginx"
```

---

## 6단계: 접속 확인

### HTTPS 접속
```
https://your-domain.com
https://www.your-domain.com
```

### 확인 사항
- ✅ HTTP가 HTTPS로 자동 리다이렉트
- ✅ 자물쇠 아이콘 표시 (브라우저)
- ✅ 로그인/회원가입 정상 작동
- ✅ 정적 파일 로딩 정상

---

## 빠른 설정 체크리스트

### 배포 전 (로컬)
- [ ] `deploy/nginx/default.conf`에서 `server_name` 수정
- [ ] `.env.production.example` 참고하여 설정값 확인

### 배포 시 (EC2)
- [ ] DNS A 레코드 설정 (도메인 → EC2 IP)
- [ ] EC2 보안 그룹 설정 (80, 443 포트 오픈)
- [ ] `.env` 파일 생성 및 수정
  - [ ] `ALLOWED_HOSTS` 수정
  - [ ] `SECRET_KEY` 변경
  - [ ] `DEBUG=False` 설정
  - [ ] `DB_PASSWORD` 변경
- [ ] Docker Compose 실행
- [ ] SSL 인증서 발급 (선택사항)
- [ ] HTTPS 설정 (선택사항)

---

## 트러블슈팅

### 1. 도메인으로 접속이 안 돼요
- DNS 전파 대기 (최대 48시간, 보통 30분~2시간)
- `nslookup your-domain.com` 으로 IP 확인
- EC2 보안 그룹에서 80, 443 포트 오픈 확인

### 2. "Bad Gateway" 에러
```bash
# Django 컨테이너 상태 확인
docker-compose ps
docker-compose logs web

# 재시작
docker-compose restart web
```

### 3. Static 파일이 로딩 안 돼요
```bash
# Static 파일 재수집
docker-compose exec web python manage.py collectstatic --noinput

# Nginx 재시작
docker-compose restart nginx
```

### 4. HTTPS 인증서 발급 실패
- 80 포트가 열려있는지 확인
- DNS가 정상적으로 설정되었는지 확인
- nginx 컨테이너가 중지되었는지 확인

---

## 도메인 예시

실제 사용 시 다음과 같이 변경:

| 항목 | 예시 값 | 실제 입력값 |
|------|---------|-------------|
| 도메인 | your-domain.com | mediaplatform.com |
| www 도메인 | www.your-domain.com | www.mediaplatform.com |
| EC2 IP | YOUR_EC2_IP | 54.180.123.45 |
| 이메일 | your-email@example.com | admin@mediaplatform.com |

---

## 참고 자료

- [Let's Encrypt 공식 문서](https://letsencrypt.org/docs/)
- [Nginx SSL 설정 가이드](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Django 배포 체크리스트](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
