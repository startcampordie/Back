# Honamdo Backend

광주·전라권의 관광지, 문화시설, 음식점, 축제 정보를 제공하고 커뮤니티와 AI 추천 챗봇 기능을 지원하는 LocalHub의 FastAPI 백엔드입니다.

## 배포 주소

| 구분 | 주소 | 배포 환경 |
| --- | --- | --- |
| 프론트엔드 | [https://ronamdo.netlify.app/](https://ronamdo.netlify.app/) | Netlify |
| 백엔드 API Base URL | [https://back-vjf9.onrender.com/api](https://back-vjf9.onrender.com/api) | Render |
| Swagger API 문서 | [https://back-vjf9.onrender.com/docs](https://back-vjf9.onrender.com/docs) | Render |
| Health Check | [https://back-vjf9.onrender.com/health](https://back-vjf9.onrender.com/health) | Render |

> `/api`는 실제 API 엔드포인트의 공통 prefix입니다. 루트, Swagger, Health Check 주소에는 `/api`가 붙지 않습니다.

## 주요 기능

- 홈: 카테고리별 랜덤 지역 콘텐츠와 최신·인기 게시글 제공
- 지역 정보: 관광지, 문화시설, 음식점, 축제·행사 조회
- 필터 및 검색: 카테고리, 다중 태그, 키워드, 지역 조건 검색과 페이지네이션
- 통합 검색: 지역 콘텐츠와 커뮤니티 게시글을 한 번에 검색
- 커뮤니티: 게시글 작성, 목록·상세 조회, 수정, 삭제, 비밀번호 확인
- AI 챗봇: 익명 채팅 세션을 만들고 OpenAI 기반 지역 콘텐츠 추천 제공
- 데이터 관리: JSON 지역 데이터와 테스트 게시글을 SQLite에 적재

## 기술 스택

- Python 3.11
- FastAPI / Uvicorn
- SQLAlchemy
- SQLite
- Pydantic
- OpenAI API

## 프로젝트 구조

```text
Back/
├── app/
│   ├── core/       # 환경 설정 및 데이터베이스 연결
│   ├── models/     # SQLAlchemy 모델
│   ├── routers/    # FastAPI API 라우터
│   ├── schemas/    # 요청·응답 Pydantic 스키마
│   ├── services/   # 검색, 챗봇, OpenAI 비즈니스 로직
│   └── main.py     # FastAPI 애플리케이션 진입점
├── data/           # 광주·전라권 지역 정보 JSON
├── scripts/        # 초기 데이터 적재 및 보정 스크립트
├── localhub.db     # 로컬 SQLite 데이터베이스
└── requirements.txt
```

## 로컬 실행 방법

모든 명령은 `Back` 디렉터리에서 실행합니다.

### 1. 가상환경 생성 및 활성화

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 2. 패키지 설치

```bash
python -m pip install -r requirements.txt
```

### 3. 환경 변수 설정

`Back/.env` 파일을 만들고 아래 값을 설정합니다.

```dotenv
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-5-mini
```

| 변수 | 필수 여부 | 설명 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 챗봇 AI 응답 사용 시 필수 | OpenAI API 키. 저장소에 커밋하지 않습니다. |
| `OPENAI_MODEL` | 선택 | 사용할 OpenAI 모델. 미설정 시 `gpt-5-mini`를 사용합니다. |

OpenAI 설정이 없거나 호출에 실패하면 챗봇은 DB 검색 결과를 기반으로 최대 5건의 대체 응답을 반환합니다.

### 4. 서버 실행

```bash
python -m uvicorn app.main:app --reload
```

서버가 시작되면 SQLAlchemy 모델을 기준으로 SQLite 테이블이 자동 생성됩니다.

- 로컬 API Base URL: `http://127.0.0.1:8000/api`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health Check: `http://127.0.0.1:8000/health`

### 5. 초기 데이터 적재

서버를 한 번 실행해 테이블을 생성한 뒤, 가상환경이 활성화된 별도 터미널에서 필요한 스크립트를 실행합니다.

```bash
# 광주·전라권 관광지, 문화시설, 음식점, 축제 데이터 적재
python -m scripts.seed_data

# 주소에서 시·군·구 정보를 추출해 보정
python -m scripts.update_district

# 테스트용 커뮤니티 게시글 100개 생성
python -m scripts.seed_posts
```

> `seed_data`는 기존 지역 콘텐츠와 태그를 삭제한 후 다시 적재합니다. `seed_posts`는 게시글이 이미 하나라도 있으면 데이터를 추가하지 않습니다.

## API 요약

### 공통 및 홈

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `GET` | `/` | API 기본 응답 |
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/api/home` | 카테고리별 추천 콘텐츠와 최신·인기 게시글 조회 |

### 지역 콘텐츠 및 통합 검색

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `GET` | `/api/contents` | 카테고리·태그·키워드 필터와 페이지네이션 조회 |
| `GET` | `/api/search` | 지역 콘텐츠 및 게시글 통합 검색 |

`/api/contents`의 카테고리는 `ALL`, `ATTRACTION`, `CULTURE`, `RESTAURANT`, `FESTIVAL`을 지원합니다. 다중 태그는 `tags=가족||tags=사진`처럼 반복해서 전달합니다.

### 커뮤니티 게시글

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `POST` | `/api/posts` | 게시글 작성 |
| `GET` | `/api/posts` | 게시글 검색, 정렬 및 페이지 조회 |
| `GET` | `/api/posts/{post_id}` | 게시글 상세 조회 및 조회수 증가 |
| `POST` | `/api/posts/{post_id}/verify-password` | 수정·삭제 전 비밀번호 확인 |
| `PUT` | `/api/posts/{post_id}` | 비밀번호 확인 후 게시글 수정 |
| `DELETE` | `/api/posts/{post_id}` | 비밀번호 확인 후 게시글 삭제 |

게시글 목록은 제목·내용 검색, 최신순·조회수순 정렬을 지원하며 한 페이지당 10개를 반환합니다.

### AI 챗봇

| Method | Endpoint | 설명 |
| --- | --- | --- |
| `POST` | `/api/chat/sessions` | 익명 채팅 세션 생성 |
| `GET` | `/api/chat/sessions/{session_id}/messages` | 세션별 채팅 기록 조회 |
| `POST` | `/api/chat` | 관광지·문화시설·음식점·축제 추천 질문 전송 |

채팅 세션은 마지막 이용 시점부터 7일간 유효합니다. 질문의 `intent` 값은 `attraction`, `culture`, `restaurant`, `festival` 중 하나이며 질문 길이는 2~100자입니다. 서버는 DB 후보 최대 10건 중 AI가 선택한 최대 5건을 반환합니다.

채팅 요청 예시:

```json
{
  "session_id": "POST /api/chat/sessions에서 발급받은 UUID",
  "intent": "restaurant",
  "message": "광주 북구 맛집 알려줘"
}
```

상세 요청·응답 스키마와 직접 실행 가능한 API 테스트는 Swagger 문서에서 확인할 수 있습니다.

## 배포 설정

### Render 백엔드

Render Web Service에서 저장소 루트가 전체 프로젝트라면 Root Directory를 `Back`으로 지정합니다.

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- 환경 변수: `OPENAI_API_KEY`, `OPENAI_MODEL`

현재 데이터베이스는 `localhub.db` SQLite 파일을 사용합니다. Render의 기본 파일 시스템에 생성된 런타임 데이터는 재배포나 인스턴스 교체 시 유지되지 않을 수 있으므로, 운영 데이터 보존이 필요하면 Persistent Disk 또는 외부 관리형 데이터베이스를 사용해야 합니다.

### Netlify 프론트엔드

Netlify의 프론트엔드 환경 변수는 다음과 같이 설정합니다.

```dotenv
VITE_API_BASE_URL=https://back-vjf9.onrender.com/api
VITE_USE_MOCK=false
```

## CORS 설정

백엔드는 다음 두 프론트엔드 Origin을 허용해야 합니다.

- 로컬 개발: `http://localhost:5173`
- 운영 배포: `https://ronamdo.netlify.app`

현재 Render 배포 서버는 Netlify Origin을 허용하고 있습니다. 다만 이 저장소의 `app/main.py`에는 로컬 Origin만 직접 지정되어 있으므로, 재배포 전에 `allow_origins` 설정에도 운영 Origin이 포함되어 있는지 확인해야 합니다.

## 참고 사항

- 게시글 비밀번호는 현재 평문으로 SQLite에 저장되므로 실제 운영 서비스에서는 해시 처리가 필요합니다.
- `.env`와 OpenAI API 키는 Git에 커밋하지 않습니다.
- API 오류의 상세 내용은 FastAPI의 `detail` 필드로 반환됩니다.
