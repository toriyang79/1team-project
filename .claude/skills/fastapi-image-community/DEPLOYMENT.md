# 배포 가이드

Docker + Docker Compose를 이용한 AI 이미지 커뮤니티 배포 가이드입니다.

---

## 📁 배포 구성 파일

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 클라이언트 라이브러리)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 업로드 디렉토리 생성
RUN mkdir -p /app/uploads/images

# 비루트 사용자 생성 (보안)
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# 실행 명령 (uvicorn)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (개발용)

```yaml
# docker-compose.yml
version: '3.9'

services:
  # FastAPI 애플리케이션
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-image-community
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/team_db
      - JWT_PUBLIC_KEY=${JWT_PUBLIC_KEY}
      - JWT_ALGORITHM=RS256
      - UPLOAD_DIR=/app/uploads/images
      - MAX_FILE_SIZE=10485760
      - ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp
    volumes:
      - ./uploads:/app/uploads  # 로컬 개발용 볼륨
      - .:/app:ro               # 코드 핫리로드 (개발용)
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  # PostgreSQL 데이터베이스 (팀 공유 - 개발환경용)
  db:
    image: postgres:15-alpine
    container_name: team-postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=team_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network
    restart: unless-stopped

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

### Docker Compose (프로덕션용)

```yaml
# docker-compose.prod.yml
version: '3.9'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-image-community-prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_PUBLIC_KEY=${JWT_PUBLIC_KEY}
      - JWT_ALGORITHM=RS256
      - UPLOAD_DIR=/app/uploads/images
      - MAX_FILE_SIZE=10485760
      - ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp
    volumes:
      - upload_data:/app/uploads
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    networks:
      - app-network
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - upload_data:/var/www/uploads:ro
    depends_on:
      - app
    networks:
      - app-network
    restart: always

networks:
  app-network:
    driver: bridge

volumes:
  upload_data:
```

---

## 🌐 Nginx 설정 (프로덕션)

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    # 로깅
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip 압축
    gzip on;
    gzip_types text/plain application/json;

    # 업스트림 설정 (로드밸런싱)
    upstream fastapi_app {
        server app:8000;
    }

    server {
        listen 80;
        server_name api.example.com;

        # HTTPS 리다이렉트
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.example.com;

        # SSL 인증서
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL 보안 설정
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers on;

        # 보안 헤더
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # 파일 업로드 크기 제한
        client_max_body_size 15M;

        # 정적 파일 서빙 (업로드된 이미지)
        location /uploads/ {
            alias /var/www/uploads/;
            expires 1d;
            add_header Cache-Control "public, immutable";
        }

        # API 프록시
        location / {
            proxy_pass http://fastapi_app;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 타임아웃 설정
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 헬스체크
        location /health {
            proxy_pass http://fastapi_app/health;
        }
    }
}
```

---

## 📋 배포 명령어

### 개발 환경

```bash
# 1. 환경변수 파일 생성
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력

# 2. 컨테이너 빌드 및 시작
docker-compose up --build -d

# 3. 로그 확인
docker-compose logs -f app

# 4. 테이블 생성 (최초 1회)
docker-compose exec app python scripts/create_tables.py

# 5. 컨테이너 중지
docker-compose down
```

### 프로덕션 환경

```bash
# 1. 프로덕션 환경변수 설정
export DATABASE_URL="postgresql+asyncpg://user:pass@prod-db:5432/team_db"
export JWT_PUBLIC_KEY="$(cat /path/to/public_key.pem)"

# 2. 프로덕션 빌드 및 배포
docker-compose -f docker-compose.prod.yml up --build -d

# 3. 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 4. 롤링 업데이트 (무중단 배포)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build app

# 5. 로그 모니터링
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

---

## ☁️ AWS EC2 배포 체크리스트

### 사전 준비
- [ ] EC2 인스턴스 생성 (t3.small 이상 권장)
- [ ] Security Group 설정 (80, 443, 22 포트)
- [ ] Elastic IP 할당
- [ ] 도메인 연결 (Route 53)

### 서버 설정

```bash
# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. 프로젝트 클론
git clone https://github.com/your-team/ai-image-community.git
cd ai-image-community

# 5. SSL 인증서 (Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d api.example.com
```

---

## 📊 모니터링 설정

### 헬스체크 엔드포인트

```python
# main.py에 추가
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/db", tags=["Health"])
async def db_health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
```

### 로그 수집 (선택사항)

```yaml
# docker-compose.prod.yml에 추가
  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
```

---

## 🔄 CI/CD 파이프라인 예시 (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to EC2

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to EC2
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd ~/ai-image-community
            git pull origin main
            docker-compose -f docker-compose.prod.yml up -d --build
```