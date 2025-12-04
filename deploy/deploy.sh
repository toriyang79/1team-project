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
        docker exec media_platform_db pg_dump -U postgres media_platform > $BACKUP_DIR/db_backup_$TIMESTAMP.sql || echo "   - DB 백업 실패 (계속 진행)"
    fi

    # 미디어 파일 백업
    if [ -d "$APP_DIR/media" ]; then
        echo "   - 미디어 파일 백업..."
        tar -czf $BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz -C $APP_DIR media/ || echo "   - 미디어 백업 실패 (계속 진행)"
    fi
fi

# .env 파일 확인
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚠️  경고: .env 파일이 없습니다!"
    echo "   GitHub Actions에서 .env 파일이 생성되어야 합니다."
    exit 1
fi

# Docker Compose로 배포
echo "2. Docker 이미지 빌드 및 컨테이너 시작..."
cd $APP_DIR

# 기존 컨테이너 중지
echo "   - 기존 컨테이너 중지..."
docker compose down || echo "   - 실행 중인 컨테이너 없음"

# 사용하지 않는 이미지 정리
echo "   - 사용하지 않는 Docker 리소스 정리..."
docker system prune -f

# 새 이미지 빌드 및 시작
echo "   - 새 이미지 빌드..."
docker compose build --no-cache

echo "   - 컨테이너 시작..."
docker compose up -d

# 컨테이너 상태 확인
echo "3. 컨테이너 상태 확인..."
sleep 10
docker compose ps

# 헬스체크
echo "4. 서비스 헬스체크..."
for i in {1..30}; do
    if docker compose ps | grep -q "healthy"; then
        echo "   ✓ 서비스가 정상적으로 시작되었습니다!"
        break
    fi
    echo "   - 대기 중... ($i/30)"
    sleep 2
done

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
echo ""
echo "최근 로그:"
docker compose logs --tail=20 web
