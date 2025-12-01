# API 명세서

AI 이미지 커뮤니티 서비스의 전체 API 명세입니다.

---

## 📋 엔드포인트 요약

| 카테고리 | 메서드 | 최종 경로 | 설명 | 인증 |
|----------|--------|-----------|------|------|
| **이미지** | POST | `/api/v1/images/` | 이미지 업로드 | ✅ |
| | GET | `/api/v1/images/{id}` | 이미지 상세 조회 | ❌ |
| | PUT | `/api/v1/images/{id}` | 이미지 수정 | ✅ |
| | DELETE | `/api/v1/images/{id}` | 이미지 삭제 | ✅ |
| **피드** | GET | `/api/v1/images/random` | 랜덤 피드 | ❌ |
| | GET | `/api/v1/images/top-24h` | 24시간 인기 Top 10 | ❌ |
| **좋아요** | POST | `/api/v1/images/{id}/like` | 좋아요 추가 | ✅ |
| | DELETE | `/api/v1/images/{id}/like` | 좋아요 취소 | ✅ |
| **토너먼트** | GET | `/api/v1/tournaments/match` | 매치업 가져오기 | ✅ |
| | POST | `/api/v1/tournaments/vote` | 투표하기 | ✅ |

---

## 🔐 인증 방식

### JWT Bearer Token
모든 보호된 엔드포인트는 Authorization 헤더에 Bearer 토큰을 요구합니다.

```http
Authorization: Bearer <jwt_token>
```

### 토큰 구조 (RS256)
```json
{
  "user_id": 123,
  "username": "user@example.com",
  "exp": 1699999999,
  "iat": 1699900000
}
```

---

## 📌 Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://api.example.com/api/v1
```

> **Note**: 아래 모든 엔드포인트는 Base URL 기준 상대 경로입니다.  
> 예: `POST /images/` → 실제 요청은 `POST http://localhost:8000/api/v1/images/`

---

## 🖼 이미지 API

### 1. 이미지 업로드 (Create)

```http
POST /images/
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

> **최종 경로**: `POST /api/v1/images/`

#### 요청 필드

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| file | File | ✅ | 이미지 파일 (jpg, png, gif, webp) |
| prompt | string | ✅ | AI 생성 프롬프트 (1-2000자) |
| model_name | string | ❌ | 사용한 AI 모델명 (최대 100자) |
| is_tournament_opt_in | boolean | ❌ | 토너먼트 참여 여부 (기본: false) |

#### 응답 예시 (201 Created)

```json
{
  "id": 1,
  "user_id": 123,
  "image_url": "/uploads/images/abc123.png",
  "prompt": "A futuristic city at sunset...",
  "model_name": "DALL-E 3",
  "is_tournament_opt_in": true,
  "created_at": "2024-01-15T10:30:00Z",
  "like_count": 0,
  "tournament_win_count": 0
}
```

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 400 | 잘못된 파일 형식 또는 크기 초과 |
| 401 | 인증 토큰 없음 또는 만료 |
| 422 | 필드 검증 실패 |

---

### 2. 이미지 상세 조회 (Read)

```http
GET /images/{image_id}
```

> **최종 경로**: `GET /api/v1/images/{image_id}`

#### 경로 파라미터

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| image_id | integer | 이미지 ID |

#### 응답 예시 (200 OK)

```json
{
  "id": 1,
  "user_id": 123,
  "image_url": "/uploads/images/abc123.png",
  "prompt": "A futuristic city at sunset...",
  "model_name": "DALL-E 3",
  "is_tournament_opt_in": true,
  "created_at": "2024-01-15T10:30:00Z",
  "like_count": 42,
  "tournament_win_count": 15,
  "is_liked_by_me": true  // 인증된 경우에만 포함
}
```

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 404 | 이미지를 찾을 수 없음 |

---

### 3. 이미지 수정 (Update)

```http
PUT /images/{image_id}
Content-Type: application/json
Authorization: Bearer <token>
```

> **최종 경로**: `PUT /api/v1/images/{image_id}`

#### 요청 본문

```json
{
  "prompt": "Updated prompt text...",
  "model_name": "Midjourney v6",
  "is_tournament_opt_in": false
}
```

#### 응답 예시 (200 OK)

```json
{
  "id": 1,
  "user_id": 123,
  "image_url": "/uploads/images/abc123.png",
  "prompt": "Updated prompt text...",
  "model_name": "Midjourney v6",
  "is_tournament_opt_in": false,
  "created_at": "2024-01-15T10:30:00Z",
  "like_count": 42,
  "tournament_win_count": 15
}
```

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 401 | 인증 필요 |
| 403 | 본인 이미지만 수정 가능 |
| 404 | 이미지를 찾을 수 없음 |

---

### 4. 이미지 삭제 (Delete)

```http
DELETE /images/{image_id}
Authorization: Bearer <token>
```

> **최종 경로**: `DELETE /api/v1/images/{image_id}`

#### 응답 (204 No Content)

본문 없음

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 401 | 인증 필요 |
| 403 | 본인 이미지만 삭제 가능 |
| 404 | 이미지를 찾을 수 없음 |

---

## 🎲 피드 API

### 5. 랜덤 이미지 피드

```http
GET /images/random?limit=20
```

> **최종 경로**: `GET /api/v1/images/random?limit=20`

#### 쿼리 파라미터

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| limit | integer | 20 | 반환할 이미지 수 (1-50) |

#### 응답 예시 (200 OK)

```json
{
  "items": [
    {
      "id": 42,
      "user_id": 101,
      "image_url": "/uploads/images/xyz789.png",
      "prompt": "Abstract geometric patterns...",
      "model_name": "Stable Diffusion XL",
      "is_tournament_opt_in": true,
      "created_at": "2024-01-14T15:20:00Z",
      "like_count": 28,
      "tournament_win_count": 8
    }
    // ... 더 많은 이미지
  ],
  "count": 20
}
```

---

### 6. 인기 이미지 Top 10 (24시간)

```http
GET /images/top-24h
```

> **최종 경로**: `GET /api/v1/images/top-24h`

#### 응답 예시 (200 OK)

```json
{
  "items": [
    {
      "id": 15,
      "user_id": 55,
      "image_url": "/uploads/images/top1.png",
      "prompt": "Epic dragon battle...",
      "model_name": "DALL-E 3",
      "is_tournament_opt_in": true,
      "created_at": "2024-01-15T08:00:00Z",
      "like_count": 156,
      "tournament_win_count": 89,
      "total_score": 245,
      "rank": 1
    }
    // ... 9개 더
  ],
  "period": "24h",
  "generated_at": "2024-01-15T12:00:00Z"
}
```

---

## ❤️ 좋아요 API

### 7. 좋아요 추가

```http
POST /images/{image_id}/like
Authorization: Bearer <token>
```

> **최종 경로**: `POST /api/v1/images/{image_id}/like`

#### 응답 예시 (201 Created)

```json
{
  "message": "좋아요가 추가되었습니다.",
  "image_id": 1,
  "like_count": 43
}
```

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 401 | 인증 필요 |
| 404 | 이미지를 찾을 수 없음 |
| 409 | 이미 좋아요한 이미지 |

---

### 8. 좋아요 취소

```http
DELETE /images/{image_id}/like
Authorization: Bearer <token>
```

> **최종 경로**: `DELETE /api/v1/images/{image_id}/like`

#### 응답 예시 (200 OK)

```json
{
  "message": "좋아요가 취소되었습니다.",
  "image_id": 1,
  "like_count": 42
}
```

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 401 | 인증 필요 |
| 404 | 좋아요 기록을 찾을 수 없음 |

---

## 🏆 토너먼트 API

### 9. 토너먼트 매치업 가져오기

```http
GET /tournaments/match
Authorization: Bearer <token>
```

> **최종 경로**: `GET /api/v1/tournaments/match`

#### 응답 예시 (200 OK)

```json
{
  "match_id": "abc123-uuid",
  "images": [
    {
      "id": 15,
      "image_url": "/uploads/images/img1.png",
      "prompt": "First image prompt...",
      "like_count": 42,
      "tournament_win_count": 12
    },
    {
      "id": 28,
      "image_url": "/uploads/images/img2.png",
      "prompt": "Second image prompt...",
      "like_count": 38,
      "tournament_win_count": 15
    }
  ],
  "expires_at": "2024-01-15T12:05:00Z"
}
```

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 401 | 인증 필요 |
| 404 | 토너먼트 참여 이미지가 2개 미만 |

---

### 10. 토너먼트 투표

```http
POST /tournaments/vote
Content-Type: application/json
Authorization: Bearer <token>
```

> **최종 경로**: `POST /api/v1/tournaments/vote`

#### 요청 본문

```json
{
  "winner_image_id": 15,
  "loser_image_id": 28
}
```

#### 응답 예시 (201 Created)

```json
{
  "message": "투표가 완료되었습니다.",
  "vote_id": 789,
  "winner": {
    "id": 15,
    "new_win_count": 13
  },
  "loser": {
    "id": 28,
    "loss_count": 5
  }
}
```

#### 에러 응답

| 코드 | 설명 |
|------|------|
| 400 | winner_id와 loser_id가 동일 |
| 401 | 인증 필요 |
| 404 | 이미지를 찾을 수 없음 |

---

## 📄 공통 응답 스키마

### 에러 응답 형식

```json
{
  "detail": "에러 메시지",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

### 페이지네이션 응답 형식

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

---

## 🔒 보안 헤더

모든 응답에 포함되는 보안 헤더:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## 📊 Rate Limiting

| 엔드포인트 | 제한 |
|------------|------|
| 이미지 업로드 | 10회/분 |
| 좋아요 | 60회/분 |
| 토너먼트 투표 | 30회/분 |
| 조회 | 100회/분 |

Rate Limit 초과 시 응답:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

```json
{
  "detail": "요청 한도를 초과했습니다. 60초 후 다시 시도해주세요.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```