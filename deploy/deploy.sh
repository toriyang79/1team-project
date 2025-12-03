#!/bin/bash
# EC2 서버 배포 스크립트
# 사용법: bash deploy.sh

set -e

APP_DIR="/home/ubuntu/app"
BACKUP_DIR="/home/ubuntu/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "================================"
echo "배포 시작: $TIMESTAMP"
echo "================================"

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 기존 컨테이너 백업 (선택사항)
if [ -d "$APP_DIR" ]; then
    echo "1. 기존 데이터 백업..."

    # 데이터베이스 백업
    if docker ps | grep -q media_platform_db; then
        echo "   - PostgreSQL 데이터베이스 백업..."
        docker exec media_platform_db pg_dump -U postgres media_platform > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
    fi

    # 미디어 파일 백업
    if [ -d "$APP_DIR/media" ]; then
        echo "   - 미디어 파일 백업..."
        tar -czf $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz -C $APP_DIR media/
    fi
fi

# Git Pull (코드가 이미 있는 경우)
if [ -d "$APP_DIR/.git" ]; then
    echo "2. 최신 코드 가져오기..."
    cd $APP_DIR
    git fetch origin
    git pull origin main  # 또는 사용 중인 브랜치 이름
else
    echo "2. Git 저장소가 없습니다. 수동으로 코드를 배포하세요."
fi

# .env 파일 확인
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚠️  경고: .env 파일이 없습니다!"
    echo "   .env.docker 파일을 .env로 복사하고 설정을 수정하세요:"
    echo "   cp .env.docker .env"
    echo "   vim .env"
    exit 1
fi

# Docker Compose로 배포
echo "3. Docker 이미지 빌드 및 컨테이너 시작..."
cd $APP_DIR

# 기존 컨테이너 중지
echo "   - 기존 컨테이너 중지..."
docker compose down

# 새 이미지 빌드 및 시작
echo "   - 새 이미지 빌드..."
docker compose build --no-cache

echo "   - 컨테이너 시작..."
docker compose up -d

# 컨테이너 상태 확인
echo "4. 컨테이너 상태 확인..."
sleep 5
docker compose ps

# 로그 확인
echo "================================"
echo "배포 완료!"
echo "================================"
echo ""
echo "로그 확인: docker compose logs -f web"
echo "상태 확인: docker compose ps"
echo "컨테이너 접속: docker compose exec web bash"
echo ""
echo "백업 위치: $BACKUP_DIR"
