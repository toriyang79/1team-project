# 소셜 로그인 설정 가이드

이 가이드는 Google, GitHub, 네이버, 카카오 소셜 로그인을 설정하는 방법을 설명합니다.

## 📋 목차

1. [패키지 설치](#1-패키지-설치)
2. [데이터베이스 마이그레이션](#2-데이터베이스-마이그레이션)
3. [Google OAuth 설정](#3-google-oauth-설정)
4. [GitHub OAuth 설정](#4-github-oauth-설정)
5. [네이버 로그인 설정](#5-네이버-로그인-설정)
6. [카카오 로그인 설정](#6-카카오-로그인-설정)
7. [환경변수 설정](#7-환경변수-설정)
8. [테스트](#8-테스트)

---

## 1. 패키지 설치

```bash
# django-allauth 설치
pip install -r requirements-base.txt

# 또는 직접 설치
pip install django-allauth==65.3.0
```

---

## 2. 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성 및 적용
python manage.py migrate

# Django admin 슈퍼유저 생성 (없다면)
python manage.py createsuperuser
```

---

## 3. Google OAuth 설정

### 3.1 Google Cloud Console에서 프로젝트 생성

1. **Google Cloud Console 접속**: https://console.cloud.google.com/
2. **새 프로젝트 생성** 또는 기존 프로젝트 선택
3. **API 및 서비스** → **사용자 인증 정보** 이동

### 3.2 OAuth 2.0 클라이언트 ID 생성

1. **사용자 인증 정보 만들기** → **OAuth 클라이언트 ID** 선택
2. **동의 화면 구성** (처음인 경우):
   - 사용자 유형: 외부
   - 앱 이름: 미디어 플랫폼
   - 사용자 지원 이메일: 본인 이메일
   - 개발자 연락처 정보: 본인 이메일
3. **OAuth 클라이언트 ID 만들기**:
   - 애플리케이션 유형: 웹 애플리케이션
   - 이름: 미디어 플랫폼
   - 승인된 리디렉션 URI:
     - `http://localhost:8000/accounts/google/login/callback/`
     - `http://your-domain.com/accounts/google/login/callback/` (프로덕션)

### 3.3 클라이언트 ID 및 시크릿 저장

- **클라이언트 ID**: `123456789-abc.apps.googleusercontent.com`
- **클라이언트 시크릿**: `GOCSPX-abc...`

---

## 4. GitHub OAuth 설정

### 4.1 GitHub에서 OAuth App 생성

1. **GitHub 설정 접속**: https://github.com/settings/developers
2. **OAuth Apps** → **New OAuth App** 클릭

### 4.2 애플리케이션 정보 입력

- **Application name**: 미디어 플랫폼
- **Homepage URL**: `http://localhost:8000` (개발) 또는 `https://your-domain.com` (프로덕션)
- **Authorization callback URL**: `http://localhost:8000/accounts/github/login/callback/`

### 4.3 클라이언트 ID 및 시크릿 저장

- **Client ID**: `Iv1.abc123...`
- **Client Secret**: `abc123...` (Generate a new client secret 클릭하여 생성)

---

## 5. 네이버 로그인 설정

### 5.1 네이버 개발자 센터 접속

1. **네이버 개발자 센터**: https://developers.naver.com/
2. **로그인** 후 **Application** → **애플리케이션 등록** 클릭

### 5.2 애플리케이션 등록

- **애플리케이션 이름**: 미디어 플랫폼
- **사용 API**: 네이버 로그인
- **제공 정보 선택**:
  - [x] 회원이름
  - [x] 이메일 주소
  - [x] 프로필 사진
- **환경 추가**:
  - PC 웹: `http://localhost:8000`
- **서비스 URL**: `http://localhost:8000`
- **Callback URL**: `http://localhost:8000/accounts/naver/login/callback/`

### 5.3 클라이언트 ID 및 시크릿 저장

- **Client ID**: `abc123...`
- **Client Secret**: `xyz789...`

---

## 6. 카카오 로그인 설정

### 6.1 Kakao Developers 접속

1. **Kakao Developers**: https://developers.kakao.com/
2. **로그인** 후 **내 애플리케이션** → **애플리케이션 추가하기** 클릭

### 6.2 애플리케이션 등록

- **앱 이름**: 미디어 플랫폼
- **사업자명**: 개인 또는 회사명
- **앱 아이콘** (선택사항)

### 6.3 플랫폼 설정

1. **앱 설정** → **플랫폼** → **Web 플랫폼 등록**
   - 사이트 도메인: `http://localhost:8000`

### 6.4 Redirect URI 설정

1. **제품 설정** → **카카오 로그인** → **활성화 설정** ON
2. **Redirect URI**: `http://localhost:8000/accounts/kakao/login/callback/`

### 6.5 동의 항목 설정

1. **제품 설정** → **카카오 로그인** → **동의 항목**
   - 프로필 정보(닉네임/프로필 사진): 필수 동의
   - 카카오계정(이메일): 필수 동의

### 6.6 클라이언트 정보 저장

1. **앱 설정** → **앱 키**:
   - **REST API 키**: `abc123...` (Client ID로 사용)
   - **JavaScript 키**: `xyz789...` (Key로 사용)
2. **제품 설정** → **카카오 로그인** → **보안**:
   - **Client Secret** 발급 및 사용 설정

---

## 7. 환경변수 설정

`.env` 파일에 다음 내용을 추가합니다:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
GOOGLE_SECRET=GOCSPX-abc...

# GitHub OAuth
GITHUB_CLIENT_ID=Iv1.abc123...
GITHUB_SECRET=abc123...

# 네이버 로그인
NAVER_CLIENT_ID=abc123...
NAVER_SECRET=xyz789...

# 카카오 로그인
KAKAO_CLIENT_ID=abc123...  # REST API 키
KAKAO_SECRET=xyz789...     # Client Secret
KAKAO_KEY=def456...        # JavaScript 키
```

---

## 8. Django Admin에서 Social Application 설정

### 8.1 서버 실행 및 Admin 접속

```bash
python manage.py runserver
```

http://localhost:8000/admin/ 접속

### 8.2 Social Applications 추가

각 소셜 로그인 제공자별로 설정:

#### Google 설정
1. **Social applications** → **Add** 클릭
2. 정보 입력:
   - **Provider**: Google
   - **Name**: Google
   - **Client id**: Google Cloud Console에서 발급받은 Client ID
   - **Secret key**: Google Cloud Console에서 발급받은 Client Secret
   - **Sites**: `example.com` 선택 (Available sites → Chosen sites로 이동)
3. **Save** 클릭

#### GitHub 설정
1. **Social applications** → **Add** 클릭
2. 정보 입력:
   - **Provider**: GitHub
   - **Name**: GitHub
   - **Client id**: GitHub에서 발급받은 Client ID
   - **Secret key**: GitHub에서 발급받은 Client Secret
   - **Sites**: `example.com` 선택
3. **Save** 클릭

#### 네이버 설정
1. **Social applications** → **Add** 클릭
2. 정보 입력:
   - **Provider**: Naver
   - **Name**: Naver
   - **Client id**: 네이버 개발자 센터에서 발급받은 Client ID
   - **Secret key**: 네이버 개발자 센터에서 발급받은 Client Secret
   - **Sites**: `example.com` 선택
3. **Save** 클릭

#### 카카오 설정
1. **Social applications** → **Add** 클릭
2. 정보 입력:
   - **Provider**: Kakao
   - **Name**: Kakao
   - **Client id**: Kakao Developers에서 발급받은 REST API 키
   - **Secret key**: Kakao Developers에서 발급받은 Client Secret
   - **Key**: Kakao Developers에서 발급받은 JavaScript 키
   - **Sites**: `example.com` 선택
3. **Save** 클릭

---

## 9. 테스트

### 9.1 로그인 페이지 접속

http://localhost:8000/login/

### 9.2 소셜 로그인 테스트

1. 각 소셜 로그인 버튼 클릭
2. 소셜 로그인 제공자 페이지로 리다이렉트
3. 계정 선택 및 권한 승인
4. 애플리케이션으로 다시 리다이렉트
5. 자동 회원가입 및 로그인 완료

---

## 10. 문제 해결

### 10.1 Redirect URI 오류

**오류**: `redirect_uri_mismatch`

**해결**:
- 소셜 로그인 제공자 콘솔에서 Redirect URI가 정확히 설정되어 있는지 확인
- URL 끝의 슬래시(`/`) 확인
- 프로토콜(`http` vs `https`) 확인

### 10.2 Social Application이 등록되지 않음

**오류**: `SocialApp matching query does not exist`

**해결**:
- Django Admin에서 해당 Social Application이 추가되었는지 확인
- Sites가 올바르게 선택되었는지 확인

### 10.3 이메일 중복 오류

**오류**: 같은 이메일로 여러 소셜 계정 연결 시

**해결**:
- `apps/users/adapters.py`의 `pre_social_login` 메서드가 자동으로 처리
- 기존 이메일이 있으면 자동으로 소셜 계정 연결

---

## 11. 프로덕션 배포 시 주의사항

### 11.1 Callback URL 업데이트

모든 소셜 로그인 제공자의 Callback URL을 프로덕션 도메인으로 변경:

```
https://your-domain.com/accounts/google/login/callback/
https://your-domain.com/accounts/github/login/callback/
https://your-domain.com/accounts/naver/login/callback/
https://your-domain.com/accounts/kakao/login/callback/
```

### 11.2 HTTPS 필수

프로덕션 환경에서는 반드시 HTTPS를 사용해야 합니다.

### 11.3 환경변수 보안

- `.env` 파일을 Git에 커밋하지 않기
- 프로덕션 서버에서 환경변수를 안전하게 관리

---

## 12. 참고 자료

- [Django Allauth 공식 문서](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [네이버 로그인 API](https://developers.naver.com/docs/login/api/)
- [카카오 로그인](https://developers.kakao.com/docs/latest/ko/kakaologin/common)
