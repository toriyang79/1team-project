# 소셜 로그인 설정 가이드

React + Django 프로젝트에서 소셜 로그인(Google, GitHub, Naver, Kakao)을 설정하는 방법입니다.

## 📋 목차

1. [OAuth 앱 생성 및 설정](#1-oauth-앱-생성-및-설정)
2. [Django 설정](#2-django-설정)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [Django Admin에서 Social App 등록](#4-django-admin에서-social-app-등록)
5. [사용 방법](#5-사용-방법)
6. [트러블슈팅](#6-트러블슈팅)

---

## 1. OAuth 앱 생성 및 설정

### 1.1 Google OAuth

1. **Google Cloud Console** 접속: https://console.cloud.google.com/
2. 프로젝트 생성 또는 선택
3. **API 및 서비스 > OAuth 동의 화면**
   - 사용자 유형: 외부
   - 앱 이름, 이메일 등 입력
4. **사용자 인증 정보 > OAuth 2.0 클라이언트 ID 만들기**
   - 애플리케이션 유형: 웹 애플리케이션
   - 승인된 리디렉션 URI:
     ```
     http://localhost:8000/accounts/google/login/callback/
     https://www.artlion.p-e.kr/accounts/google/login/callback/
     ```
5. **클라이언트 ID**와 **클라이언트 보안 비밀번호** 저장

### 1.2 GitHub OAuth

1. **GitHub Settings** 접속: https://github.com/settings/developers
2. **OAuth Apps > New OAuth App**
3. 정보 입력:
   - Application name: Artlion
   - Homepage URL: `https://www.artlion.p-e.kr`
   - Authorization callback URL:
     ```
     http://localhost:8000/accounts/github/login/callback/
     https://www.artlion.p-e.kr/accounts/github/login/callback/
     ```
4. **Client ID**와 **Client Secret** 생성 및 저장

### 1.3 Naver OAuth

1. **Naver Developers** 접속: https://developers.naver.com/apps/#/register
2. **애플리케이션 등록**
3. 정보 입력:
   - 애플리케이션 이름: Artlion
   - 사용 API: 네이버 로그인
   - 서비스 URL: `https://www.artlion.p-e.kr`
   - Callback URL:
     ```
     http://localhost:8000/accounts/naver/login/callback/
     https://www.artlion.p-e.kr/accounts/naver/login/callback/
     ```
4. **Client ID**와 **Client Secret** 확인

### 1.4 Kakao OAuth

1. **Kakao Developers** 접속: https://developers.kakao.com/
2. **내 애플리케이션 > 애플리케이션 추가하기**
3. **앱 설정 > 플랫폼 > Web 플랫폼 등록**
   - 사이트 도메인: `https://www.artlion.p-e.kr`
4. **제품 설정 > 카카오 로그인**
   - 활성화 설정: ON
   - Redirect URI:
     ```
     http://localhost:8000/accounts/kakao/login/callback/
     https://www.artlion.p-e.kr/accounts/kakao/login/callback/
     ```
5. **REST API 키** 확인 (Client ID로 사용)
6. **보안 > Client Secret** 생성 (필수 설정)

---

## 2. Django 설정

Django Allauth가 이미 설치되어 있으므로 추가 설치는 필요 없습니다.

### 2.1 settings.py 확인

`config/settings.py`에 다음 설정이 있는지 확인:

```python
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.naver',
    'allauth.socialaccount.providers.kakao',
]

SITE_ID = 1

# Allauth 설정
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
SOCIALACCOUNT_AUTO_SIGNUP = True
```

### 2.2 마이그레이션

```bash
python manage.py migrate
```

---

## 3. 환경 변수 설정

### 3.1 .env 파일 수정

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Naver OAuth
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret

# Kakao OAuth
KAKAO_CLIENT_ID=your-kakao-rest-api-key
KAKAO_CLIENT_SECRET=your-kakao-client-secret
```

### 3.2 프로덕션 환경 (GitHub Secrets)

GitHub Actions를 사용하는 경우 다음 Secrets 추가:

1. GitHub Repository > Settings > Secrets and variables > Actions
2. 다음 Secrets 추가:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GITHUB_CLIENT_ID`
   - `GITHUB_CLIENT_SECRET`
   - `NAVER_CLIENT_ID`
   - `NAVER_CLIENT_SECRET`
   - `KAKAO_CLIENT_ID`
   - `KAKAO_CLIENT_SECRET`

---

## 4. Django Admin에서 Social App 등록

### 4.1 슈퍼유저 생성 (아직 없는 경우)

```bash
python manage.py createsuperuser
```

### 4.2 Django Admin 접속

1. 서버 실행: `python manage.py runserver`
2. http://localhost:8000/admin/ 접속
3. 슈퍼유저로 로그인

### 4.3 Social applications 등록

**Google**:
- Provider: Google
- Name: Google
- Client id: (Google Cloud Console에서 복사한 Client ID)
- Secret key: (Google Cloud Console에서 복사한 Client Secret)
- Sites: example.com 선택 (또는 추가)

**GitHub**:
- Provider: GitHub
- Name: GitHub
- Client id: (GitHub에서 복사한 Client ID)
- Secret key: (GitHub에서 복사한 Client Secret)
- Sites: example.com 선택

**Naver**:
- Provider: Naver
- Name: Naver
- Client id: (Naver에서 복사한 Client ID)
- Secret key: (Naver에서 복사한 Client Secret)
- Sites: example.com 선택

**Kakao**:
- Provider: Kakao
- Name: Kakao
- Client id: (Kakao REST API 키)
- Secret key: (Kakao Client Secret)
- Sites: example.com 선택

---

## 5. 사용 방법

### 5.1 API 엔드포인트

소셜 로그인은 다음 엔드포인트를 통해 시작됩니다:

```
GET /api/v1/social/{provider}/
```

**지원되는 Provider**:
- `google`
- `github`
- `naver`
- `kakao`

**예시**:
```
http://localhost:8000/api/v1/social/google/
http://localhost:8000/api/v1/social/github/
http://localhost:8000/api/v1/social/naver/
http://localhost:8000/api/v1/social/kakao/
```

### 5.2 React에서 사용

React 컴포넌트에서 소셜 로그인 버튼을 클릭하면:

```typescript
// SocialLoginButtons 컴포넌트 사용 예시
import SocialLoginButtons from '../components/SocialLoginButtons';

<SocialLoginButtons />
```

버튼 클릭 시 자동으로:
1. Django API로 리다이렉트
2. OAuth 제공자로 리다이렉트
3. 사용자 인증
4. Django 콜백으로 돌아옴
5. JWT 토큰 발급
6. React 앱의 `/social-callback`으로 리다이렉트 (토큰 포함)
7. 토큰 저장 후 대시보드로 이동

---

## 6. 트러블슈팅

### 6.1 "Redirect URI mismatch" 에러

**원인**: OAuth 앱에 등록된 Redirect URI와 실제 콜백 URL이 다름

**해결**:
1. OAuth 제공자 설정에서 정확한 콜백 URL 등록 확인
2. 프로토콜 확인 (http vs https)
3. 포트 번호 확인 (localhost:8000)
4. 끝에 슬래시(/) 확인

**정확한 형식**:
```
http://localhost:8000/accounts/google/login/callback/
https://www.artlion.p-e.kr/accounts/google/login/callback/
```

### 6.2 "SocialApp matching query does not exist" 에러

**원인**: Django Admin에서 Social App이 등록되지 않음

**해결**:
1. Django Admin 접속
2. Social applications에서 해당 Provider 추가
3. Sites에 올바른 도메인 선택

### 6.3 CORS 에러

**원인**: React 앱과 Django API가 다른 도메인

**해결**:
`config/settings.py`에서 CORS 설정 확인:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://www.artlion.p-e.kr',
]
```

### 6.4 토큰이 저장되지 않음

**원인**: 로컬 스토리지 접근 문제 또는 콜백 처리 오류

**해결**:
1. 브라우저 개발자 도구 > Console 확인
2. Network 탭에서 API 응답 확인
3. Application 탭 > Local Storage 확인

### 6.5 프로덕션에서 작동하지 않음

**확인 사항**:
1. ✅ 프로덕션 도메인이 OAuth 앱에 등록되어 있는지
2. ✅ 환경 변수가 서버에 올바르게 설정되어 있는지
3. ✅ HTTPS 사용 여부 (대부분의 OAuth는 HTTPS 필수)
4. ✅ Django Admin에서 Sites 도메인이 올바른지

---

## 7. 보안 고려사항

### 7.1 Client Secret 보호

- ❌ **절대** Git에 커밋하지 마세요
- ✅ 환경 변수 (.env) 사용
- ✅ GitHub Secrets 사용 (CI/CD)
- ✅ .gitignore에 .env 추가

### 7.2 Redirect URI 화이트리스트

- ✅ 필요한 URI만 등록
- ❌ 와일드카드(*) 사용 금지
- ✅ HTTPS 사용 (프로덕션)

### 7.3 State 파라미터

Django Allauth가 자동으로 CSRF 보호를 위한 state 파라미터를 처리합니다.

---

## 8. 테스트 방법

### 8.1 로컬 테스트

1. Django 서버 실행:
   ```bash
   python manage.py runserver
   ```

2. React 개발 서버 실행:
   ```bash
   cd frontend
   npm start
   ```

3. http://localhost:3000/login 접속

4. 소셜 로그인 버튼 클릭

5. 인증 후 대시보드로 리다이렉트 확인

### 8.2 프로덕션 테스트

1. 프로덕션 환경에 배포
2. https://www.artlion.p-e.kr/login 접속
3. 소셜 로그인 테스트
4. 브라우저 개발자 도구로 네트워크 요청 확인

---

## 9. API 문서

### 9.1 소셜 로그인 시작

**Endpoint**: `GET /api/v1/social/{provider}/`

**Parameters**:
- `provider`: google, github, naver, kakao
- `redirect_uri` (optional): 프론트엔드 URL

**Response**: 302 Redirect to OAuth provider

### 9.2 소셜 로그인 콜백

**Endpoint**: `GET /api/v1/social/callback/{provider}/`

**Parameters**:
- `provider`: google, github, naver, kakao
- `code`: OAuth authorization code
- `state`: CSRF protection token
- `frontend`: 프론트엔드 URL

**Response**: 302 Redirect to frontend with tokens

**Redirect URL Format**:
```
{frontend_url}/social-callback?access_token={jwt_access}&refresh_token={jwt_refresh}
```

---

## 10. 참고 자료

- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Naver Login API](https://developers.naver.com/docs/login/overview/)
- [Kakao Login](https://developers.kakao.com/docs/latest/ko/kakaologin/common)

---

## 문제 발생 시

1. Django 로그 확인: `python manage.py runserver`의 콘솔 출력
2. React 콘솔 확인: 브라우저 개발자 도구 > Console
3. Network 탭에서 API 요청/응답 확인
4. GitHub Issues: https://github.com/your-repo/issues
