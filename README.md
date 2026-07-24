# Hermes-Agent

Hermes-Agent는 여러 웹사이트의 콘텐츠를 수집하고 Ollama를 이용해 내용을 분석하는 로컬 AI 에이전트입니다.

경쟁사 홈페이지 조사부터 분석 보고서, 홈페이지 기획안, HTML 사이트 생성까지 하나의 명령으로 처리할 수 있습니다.

## 주요 기능

- 웹사이트 내부 페이지 자동 수집
- `robots.txt` 및 `sitemap.xml` 지원
- 링크 탐색 깊이와 최대 페이지 수 설정
- 여러 경쟁사 홈페이지 동시 조사
- Ollama 기반 질문·답변 및 분석 보고서 생성
- 특정 출처로 벡터 검색 범위 제한
- 홈페이지 기획안 자동 생성
- Markdown, JSON, HTML 출력
- HTML, CSS, JavaScript 분리형 사이트 생성
- 일부 사이트 수집 실패 시 나머지 사이트 계속 처리

## 실행 환경

- Python 3.12 이상
- uv
- Ollama
- Playwright
- macOS, Linux

## 설치

프로젝트를 내려받고 프로젝트 디렉터리로 이동합니다.

```bash
git clone https://github.com/cg63sun/Hermes-Agent.git
cd Hermes-Agent
```

의존성을 설치합니다.

```bash
uv sync --locked
```

`uv.lock` 파일과 `pyproject.toml`의 의존성이 일치하지 않아 실패한다면 다음 명령으로 동기화합니다.

```bash
uv sync
```

Playwright 브라우저가 설치되지 않았다면 Chromium을 설치합니다.

```bash
uv run playwright install chromium
```

## Ollama 설치 및 모델 준비

Ollama가 설치되어 있지 않다면 공식 사이트에서 설치합니다.

- https://ollama.com

Ollama 서버가 실행 중인지 확인합니다.

```bash
ollama --version
```

답변과 홈페이지 기획안 생성에 사용할 모델을 설치합니다.

```bash
ollama pull qwen3:8b
```

문서 임베딩에 사용할 모델을 설치합니다.

```bash
ollama pull nomic-embed-text
```

설치된 모델을 확인합니다.

```bash
ollama list
```

기본 Ollama 서버 주소는 다음과 같습니다.

```text
http://127.0.0.1:11434
```

## 제공 명령

Hermes-Agent는 다음 세 가지 명령을 제공합니다.

| 명령 | 기능 |
|---|---|
| `hermes-crawl` | 웹사이트를 크롤링하고 JSON 보고서 저장 |
| `hermes-research` | 여러 웹사이트를 조사하고 질문에 대한 분석 보고서 생성 |
| `hermes-site-plan` | 경쟁사를 분석해 홈페이지 기획안과 사이트 생성 |

각 명령은 `uv run`으로 실행합니다.

```bash
uv run hermes-crawl --help
uv run hermes-research --help
uv run hermes-site-plan --help
```

---

## 1. 웹사이트 크롤링

### 기본 사용법

```bash
uv run hermes-crawl \
  https://example.com
```

### 수집 결과 저장

```bash
uv run hermes-crawl \
  https://example.com \
  --max-pages 20 \
  --max-depth 2 \
  --output output/crawl-report.json
```

### 옵션

| 옵션 | 설명 |
|---|---|
| `url` | 크롤링을 시작할 URL |
| `--max-pages` | 최대 수집 페이지 수 |
| `--max-depth` | 최대 링크 탐색 깊이 |
| `--output` | JSON 보고서 저장 경로 |
| `--no-robots` | `robots.txt` 검사 비활성화 |
| `--no-sitemap` | `sitemap.xml` 사용 비활성화 |
| `--no-filter` | URL 필터 비활성화 |

### robots.txt 검사를 사용하지 않는 예제

사이트 수집 권한과 이용 약관을 직접 확인한 경우에만 사용하세요.

```bash
uv run hermes-crawl \
  https://example.com \
  --no-robots \
  --output output/crawl-report.json
```

---

## 2. 웹사이트 조사 및 분석

`hermes-research`는 여러 웹사이트를 수집한 후 문서를 청크로 나누고, 임베딩 검색 결과를 이용해 Ollama가 질문에 답하도록 합니다.

### 기본 사용법

```bash
uv run hermes-research \
  https://example.com \
  --question "이 업체의 주요 서비스와 강점을 분석하세요."
```

### 여러 웹사이트 비교

```bash
uv run hermes-research \
  https://example.com \
  https://example.org \
  --question "두 업체의 주요 서비스, 강점, 가격 정책과 차별점을 비교하세요." \
  --output output/research-report.md
```

### 전체 옵션 사용 예제

```bash
uv run hermes-research \
  https://example.com \
  https://example.org \
  --question "경쟁사의 핵심 서비스와 차별화 요소를 분석하세요." \
  --top-k 5 \
  --chunk-size 500 \
  --model qwen3:8b \
  --embedding-model nomic-embed-text \
  --ollama-url http://127.0.0.1:11434 \
  --generation-timeout 300 \
  --output output/research-report.md
```

### 특정 출처만 검색

여러 웹사이트를 수집한 후 특정 URL에서 생성된 문서만 검색하려면 `--source`를 사용합니다.

```bash
uv run hermes-research \
  https://example.com \
  https://example.org \
  --question "이 업체의 핵심 서비스를 정리하세요." \
  --source https://example.com \
  --top-k 5 \
  --output output/example-report.md
```

`--source` 값은 수집된 문서의 출처 URL과 일치해야 합니다.

### 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `urls` | 수집할 웹사이트 URL 한 개 이상 | 필수 |
| `--question`, `-q` | 수집한 내용을 바탕으로 질문할 내용 | 필수 |
| `--top-k` | 답변 생성에 사용할 검색 결과 수 | `5` |
| `--source` | 검색 대상을 제한할 출처 URL | 제한 없음 |
| `--chunk-size` | 문서를 나눌 청크 크기 | `500` |
| `--model` | Ollama 답변 생성 모델 | `qwen3:8b` |
| `--embedding-model` | Ollama 임베딩 모델 | `nomic-embed-text` |
| `--ollama-url` | Ollama 서버 주소 | `http://127.0.0.1:11434` |
| `--generation-timeout` | 답변 생성 제한 시간(초) | `300` |
| `--output`, `-o` | Markdown 보고서 저장 경로 | 명령 기본 경로 |
| `--stop-on-error` | 사이트 하나의 수집 실패 시 즉시 중단 | 비활성화 |

기본적으로 일부 웹사이트 수집이 실패해도 정상 수집된 사이트를 이용해 작업을 계속합니다.

모든 수집 오류에서 즉시 중단하려면 다음 옵션을 추가합니다.

```bash
--stop-on-error
```

---

## 3. 홈페이지 기획안 및 사이트 생성

`hermes-site-plan`은 경쟁사 홈페이지를 조사한 후 사업 정보에 맞는 홈페이지 기획안을 생성합니다.

생성되는 기획안에는 다음 정보가 포함됩니다.

- 홈페이지 콘셉트
- 핵심 메시지
- 페이지별 목적
- 헤드라인
- 본문 콘텐츠
- 행동 유도 문구
- 조사에 사용된 출처 URL

### 기본 사용법

```bash
uv run hermes-site-plan \
  https://example.com \
  --business-name "여수넷" \
  --business-type "홈페이지 제작 및 AI 챗봇 개발" \
  --target-audience "홈페이지가 필요한 지역 소상공인과 중소기업" \
  --goal "서비스를 소개하고 상담 문의를 늘리는 홈페이지 제작"
```

### 경쟁사 여러 곳 분석

```bash
uv run hermes-site-plan \
  https://example.com \
  https://example.org \
  --business-name "여수넷" \
  --business-type "홈페이지 제작 및 AI 챗봇 개발" \
  --target-audience "홈페이지 제작이 필요한 여수 지역 소상공인과 중소기업" \
  --goal "경쟁사의 서비스와 강점을 분석하여 차별화된 홈페이지 기획안 만들기" \
  --output output/yeosunet-site-plan.md
```

### Markdown과 JSON 동시 생성

```bash
uv run hermes-site-plan \
  https://example.com \
  https://example.org \
  --business-name "여수넷" \
  --business-type "홈페이지 제작 및 AI 챗봇 개발" \
  --target-audience "여수 지역 소상공인과 중소기업" \
  --goal "온라인 상담 문의 증가" \
  --output output/yeosunet-site-plan.md \
  --json-output output/yeosunet-site-plan.json
```

### 단일 HTML 홈페이지 생성

CSS와 JavaScript가 포함된 단일 HTML 파일을 생성합니다.

```bash
uv run hermes-site-plan \
  https://example.com \
  https://example.org \
  --business-name "여수넷" \
  --business-type "홈페이지 제작 및 AI 챗봇 개발" \
  --target-audience "여수 지역 소상공인과 중소기업" \
  --goal "서비스 소개와 상담 문의 증가" \
  --output output/yeosunet-site-plan.md \
  --html-output output/yeosunet-index.html
```

생성된 HTML 파일은 브라우저에서 직접 열어 확인할 수 있습니다.

macOS:

```bash
open output/yeosunet-index.html
```

Linux:

```bash
xdg-open output/yeosunet-index.html
```

### HTML, CSS, JavaScript 분리형 사이트 생성

```bash
uv run hermes-site-plan \
  https://example.com \
  https://example.org \
  --business-name "여수넷" \
  --business-type "홈페이지 제작 및 AI 챗봇 개발" \
  --target-audience "여수 지역 소상공인과 중소기업" \
  --goal "서비스 소개와 상담 문의 증가" \
  --output output/yeosunet-site-plan.md \
  --json-output output/yeosunet-site-plan.json \
  --site-output-dir output/yeosunet-site
```

생성되는 기본 구조는 다음과 같습니다.

```text
output/yeosunet-site/
├── index.html
└── assets/
    ├── style.css
    └── script.js
```

브라우저에서 확인합니다.

```bash
open output/yeosunet-site/index.html
```

### 모든 출력 형식 동시 생성

```bash
uv run hermes-site-plan \
  https://veryeasy.kr/price \
  https://website.it.kr \
  --business-name "여수넷" \
  --business-type "홈페이지 제작 및 AI 챗봇 개발" \
  --target-audience "홈페이지 제작이 필요한 여수 지역 소상공인과 중소기업" \
  --goal "경쟁사의 서비스와 가격을 분석하여 여수넷 홈페이지 기획안 만들기" \
  --question "경쟁사의 주요 서비스, 강점, 핵심 메시지, 페이지 구성과 차별화 요소를 분석하세요." \
  --top-k 5 \
  --chunk-size 500 \
  --model qwen3:8b \
  --embedding-model nomic-embed-text \
  --generation-timeout 300 \
  --output output/yeosunet-site-plan.md \
  --json-output output/yeosunet-site-plan.json \
  --html-output output/yeosunet-index.html \
  --site-output-dir output/yeosunet-site
```

### 특정 경쟁사 출처로 검색 제한

여러 사이트를 수집하되 기획안 작성에 전달되는 검색 결과를 특정 출처로 제한할 수 있습니다.

```bash
uv run hermes-site-plan \
  https://example.com \
  https://example.org \
  --business-name "여수넷" \
  --business-type "홈페이지 제작 및 AI 챗봇 개발" \
  --target-audience "여수 지역 소상공인과 중소기업" \
  --goal "경쟁사 분석을 바탕으로 홈페이지 기획안 만들기" \
  --source https://example.com \
  --output output/yeosunet-site-plan.md
```

### 옵션

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `urls` | 조사할 경쟁사 웹사이트 URL 한 개 이상 | 필수 |
| `--business-name` | 홈페이지를 만들 상호 | 필수 |
| `--business-type` | 사업 업종 | 필수 |
| `--target-audience` | 핵심 고객 | 필수 |
| `--goal` | 홈페이지 제작 목표 | 필수 |
| `--question` | 경쟁사 조사 질문 | 기본 분석 질문 |
| `--top-k` | 연구 답변에 사용할 검색 결과 수 | `5` |
| `--source` | 검색 대상을 제한할 출처 URL | 제한 없음 |
| `--chunk-size` | 문서를 나눌 청크 크기 | `500` |
| `--model` | Ollama 생성 모델 | `qwen3:8b` |
| `--embedding-model` | Ollama 임베딩 모델 | `nomic-embed-text` |
| `--ollama-url` | Ollama 서버 주소 | `http://127.0.0.1:11434` |
| `--generation-timeout` | Ollama 생성 요청 제한 시간(초) | `300` |
| `--output`, `-o` | 기획안 Markdown 저장 경로 | `output/site-plan.md` |
| `--json-output` | 기획안 JSON 저장 경로 | 생성 안 함 |
| `--html-output` | 단일 HTML 저장 경로 | 생성 안 함 |
| `--site-output-dir` | 분리형 사이트 저장 폴더 | 생성 안 함 |
| `--stop-on-error` | 웹사이트 수집 실패 시 즉시 중단 | 비활성화 |

## 생성 시간이 오래 걸리는 경우

`qwen3:8b` 모델은 컴퓨터 성능과 조사할 문서의 양에 따라 생성 시간이 오래 걸릴 수 있습니다.

시간 초과가 발생하면 제한 시간을 늘립니다.

```bash
--generation-timeout 600
```

예제:

```bash
uv run hermes-research \
  https://example.com \
  --question "주요 서비스와 강점을 자세히 분석하세요." \
  --generation-timeout 600
```

Ollama가 정상 실행 중인지 확인합니다.

```bash
curl http://127.0.0.1:11434/api/tags
```

모델이 설치되어 있는지도 확인합니다.

```bash
ollama list
```

## 테스트

전체 테스트를 실행합니다.

```bash
uv run pytest -q
```

특정 테스트 파일만 실행할 수도 있습니다.

```bash
uv run pytest tests/cli/test_site_plan_cli.py -q
```

코드의 공백 오류를 검사합니다.

```bash
git diff --check
```

## 개발 작업 확인

현재 변경 내용을 확인합니다.

```bash
git status --short
git diff
```

테스트와 검사가 모두 성공하면 커밋합니다.

```bash
git add README.md
git commit -m "docs: add project usage guide"
git push origin main
```

마지막으로 작업 상태를 확인합니다.

```bash
git status --short
```

아무 내용도 출력되지 않으면 커밋되지 않은 변경 사항이 없는 깨끗한 상태입니다.

## 주의 사항

- 다른 웹사이트를 수집할 때는 해당 사이트의 이용 약관과 `robots.txt` 정책을 확인하세요.
- 수집한 콘텐츠를 그대로 복제하지 말고 조사, 비교 및 기획 참고 자료로 사용하세요.
- `--no-robots` 옵션은 대상 사이트의 수집 권한을 확인한 경우에만 사용하세요.
- 생성된 기획안과 HTML은 AI 결과물이므로 실제 배포 전에 문구, 연락처, 링크와 사업 정보를 검토하세요.

## 라이선스

이 프로젝트의 라이선스 정책은 저장소의 라이선스 파일을 따릅니다.
