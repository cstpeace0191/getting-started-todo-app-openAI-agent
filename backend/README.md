# Getting Started Todo App - FastAPI Backend

FastAPI 및 Uvicorn 기반의 비동기(Async) Python Todo App 백엔드 서버입니다.  
SQLite 및 PostgreSQL 데이터베이스와의 비동기 연동을 지원하며, React 기반 프론트엔드(`client`) 및 Nginx 리버스 프록시와 완벽하게 연동됩니다.

---

## 🛠️ 기술 스택 (Tech Stack)

- **언어 및 런타임**: Python 3.10+
- **웹 프레임워크**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI 서버**: [Uvicorn](https://www.uvicorn.org/)
- **데이터 검증/직렬화**: [Pydantic v2](https://docs.pydantic.dev/)
- **비동기 DB 클라이언트**: 
  - [aiosqlite](https://github.com/omnilib/aiosqlite) (SQLite)
  - [asyncpg](https://github.com/MagicStack/asyncpg) (PostgreSQL)
- **AI**: [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) (`openai-agents`)
- **테스트 프레임워크**: [pytest](https://docs.pytest.org/), `pytest-asyncio`, `httpx`

---

## 📁 디렉토리 구조 (Project Structure)

```text
backend/
├── src/
│   ├── main.py              # FastAPI 메인 앱 및 라이프사이클(Lifespan) 관리
│   ├── models.py            # Pydantic 데이터 모델 (Item, ItemCreate, Briefing 등)
│   ├── ai/                  # OpenAI Agents SDK 기반 AI 기능
│   │   ├── agent.py         # 공통 실행·옵션·오류 처리
│   │   ├── classifier.py    # 할 일 자동 분류
│   │   └── planner.py       # 일정 브리핑 에이전트 (함수 도구)
│   ├── persistence/         # 비동기 데이터베이스 계층
│   │   ├── __init__.py      # DB 엔진 자동 선택 (SQLite / PostgreSQL)
│   │   ├── sqlite.py        # aiosqlite 기반 SQLite 구현
│   │   └── postgres.py      # asyncpg 기반 PostgreSQL 풀 구현
│   └── routes/              # API 라우터
│       ├── __init__.py
│       ├── greeting.py      # /api/greeting 라우트
│       └── items.py         # /api/items CRUD, 재분류, AI 브리핑 라우트
├── spec/                    # pytest 기반 비동기 단위/통합 테스트
│   ├── ai/
│   ├── persistence/
│   └── routes/
├── Dockerfile               # 컨테이너 빌드 파일
├── main.py                  # 진입점 스크립트
├── pytest.ini               # pytest 설정 파일
├── requirements.txt         # Python 의존성 패키지 목록
└── README.md                # 백엔드 설명 문서
```

---

## 🚀 설치 및 로컬 실행 방법 (Getting Started)

### 0. 사전 작업: `uv` 설치

이 프로젝트는 빠르고 효율적인 Python 패키지 및 가상환경 관리를 위해 [`uv`](https://docs.astral.sh/uv/)를 사용합니다. 각 운영체제(OS) 환경에 맞추어 `uv`를 먼저 설치해 주세요.

#### Windows
Windows에서는 **`winget`**(Windows 패키지 관리자)을 이용하여 간편하게 설치할 수 있습니다:
```cmd
winget install --id=astral-sh.uv -e
```
> **참고**: 설치 완료 후 열려 있는 터미널(PowerShell 또는 CMD)을 다시 시작해야 `uv` 명령어가 환경 변수에 반영됩니다.  
> (winget 미지원 환경일 경우 PowerShell에서 설치: `irm https://astral.sh/uv/install.ps1 | iex`)

#### macOS
Homebrew를 사용하거나 공식 독립 설치 스크립트를 실행합니다:
```bash
# Homebrew 사용 시
brew install uv

# 또는 공식 설치 스크립트 사용 시
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Linux
공식 독립형 설치 스크립트를 실행하여 설치합니다:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 설치 확인
터미널에서 아래 명령어를 실행하여 설치를 확인합니다:
```bash
uv --version
```

---

### 1. 가상환경(venv) 생성 및 활성화

#### Windows (PowerShell)
```powershell
cd backend
uv sync
```

#### Windows (CMD)
```cmd
cd backend
uv venv
.venv\Scripts\activate.bat
```

#### macOS / Linux
```bash
cd backend
uv venv
source .venv/bin/activate
```

---

### 2. 패키지 의존성 설치

```bash
uv pip install -r requirements.txt
```

---

### 3. 패키지 설치후에 추후 다시 backend server 동작시킬려면

이미 가상환경(`.venv`) 생성과 패키지 의존성 설치가 완료된 경우, 매번 새로 가상환경을 만들거나 패키지를 설치할 필요 없이 아래 방법 중 하나로 서버를 다시 실행할 수 있습니다.

#### 방법 A: `uv run`을 이용하여 즉시 실행 (권장)
가상환경을 수동으로 활성화(`activate`)하지 않아도, `uv`가 디렉토리 내 `.venv`를 자동으로 감지하여 실행합니다:

```bash
cd backend

# 방법 1: main.py 실행
uv run main.py

# 방법 2: uvicorn 직접 실행 (코드 변경 시 자동 재시작)
uv run uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload
```

#### 방법 B: 기존 가상환경 활성화 후 실행

1. **`backend` 디렉토리로 이동**:
   ```bash
   cd backend
   ```

2. **가상환경 활성화**:
   - **Windows (Git Bash)**:
     ```bash
     source .venv/Scripts/activate
     ```
     > Git Bash 에서는 역슬래시(`\`)가 이스케이프 문자로 처리되므로 경로를 `/` 로 써야 합니다.
   - **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     source .venv/bin/activate
     ```

3. **서버 실행**:
   ```bash
   python main.py
   # 또는
   uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload
   ``` 

---
### 4. 서버 실행

기본 포트인 **`3000`** 번 포트로 서버가 기동됩니다.

#### 방법 1: `uvicorn` 명령어로 직접 실행 (코드 수정 시 자동 재시작 지원)
```bash
uvicorn src.main:app --host 0.0.0.0 --port 3000 --reload
```

#### 방법 2: `main.py` 실행
```bash
python main.py
```

- 서버 주소: `http://localhost:3000`
- **Swagger UI (대화형 API 문서)**: `http://localhost:3000/docs`
- **Redoc 문서**: `http://localhost:3000/redoc`

---

## 🗄️ 데이터베이스 설정 (Database Configuration)

환경변수를 통해 데이터베이스를 유연하게 설정할 수 있습니다.

### SQLite (기본값)
`POSTGRES_HOST` 환경변수가 설정되지 않은 경우 기본적으로 SQLite를 사용합니다.

- `SQLITE_DB_LOCATION`: SQLite 데이터베이스 파일 경로 (기본값: `/etc/todos/todo.db` 또는 로컬 지정 경로)
- 로컬 경로 지정 예시:
  ```powershell
  # Windows PowerShell
  $env:SQLITE_DB_LOCATION = "./todo.db"
  python main.py
  ```

### PostgreSQL
`POSTGRES_HOST` 또는 `POSTGRES_HOST_FILE` 환경변수가 설정되어 있으면 자동으로 PostgreSQL 비동기 모드로 전환됩니다.

| 환경변수명 | Docker Secret 파일 변수명 | 기본값 | 설명 |
| :--- | :--- | :--- | :--- |
| `POSTGRES_HOST` | `POSTGRES_HOST_FILE` | `localhost` | PostgreSQL 서버 호스트명 또는 IP |
| `POSTGRES_USER` | `POSTGRES_USER_FILE` | `postgres` | PostgreSQL 사용자명 |
| `POSTGRES_PASSWORD` | `POSTGRES_PASSWORD_FILE` | `""` | PostgreSQL 비밀번호 |
| `POSTGRES_DB` | `POSTGRES_DB_FILE` | `todos` | 데이터베이스 이름 |
| `POSTGRES_PORT` | - | `5432` | 포트 |

시작 시 `pg_trgm` 확장과 `todo_items.name` GIN 인덱스를 만들어 검색 속도를 높입니다 (권한이 없으면 인덱스 없이 검색만 동작).

---

## 📡 API 엔드포인트 명세 (API Specification)

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/greeting` | 인사말 조회 | - | `{"greeting": "Hello world!"}` |
| `GET` | `/api/items` | Todo 목록 조회. 선택 파라미터: `q`(이름 부분 일치, 대소문자 무시), `category`(`study`/`work`/`personal`), `registered`(`true`=등록됨, `false`=작업 중) | - |
| `GET` | `/api/categories?registered=true` | 분류별 항목 개수 분류별 개수 (분류 선택 목록용) | - | `[{"category": "work", "count": 2}]` |
| `GET` | `/api/items` (응답) | 응답 형식 | - | `[{"id": "...", "name": "...", "completed": false, "category": "study", "priority": "high", "registered": false, "due_date": "2026-11-25", "due_time": "09:00"}, ...]` |
| `GET` | `/api/schedule?date=YYYY-MM-DD` | 오늘 일정: `date` 의 항목 + 기한이 지난 미완료 항목 (등록 여부 무관, 날짜·시간순). `date` 생략 시 서버 오늘 | - | 항목 배열 (잘못된 날짜: 422) |
| `GET` | `/api/schedule?start=YYYY-MM-DD&end=YYYY-MM-DD` | 기간 일정: 기한이 `start`~`end`(양끝 포함) 사이인 항목. 주간·월간·연간·캘린더 검색에 사용. `start`/`end` 는 함께 줘야 하고 `date` 와 같이 쓸 수 없음 | - | 항목 배열 (`start` > `end`, 한쪽만 지정, 잘못된 날짜: 422) |
| `POST` | `/api/items` | 새 Todo 항목 추가 (AI 자동 분류 + 일정 추출) | `{"name": "할 일 내용", "today": "YYYY-MM-DD", "due_date": "YYYY-MM-DD", "due_time": "HH:MM"}` (`name` 외 선택. `due_*` 를 주면 AI 추출값보다 우선) | `{"id": "UUID", "name": "할 일 내용", "completed": false, "category": "...", "priority": "..."}` |
| `PUT` | `/api/items/{id}` | Todo 항목 수정 (분류 수동 변경 가능) | `{"name": "수정 이름", "completed": true, "category": "work", "priority": "low"}` (모두 선택). `{"registered": true}` 로 **등록(Register)**, `due_date`/`due_time` 으로 일정 변경 (`""` 이면 삭제, 날짜 삭제 시 시간도 삭제) | 수정된 항목 |
| `POST` | `/api/items/{id}/classify?today=YYYY-MM-DD` | AI 로 다시 분류 (문장에서 일정도 다시 추출, 못 찾으면 기존 일정 유지) | - | 분류된 항목 (AI 꺼짐: 503, 실패: 502) |
| `POST` | `/api/ai/briefing` | AI 일정 브리핑 (에이전트가 DB 를 조회) | `{"today": "YYYY-MM-DD"}` (선택) | `{"summary": "...", "focus": [{"item_id", "name", "reason"}], "warnings": [], "tips": []}` (AI 꺼짐: 503, 실패: 502) |
| `GET` | `/api/ai/status` | AI 기능 사용 가능 여부 | - | `{"enabled": true}` |
| `DELETE` | `/api/items/{id}` | Todo 항목 삭제 | - | `HTTP 200 OK` |

---

## 🤖 AI 기능 (OpenAI Agents SDK)

AI 기능은 모두 **OpenAI Agents SDK**(`openai-agents`)의 `Agent` 로 동작합니다. 공통 실행 코드는 `src/ai/agent.py` (`Agent` 생성 + `Runner.run` 실행, `output_type` 으로 구조화 출력)에 있고, 모델은 `AI_MODEL` 로 바꿀 수 있습니다(생략하면 `gpt-5.6-luna`). AI 전체를 끄려면 `AI_ENABLED=false` (구 이름 `AI_CLASSIFY_ENABLED` 도 인정).

### 1) 자동 분류 — `src/ai/classifier.py`
할 일을 추가하면 도구 없는 단일 턴 `Agent` 가 카테고리·우선순위·일정을 구조화 출력으로 돌려줍니다.

| 필드 | 값 | 화면 표시 |
| :--- | :--- | :--- |
| `category` | `study` / `work` / `personal` | 학업 / 업무 / 개인 |
| `priority` | `high` / `medium` / `low` | 높음 / 보통 / 낮음 |

- **구조화 출력**: `Agent(output_type=Classification)` 으로 OpenAI Structured Outputs(strict JSON 스키마)를 강제하고, `result.final_output` 을 Pydantic 모델로 받습니다.
- **비용·지연 절감**: 단순 분류이므로 가벼운 기본 모델(`gpt-5.6-luna`, SDK 가 GPT-5 계열 기본 설정 `reasoning.effort="none"` 을 적용)을 사용합니다. 별도 하위 프로세스 없이 서버 프로세스 안에서 모델 API 를 직접 호출합니다.
- **격리**: 에이전트에는 코드에서 넘겨 준 함수 도구만 노출되고(분류기는 `tools=[]`), `Runner.run` 은 호출마다 새 대화로 시작하므로 요청 간 내용이 섞이지 않습니다. `max_turns=8` 로 도구 호출 루프에 상한을 둡니다.
- **장애 격리**: 키가 없거나 API 호출이 실패하면 분류만 비어 있는 상태(`null`)로 저장되고, CRUD 는 그대로 동작합니다.
- **일정 추출**: 클라이언트가 보낸 오늘 날짜(`today`)를 기준으로 "내일 오전 9시" 같은 표현을 `due_date`/`due_time` 으로 변환합니다. AI 가 돌려준 값은 형식·존재 여부를 검증하고 틀리면 버립니다.
- **DB 마이그레이션**: 기존 `todo_items` 테이블에 `category`, `priority` 컬럼이 없으면 시작 시 자동으로 추가합니다 (SQLite/PostgreSQL).

### API 키 설정

| 환경 변수 | 설명 |
| :--- | :--- |
| `OPENAI_API_KEY` | OpenAI API 키 ([platform.openai.com](https://platform.openai.com/api-keys)) |
| `OPENAI_API_KEY_FILE` | 키가 들어 있는 파일 경로 (Docker/K8s Secret 마운트용, 우선 적용) |
| `AI_MODEL` | 사용할 모델 (기본 `gpt-5.6-luna`) |
| `AI_ENABLED` | `false` 로 두면 키가 있어도 AI 기능 전체 비활성화 (구 이름 `AI_CLASSIFY_ENABLED` 도 인정) |
| `OPENAI_BASE_URL` | (선택) OpenAI 호환 엔드포인트 주소 |
| `OPENAI_AGENTS_DISABLE_TRACING` | (선택) `1` 이면 OpenAI 대시보드(Traces)로의 실행 기록 전송을 끔 |

```powershell
# 로컬 실행 (PowerShell)
$env:OPENAI_API_KEY = "<your-key>"
uv run python main.py
```

Docker Compose 는 호스트의 `OPENAI_API_KEY` 와 `AI_MODEL` 을 백엔드 컨테이너로 전달합니다. Kubernetes(kind/GKE)에서는 아래처럼 Secret 을 만들면 `todo-backend` Deployment 가 읽어 갑니다 (Secret 이 없어도 Pod 는 정상 기동).

```bash
kubectl create secret generic todo-ai-secret --from-literal=OPENAI_API_KEY=<your-key>
kubectl rollout restart deployment/todo-backend
```

> 테스트(`spec/ai`, `spec/routes/test_classifyItem.py`)는 Agents SDK 의 `Runner` 를 mock 으로 대체하므로 실제 API 를 호출하지 않고 비용도 들지 않습니다.

### 2) 일정 브리핑 에이전트 (신규) — `src/ai/planner.py`
`POST /api/ai/briefing` (`{"today": "YYYY-MM-DD"}`, 선택). 에이전트가 함수 도구(앱 내 비동기 함수를 `function_tool` 로 감싸 `FunctionTool` 로 등록)
`get_schedule` / `search_items` / `get_category_counts` 로 **할 일 DB 를 직접 조회**한 뒤, 오늘 먼저 할 일(`focus`),
주의사항(`warnings`), 조언(`tips`)을 담은 브리핑을 돌려줍니다. 도구는 읽기 전용이며 Bash/파일 같은 다른 도구는 쓸 수 없습니다.
AI 꺼짐: 503, 실패: 502. 화면에서는 날짜별 검색의 **AI 브리핑** 버튼으로 호출합니다.

---

## 🧪 테스트 실행 (Running Tests)

`pytest`를 사용하여 영속성 계층, AI 모듈 및 API 라우트에 대한 비동기 단위 테스트를 실행합니다.

```bash
# 전체 테스트 실행
pytest

# 상세 출력 모드로 실행
pytest -v
```

---

## 🐳 Docker 컨테이너 빌드 및 실행

```bash
# Docker 이미지 빌드
docker build -t todo-backend-fastapi .

# SQLite 모드로 컨테이너 실행
docker run -dp 3000:3000 todo-backend-fastapi
```
