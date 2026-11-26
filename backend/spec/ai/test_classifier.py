"""classifier 단위 테스트 — 실제 모델은 호출하지 않는다 (Agents SDK 의 Runner 를 mock)"""
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.ai import agent, classifier
from src.models import Classification

AI_ENV = (
    "OPENAI_API_KEY", "OPENAI_API_KEY_FILE", "AI_MODEL", "AI_ENABLED", "AI_CLASSIFY_ENABLED",
)


def fake_runner(output=None, *, captured=None, error=None):
    """agent.Runner 를 대체하는 가짜. Runner.run 이 미리 정한 final_output 을 돌려준다.

    output 은 Pydantic 모델(정상 경로), dict/str(JSON) 또는 None 일 수 있다.
    """

    class FakeRunner:
        @classmethod
        async def run(cls, starting_agent, input, **kwargs):
            if captured is not None:
                captured["agent"] = starting_agent
                captured["prompt"] = input
                captured["kwargs"] = kwargs
            if error:
                raise error
            return SimpleNamespace(final_output=output)

    return FakeRunner


@pytest.fixture(autouse=True)
def openai_key(monkeypatch):
    for n in AI_ENV:
        monkeypatch.delenv(n, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")


async def _classify(*args, runner=None, **kw):
    with patch.object(agent, "Runner", runner):
        return await classifier.classify_item(*args, **kw)


async def test_it_returns_parsed_classification():
    cap = {}
    out = Classification(category="study", priority="high")
    result = await _classify("내일까지 클라우드 과제 제출",
                             runner=fake_runner(out, captured=cap))

    assert result == Classification(category="study", priority="high")
    a = cap["agent"]
    assert a.model == agent.DEFAULT_MODEL
    assert a.tools == []                          # 도구 없음
    assert a.output_type is Classification
    assert cap["kwargs"]["max_turns"] == agent.MAX_TURNS
    assert "<todo>내일까지 클라우드 과제 제출</todo>" in cap["prompt"]


async def test_it_accepts_json_text_output():
    out = json.dumps({"category": "work", "priority": "low"})
    result = await _classify("보고서", runner=fake_runner(out))
    assert result.category == "work"


async def test_it_uses_ai_model_env(monkeypatch):
    monkeypatch.setenv("AI_MODEL", "gpt-5.6-sol")
    cap = {}
    await _classify("보고서", runner=fake_runner(None, captured=cap))
    assert cap["agent"].model == "gpt-5.6-sol"


async def test_it_is_disabled_without_any_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY")
    cap = {}
    assert await _classify("장보기", runner=fake_runner(captured=cap)) is None
    assert cap == {}
    assert classifier.is_enabled() is False


@pytest.mark.parametrize("name", ["AI_ENABLED", "AI_CLASSIFY_ENABLED"])
def test_it_can_be_disabled_by_env(monkeypatch, name):
    monkeypatch.setenv(name, "false")
    assert classifier.is_enabled() is False


def test_it_reads_openai_key_from_file(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY")
    key_file = tmp_path / "openai_api_key"
    key_file.write_text("file-key\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY_FILE", str(key_file))

    assert agent.read_api_key() == "file-key"
    assert classifier.is_enabled() is True


async def test_it_returns_none_on_runner_error():
    assert await _classify("회의 준비", runner=fake_runner(error=RuntimeError("boom"))) is None


async def test_it_returns_none_without_final_output():
    assert await _classify("무언가", runner=fake_runner(None)) is None


async def test_it_returns_none_on_schema_mismatch():
    bad = {"category": "nonsense", "priority": "high"}
    assert await _classify("무언가", runner=fake_runner(bad)) is None


async def test_it_returns_none_on_non_json_text():
    assert await _classify("무언가", runner=fake_runner("분류 불가")) is None


async def test_it_sends_today_and_returns_due_date():
    cap = {}
    out = Classification(category="work", priority="high",
                         due_date="2026-11-26", due_time="09:00")
    result = await _classify("내일 오전 9시까지 보고서", "2026-11-25",
                             runner=fake_runner(out, captured=cap))

    assert "오늘 날짜: 2026-11-25" in cap["prompt"]
    assert (result.due_date, result.due_time) == ("2026-11-26", "09:00")


async def test_it_does_not_send_today_when_not_given():
    cap = {}
    out = Classification(category="work", priority="high")
    await _classify("보고서", runner=fake_runner(out, captured=cap))
    assert "오늘 날짜" not in cap["prompt"]


@pytest.mark.parametrize(
    "due_date,due_time,expected",
    [
        ("2026-02-31", "09:00", (None, None)),        # 존재하지 않는 날짜 → 일정 버림
        ("tomorrow", "09:00", (None, None)),          # 형식 오류
        ("2026-11-26", "9am", ("2026-11-26", None)),  # 시간만 잘못 → 시간만 버림
        (None, "09:00", (None, None)),                # 날짜 없이 시간만 → 버림
    ],
)
async def test_it_discards_invalid_ai_due_values(due_date, due_time, expected):
    out = Classification(category="work", priority="low", due_date=due_date, due_time=due_time)
    result = await _classify("x", "2026-11-25", runner=fake_runner(out))
    assert (result.due_date, result.due_time) == expected
