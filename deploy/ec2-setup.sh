#!/bin/bash
# EC2 Ubuntu 서버 초기 설정 스크립트
# 사용법: sudo bash ec2-setup.sh

set -e

echo "================================"
echo "EC2 서버 초기 설정 시작"
echo "================================"

# 시스템 업데이트
echo "1. 시스템 패키지 업데이트..."
apt-get update
apt-get upgrade -y

# 필수 패키지 설치
echo "2. 필수 패키지 설치..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    vim \
    ufw \
    fail2ban

# Docker 설치
echo "3. Docker 설치..."
if ! command -v docker &> /dev/null; then
    # Docker GPG 키 추가
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Docker 저장소 추가
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Docker 설치
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Docker 서비스 시작
    systemctl start docker
    systemctl enable docker

    echo "Docker 설치 완료!"
else
    echo "Docker가 이미 설치되어 있습니다."
fi

# ubuntu 사용자를 docker 그룹에 추가
echo "4. ubuntu 사용자를 docker 그룹에 추가..."
usermod -aG docker ubuntu

# 방화벽 설정
echo "5. 방화벽 설정..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw status

# fail2ban 설정
echo "6. fail2ban 설정..."
systemctl enable fail2ban
systemctl start fail2ban

# 프로젝트 디렉토리 생성
echo "7. 프로젝트 디렉토리 생성..."
mkdir -p /home/ubuntu/app
chown -R ubuntu:ubuntu /home/ubuntu/app

# Docker 버전 확인
echo "================================"
echo "설치 완료!"
echo "================================"
docker --version
docker compose version

echo ""
echo "다음 단계:"
echo "1. 로그아웃 후 다시 로그인 (Docker 그룹 적용)"
echo "2. 프로젝트 코드를 /home/ubuntu/app 에 배포"
echo "3. .env 파일 설정"
echo "4. docker compose up -d --build 실행"
