"""planner(일정 브리핑 에이전트, OpenAI Agents SDK) 테스트 — 도구 함수와 에이전트 구성만 검증, 실제 모델은 호출하지 않는다"""
import json
from unittest.mock import AsyncMock, patch

import pytest

from src.ai import agent, planner
from src.models import Briefing

from .test_classifier import AI_ENV, fake_runner

BRIEFING = {
    "summary": "오늘은 보고서 마감이 있습니다.",
    "focus": [{"item_id": "1", "name": "보고서", "reason": "오늘 마감"}],
    "warnings": [],
    "tips": ["오전에 먼저 처리하세요"],
}


@pytest.fixture(autouse=True)
def openai_key(monkeypatch):
    for n in AI_ENV:
        monkeypatch.delenv(n, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


async def test_make_briefing_uses_tools_and_returns_model():
    cap = {}
    with patch.object(agent, "Runner", fake_runner(Briefing(**BRIEFING), captured=cap)):
        result = await planner.make_briefing("2026-11-25")

    assert result.focus[0].item_id == "1"
    assert "오늘 날짜: 2026-11-25" in cap["prompt"]
    a = cap["agent"]
    assert a.output_type is Briefing
    assert [t.name for t in a.tools] == planner.TOOL_NAMES
    assert set(planner.TOOL_NAMES) == {"get_schedule", "search_items", "get_category_counts"}


async def test_make_briefing_disabled_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    assert await planner.make_briefing() is None


def test_tool_schemas_come_from_docstrings():
    tools = {t.name: t for t in planner.TOOLS}
    schedule = tools["get_schedule"]
    assert "날짜" in schedule.description
    assert schedule.params_json_schema["required"] == ["date"]
    assert "YYYY-MM-DD" in schedule.params_json_schema["properties"]["date"]["description"]


async def test_get_schedule_tool_reads_db():
    rows = [{"id": "1", "name": "보고서"}]
    with patch("src.persistence.get_schedule", new_callable=AsyncMock, return_value=rows) as m:
        out = await planner.get_schedule("2026-11-25")
    m.assert_awaited_once_with("2026-11-25")
    assert out == {"status": "success", "items": rows}
    json.dumps(out)  # 도구 결과는 JSON 직렬화 가능해야 한다


async def test_get_schedule_tool_rejects_bad_date():
    out = await planner.get_schedule("내일")
    assert out["status"] == "error"


async def test_search_items_tool_hides_completed():
    rows = [{"id": "1", "completed": True}, {"id": "2", "completed": False}]
    with patch("src.persistence.get_items", new_callable=AsyncMock, return_value=rows):
        out = await planner.search_items("")
    assert [i["id"] for i in out["items"]] == ["2"]


async def test_get_category_counts_tool():
    with patch("src.persistence.get_category_counts", new_callable=AsyncMock,
               return_value={"study": 2}):
        out = await planner.get_category_counts()
    assert out == {"status": "success", "counts": {"study": 2}}
