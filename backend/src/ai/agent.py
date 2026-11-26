"""OpenAI Agents SDK 공통 실행 모듈

classifier(도구 없는 단일 분류)와 planner(도구를 쓰는 일정 브리핑)가 함께 쓴다.
각 기능은 Agents SDK 의 Agent 로 정의하고, 이 모듈의 run_structured() 가
Runner 로 에이전트를 실행해 output_type(Pydantic) 으로 검증된 결과를 돌려준다.

설정 (환경변수):
  - OPENAI_API_KEY / OPENAI_API_KEY_FILE (Docker/K8s Secret 마운트용 파일 경로)
  - AI_MODEL        : 사용할 모델 (생략 시 DEFAULT_MODEL)
  - OPENAI_BASE_URL : (선택) OpenAI 호환 엔드포인트를 쓸 때. openai 클라이언트가 직접 읽는다.
  - OPENAI_AGENTS_DISABLE_TRACING=1 : (선택) OpenAI 대시보드로의 트레이스 전송 끄기
API 키가 없거나 AI_ENABLED=false (구버전 이름 AI_CLASSIFY_ENABLED 도 인정) 이면 AI 기능은 꺼진다.
"""
import logging
import os
from typing import Any, TypeVar

from agents import Agent, FunctionTool, Runner, set_default_openai_key
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-5.6-luna"
# 도구 호출 → 결과 → 최종 응답까지 넉넉히. 무한 루프로 비용이 새지 않도록 상한을 둔다.
MAX_TURNS = 8

T = TypeVar("T", bound=BaseModel)


def read_api_key() -> str | None:
    """키 파일(OPENAI_API_KEY_FILE)이 있으면 그 내용을, 없으면 OPENAI_API_KEY 를 돌려준다."""
    file_path = os.getenv("OPENAI_API_KEY_FILE")
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            key = f.read().strip()
            if key:
                return key
    return os.getenv("OPENAI_API_KEY") or None


def resolve_model() -> str | None:
    """사용할 모델 이름. API 키가 없으면 None."""
    if read_api_key() is None:
        return None
    return os.getenv("AI_MODEL") or DEFAULT_MODEL


def is_enabled() -> bool:
    for name in ("AI_ENABLED", "AI_CLASSIFY_ENABLED"):
        if os.getenv(name, "true").lower() in ("false", "0", "no"):
            return False
    return resolve_model() is not None


def build_agent(
    *,
    name: str,
    instruction: str,
    schema: type[BaseModel],
    tools: list[FunctionTool] | None = None,
) -> Agent | None:
    """앱 전용 에이전트. 결과는 schema 로 강제되고, 도구는 넘겨 준 함수 도구만 쓸 수 있다."""
    model = resolve_model()
    if model is None:
        return None
    # 키 파일로 받은 경우에도 동작하도록 SDK 기본 클라이언트(모델 호출·트레이싱)에 키를 넣어 둔다.
    set_default_openai_key(read_api_key())
    return Agent(
        name=name,
        instructions=instruction,
        model=model,
        tools=list(tools or []),
        output_type=schema,
    )


async def run_structured(agent: Agent, prompt: str, schema: type[T]) -> T | None:
    """에이전트를 실행해 구조화된 결과를 schema 로 검증해 돌려준다. 실패 시 None.

    할 일 저장(CRUD)은 AI 가 실패해도 항상 동작해야 하므로 예외를 밖으로 던지지 않는다.
    Runner.run 은 호출마다 새 대화로 시작하므로 요청 간 내용이 섞이지 않는다.
    """
    try:
        result = await Runner.run(agent, prompt, max_turns=MAX_TURNS)
    except Exception as e:  # noqa: BLE001 - 모델/네트워크/인증 오류도 CRUD 를 막으면 안 된다
        logger.warning("에이전트 실행 실패: %s", e)
        return None

    output: Any = result.final_output
    if output is None:
        logger.warning("에이전트가 결과를 돌려주지 않았습니다.")
        return None
    try:
        if isinstance(output, schema):
            return output
        if isinstance(output, str):
            return schema.model_validate_json(output)
        return schema.model_validate(output)
    except ValidationError as e:
        logger.warning("AI 결과가 스키마와 맞지 않습니다: %s", e)
        return None
