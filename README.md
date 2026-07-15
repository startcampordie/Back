# LocalHub Backend

## 개발 환경

- Python 3.11
- FastAPI
- SQLite
- SQLAlchemy

---

## 프로젝트 실행 방법

## 최초 실행 순서

1. 가상환경 생성
2. 패키지 설치
3. 서버 실행 (`python -m uvicorn app.main:app --reload`)
4. 초기 데이터 적재 (`python -m scripts.seed_data`)

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd pythonProject1
```

### 2. 가상환경 생성

```bash
python -m venv .venv
```

### 3. 가상환경 활성화

### Windows (CMD)

```bash
.venv\Scripts\activate
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

---

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

---

### 5. 서버 실행

```bash
python -m uvicorn app.main:app --reload
```

---

## API 확인

Swagger

```
http://127.0.0.1:8000/docs
```

Health Check

```
http://127.0.0.1:8000/health
```

---

## 초기 데이터 적재

JSON 데이터를 SQLite에 적재합니다.

```bash
python -m scripts.seed_data
```

---

## 프로젝트 구조

```
app/
 ├── core
 ├── models
 ├── routers
 ├── schemas
 └── services

data/
scripts/
```