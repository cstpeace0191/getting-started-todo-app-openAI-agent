<div style="text-align:center; margin: auto 0 4em 0" align="center">
<img src="https://repo.katenary.io/Katenary/katenary/raw/branch/master/doc/docs/statics/logo-vertical.svg" alt="Katenary Logo" style="max-width: 90%" align="center"/>
</div>

<div style="text-align:center; margin: auto 0 4em 0" align="center">

[![Documentation Status](https://readthedocs.org/projects/katenary/badge/?version=latest)](https://katenary.readthedocs.io/latest/?badge=latest)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=katenary_katenary&metric=coverage)](https://sonarcloud.io/summary/new_code?id=katenary_katenary)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=katenary_katenary&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=katenary_katenary)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=katenary_katenary&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=katenary_katenary)

</div>

<div style="text-align:center; margin: auto 0 4em 0" align="center">
<h3>🚀 Katenary로 생산성을 극대화하세요! 🚀</h3>
</div>

수동 변환 작업에 지치셨나요? Katenary는 "`compose`" 파일의 라벨을 활용하여 손쉽게 완전한 Helm 차트를 생성하므로, 사용자의 시간과 에너지를 절약해 줍니다.

🛠️ 단순한 자동화 CLI: Katenary는 번거로운 반복 작업을 대신 처리하며, 원활한 서비스 바인딩과 Helm 차트 생성에 필요한 모든 것을 만들어냅니다.

💡 손쉬운 효율성: 상세한 설정이 필요한 경우에만 라벨을 추가하면 됩니다.
그런 다음 `katenary convert`를 실행하면 마법 같은 일이 일어납니다.

---

## 무엇인가요? (What is Katenary?)

Katenary는 `compose`(`docker compose`, `podman compose`, `nerdctl compose` 등) 파일을 Kubernetes용으로 작동하는 Helm 차트로 변환하도록 돕는 도구입니다.

현재 이 프로젝트는 [Klee Group](https://www.kleegroup.com)과의 협업을 통해 부분적으로 개발되고 있습니다. Katenary는 **앞으로도 오픈 소스이자 자유(free as in freedom) 프로젝트로 유지될 것**입니다. 커뮤니티와 공유하는 것이 프로젝트를 더욱 발전시키는 최선의 방법이라고 확신하기 때문입니다.

메인 개발자는 [Patrice FERLET](https://repo.katenary.io/metal3d)입니다.

---

## 📌 현재 프로젝트(`getting-started-todo-app-openAI-agent`)에서의 적용 및 구성

본 프로젝트에서는 환경별 Docker Compose 파일을 쿠버네티스 표준 Helm Chart로 자동 변환하고 배포하기 위해 Katenary를 사용합니다.

### 환경별 프로젝트 파일 및 차트 매핑 구조

| 환경 (Environment) | 소스 Compose 파일 | 생성된 Helm Chart 경로 | 대상 클러스터 및 컨테이너 이미지 | 상세 배포 가이드 문서 |
|---|---|---|---|---|
| **로컬 KIND (Local)** | `compose-local_kind.yaml` | `charts/getting-started-todo-app-openai-agent.local_kind` | 로컬 KIND (`todo-backend:prod`) | [README.md](charts/getting-started-todo-app-openai-agent.local_kind/README.md) |
| **GitHub Packages (GHCR)** | `compose-github_kind.yaml` | `charts/getting-started-todo-app-openai-agent.github_kind` | KIND / 원격 GHCR (`ghcr.io/...`) | [README.md](charts/getting-started-todo-app-openai-agent.github_kind/README.md) |
| **GCP Artifact Registry / GKE** | `compose-gcp_gke.yaml` | `charts/getting-started-todo-app-openai-agent.gcp_gke` | GKE / GCP Artifact Registry (`asia-northeast3-docker.pkg.dev/...`) | [README.md](charts/getting-started-todo-app-openai-agent.gcp_gke/README.md) |

### 프로젝트 내 Katenary 변환 명령어

프로젝트 루트 디렉토리에서 대상 환경에 맞추어 변환 명령을 실행합니다:

```bash
# 1. 로컬 KIND용 Helm Chart 생성
katenary convert -c compose-local_kind.yaml -o charts/getting-started-todo-app-openai-agent.local_kind -a 1.0.0 -v 0.1.0 -f

# 2. GitHub Packages (GHCR) 원격 이미지용 Helm Chart 생성
katenary convert -c compose-github_kind.yaml -o charts/getting-started-todo-app-openai-agent.github_kind -a 1.0.0 -v 0.1.0 -f

# 3. GCP Artifact Registry / GKE용 Helm Chart 생성
katenary convert -c compose-gcp_gke.yaml -o charts/getting-started-todo-app-openai-agent.gcp_gke -a 1.0.0 -v 0.1.0 -f
```

- **옵션 설명**:
  - `-c <file>`: 변환할 대상 Docker Compose 소스 파일 지정
  - `-o <dir>`: 생성될 Helm Chart 출력 디렉터리 경로 지정
  - `-a 1.0.0`: `Chart.yaml` 내 `appVersion` (애플리케이션 릴리스 버전)
  - `-v 0.1.0`: `Chart.yaml` 내 `version` (Helm 차트 자체 버전)
  - `-f`: 기존 출력 디렉터리가 있을 경우 확인 질문 없이 강제 덮어쓰기

### 실제 프로젝트 Compose 설정 예시 (`compose-local_kind.yaml`)

다음은 본 프로젝트에서 실제 사용되는 Compose 설정과 Katenary 라벨 적용 내역입니다:

```yaml
services:
  # 1) 로컬 프록시 (Traefik): 쿠버네티스 차트 생성 제외
  proxy:
    image: traefik:v3.6
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - 80:80
      - 443:443
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    labels:
      katenary.v3/ignore: "true"   # Katenary 변환 시 해당 서비스를 완전히 제외함

  # 2) 백엔드 프로덕션 서비스: Express API + React 정적 번들
  backend:
    image: todo-backend:prod
    build:
      context: ./
      target: final                # Dockerfile 멀티스테이지 최종 프로덕션 빌드 단계
    ports:
      - 3000:3000                  # Katenary가 쿠버네티스 ClusterIP Service를 자동 생성하는 기준
    expose:
      - 3000
    environment:
      MYSQL_HOST: mysql
      MYSQL_USER: root
      MYSQL_PASSWORD: secret
      MYSQL_DB: todos    
    depends_on:
      mysql:
        condition: service_healthy # Katenary가 wait-for-mysql InitContainer를 자동 생성함
    labels:
      # [쿠버네티스 서비스 DNS 동적 바인딩]
      # Helm 릴리스명에 따라 달라지는 MySQL 서비스명을 동적으로 참조하도록 매핑
      katenary.v3/map-env: |-
        MYSQL_HOST: '{{ include "__APP__.fullname" . }}-mysql'

  # 3) MySQL 데이터베이스 서비스
  mysql:
    image: mysql:9.3
    ports:
      - 3306:3306
    expose:
      - 3306
    volumes:
      - todo-mysql-data:/var/lib/mysql # Katenary가 PersistentVolumeClaim(PVC)을 자동 생성함
    environment: 
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: todos
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### 생성되는 Helm Chart 디렉터리 구조

로컬 KIND 차트(`charts/getting-started-todo-app-openai-agent.local_kind/`) 기준으로 생성되는 실제 구조입니다:

```text
charts/getting-started-todo-app-openai-agent.local_kind/
├── Chart.yaml              # 차트 메타데이터 (name: getting-started-todo-app-openai-agent, version: 0.1.0, appVersion: 1.0.0)
├── README-local_kind.md    # 로컬 KIND 클러스터 배포 안내 문서
├── values.yaml             # 서비스별 기본 구성 값 (레플리카, 이미지 태그, 리소스, 영구 볼륨 등)
└── templates/              # 렌더링된 쿠버네티스 리소스 매니페스트 템플릿
    ├── _helpers.tpl        # 이름 및 라벨 공통 네이밍 헬퍼 템플릿
    ├── backend/            # Express + Frontend 번들 서비스 매니페스트
    │   ├── configmap.yaml
    │   ├── deployment.yaml
    │   └── service.yaml
    └── mysql/              # MySQL 데이터베이스 매니페스트
        ├── configmap.yaml
        ├── deployment.yaml
        ├── service.yaml
        └── todo_mysql_data.volumeclaim.yaml
```

---

## 설치 (Installation)

### 현재 프로젝트 워크스페이스에서 바로 실행 (Windows)

본 프로젝트의 루트 디렉터리에 실행 가능한 단일 바이너리인 `katenary.exe`가 이미 포함되어 있습니다!

PowerShell에서 즉시 실행할 수 있습니다:
```powershell
.\katenary.exe version
```

현재 터미널 세션의 환경 변수 `Path`에 추가하여 명령어처럼 사용하려면:
```powershell
$env:Path += ";$pwd"
katenary version
```

### 저장소 패키지 및 Windows 설치 프로그램 (공식 배포본)

Linux 패키지 저장소와 Windows용 설치 프로그램은 [패키지 페이지](https://repo.katenary.io/Katenary/katenary/packages)에서 확인할 수 있습니다.

> Fedora >= 42 사용자를 위한 참고 사항: 저장소 안내가 최신 상태가 아닐 수 있으므로 아래 명령을 사용하세요:
>
> ```bash
> dnf config-manager addrepo \
>   --from-repofile https://repo.katenary.io/Katenary/katenary/fedora/katenary.repo
> dnf install katenary
> ```

- **Windows 사용자**: "generic" 패키지 페이지에서 `setup.exe` 파일을 다운로드하여 설치할 수 있습니다.
- **macOS 사용자**: "`darwin`" 바이너리를 사용하세요. (실험적 패키지 준비 중)
- **FreeBSD 사용자**: "generic" 패키지 페이지에서 "`freebsd`" 패키지를 사용하세요.

### 바이너리 설치

[릴리스(Release)](https://repo.katenary.io/Katenary/katenary/releases) 섹션에서 바이너리를 다운로드할 수 있습니다. 바이너리를 복사한 후 이름을 `katenary`로 변경하여 `PATH` 경로에 위치시키면 됩니다.

Linux에서는 저장소의 `install.sh` 스크립트를 사용하여 `$HOME/.local/bin`에 바로 설치할 수 있습니다:

```bash
sh <(curl -sSL https://repo.katenary.io/Katenary/katenary/raw/branch/master/install.sh)
```

Go가 설치되어 있는 경우 다음 명령으로 설치 가능합니다:

```bash
go install -u katenary.io/cmd@latest
# 또는 특정 릴리스 버전 사용
go install -u katenary.io/cmd@v3.0.0
```

### 소스코드에서 직접 빌드하기

`podman` 또는 `docker`가 설치되어 있는 경우:

```bash
make build
make install
```

기본 PREFIX(`~/.local/`)를 사용하여 `bin` 디렉토리에 바이너리를 설치합니다. 설치 경로를 변경하려면:

```bash
sudo make install PREFIX=/usr/local
```

로컬 Go 컴파일러로 직접 빌드할 수도 있습니다:

```bash
make build GO=local

# OS 또는 아키텍처 강제 지정 시
make build GO=local GOOS=linux GOARCH=arm64
```

---

## 셸 자동 완성 팁 (Shell Completion Tips)

사용하는 셸의 프로필 파일(`.bashrc`, `.zshrc` 등)에 자동 완성(completion)을 추가하면 편리하게 사용할 수 있습니다:

```bash
# bash (~/.bashrc)
source <(katenary completion bash)
# 설명문(description)으로 인해 자동완성이 깨질 경우:
source <(katenary completion bash --no-description)

# zsh (~/.zshrc)
source <(katenary completion zsh)

# fish (~/.config/fish/config.fish)
katenary completion fish | source
```

---

## CLI 기본 사용법 (General Usage)

```text
Katenary는 compose 파일을 Helm 차트로 변환하는 도구입니다.

각 [명령어(command)] 및 하위 명령어에는 자세한 정보를 확인할 수 있는 "help" 및 "--help" 플래그가 제공됩니다.

사용법:
  katenary [command]

예시:
  katenary convert -c docker-compose.yml -o ./charts

사용 가능한 명령어:
  completion        자동 완성 스크립트 생성
  convert           docker-compose 파일을 Helm 차트로 변환
  hash-composefiles compose 파일들의 해시값 출력
  help              명령어에 대한 도움말 확인
  help-labels       전체 또는 특정 라벨에 대한 도움말 출력
  schema            katenary 파일의 스키마 출력
  version           Katenary의 버전 번호 출력

플래그:
  -h, --help      katenary 도움말
  -v, --version   katenary 버전 정보

명령어에 대한 자세한 정보를 보려면 "katenary [command] --help"를 실행하세요.
```

---

## Katenary 라벨 레퍼런스 (Labels Reference)

`katenary help-labels` 명령으로 조회할 수 있는 전체 라벨 목록입니다. Docker Compose 파일의 서비스 하위 `labels`에 지정합니다:

```text
특정 라벨에 대한 상세 정보를 보려면: katenary help-label <접두사_없는_라벨명>
예: katenary help-label dependencies

katenary.v3/configmap-files:   []string                        파일들을 ConfigMap으로 주입합니다.
katenary.v3/cronjob:           object                          서비스로부터 CronJob을 생성합니다.
katenary.v3/dependencies:      []object                        서비스에 Helm 의존성(dependencies)을 추가합니다.
katenary.v3/description:       string                          서비스에 대한 설명
katenary.v3/env-from:          []string                        다른 서비스의 환경 변수를 추가합니다.
katenary.v3/exchange-volumes:  []object                        컨테이너 간 데이터 공유를 위한 교환 볼륨(emptyDir)을 추가합니다.
katenary.v3/health-check:      object                          배포(Deployment)에 추가할 헬스 체크(Health check) 설정
katenary.v3/ignore:            bool                            해당 서비스를 무시합니다 (매니페스트 생성 제외).
katenary.v3/ingress:           object                          서비스에 추가할 Ingress 규칙 설정
katenary.v3/main-app:          bool                            해당 서비스를 메인 앱으로 지정합니다.
katenary.v3/map-env:           map[string]string               서비스의 환경 변수를 Helm 템플릿 표현식으로 배포 매니페스트에 매핑합니다.
katenary.v3/ports:             []uint32                        서비스에 추가할 포트 목록
katenary.v3/same-pod:          string                          동일 파드 배포(same-pod deployment)를 대상 배포로 이동합니다.
katenary.v3/secrets:           []string                        쿠버네티스 시크릿(Secret)으로 설정할 환경 변수 목록
katenary.v3/values:            []string or map[string]string   values.yaml에 추가할 환경 변수 목록
katenary.v3/values-from:       map[string]string               다른 서비스로부터 값을 가져와 추가합니다.
```

---

## Katenary.yaml 파일 및 스키마 유효성 검사

Compose 파일 안에 직접 라벨을 작성하는 대신, 별도의 `katenary.yaml` 파일로 라벨 설정을 분리하여 관리할 수도 있습니다:

```yaml
web:
  ingress:
    hostname: myapp.example.com
    port: 80
```

`katenary.yaml` 파일의 스키마 유효성을 검사하려면 공식 원본 JSON 스키마를 사용합니다:
`https://repo.katenary.io/Katenary/katenary/raw/branch/master/katenary.json`

### VSCode 설정

VSCode `settings.json`에 다음 설정을 추가합니다:

```json
{
  "yaml.schemas": {
    "https://repo.katenary.io/Katenary/katenary/raw/branch/master/katenary.json": "katenary.yaml"
  }
}
```

### LazyVim / Neovim 설정 (`nvim-lspconfig`)

```lua
-- yaml.lua
return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        yamlls = {
          settings = {
            yaml = {
              schemas = {
                ["https://repo.katenary.io/Katenary/katenary/raw/branch/master/katenary.json"] = "katenary.yaml",
              },
            },
          },
        },
      },
    },
  },
}
```

---

## 이름의 유래… (What a name…)

Katenary라는 프로젝트의 스타일화된 이름은 현수선(懸垂線)을 의미하는 영단어 "catenary"에서 유래되었습니다.

현수선(catenary)이란 동일한 수직선상에 있지 않은 두 지점 사이에 줄, 로프 또는 체인을 자유롭게 늘어뜨렸을 때 생기는 곡선을 말합니다. 예를 들어, 배와 닻 사이에 드리워진 닻줄(앵커 체인) 곡선이 이에 해당합니다.

이 완만한 곡선의 연결선은 Katenary가 추구하는 바를 상징합니다. 즉, 이 프로젝트는 `docker-compose`에서 `helm chart`로 이어지는 유연하고 견고한 연결 고리입니다.

---

## 프로젝트 관련 문서 링크

- [프로젝트 메인 README](README.md)
- [Helm Chart 상세 배포 가이드](README(HelmChart).md)
- [로컬 KIND 배포 가이드](charts/getting-started-todo-app-openai-agent.local_kind/README.md)
- [GitHub Packages (GHCR) 배포 가이드](charts/getting-started-todo-app-openai-agent.github_kind/README.md)
- [GCP GKE 배포 가이드](charts/getting-started-todo-app-openai-agent.gcp_gke/README.md)
- [Katenary English Documentation](Katenary-README-EN.md)
