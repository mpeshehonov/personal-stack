"""Cursor SDK agent runner with resume support."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from orchestrator.config import STACK_DIR, load_env_file
from orchestrator.cursor_session import CursorBusyError, cursor_session
from orchestrator.state import kv_get, kv_set, log_run

logger = logging.getLogger(__name__)

KV_BOUNTY_AGENT = "cursor_bounty_agent_id"
KV_TASK_AGENT = "cursor_task_agent_id"
KV_DAILY_AGENT = "cursor_agent_id"


def _ensure_sdk():
    try:
        from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions
        return Agent, AgentOptions, CursorAgentError, LocalAgentOptions
    except ImportError:
        logger.error("cursor-sdk not installed")
        raise


def _api_key() -> str | None:
    load_env_file(".env.cursor")
    return os.environ.get("CURSOR_API_KEY", "").strip() or None


def _model() -> str:
    return os.environ.get("CURSOR_AGENT_MODEL", "auto").strip() or "auto"


def _bounty_model() -> str:
    return os.environ.get("BOUNTY_CURSOR_MODEL", "auto").strip() or "auto"


def _local_opts():
    _, _, _, LocalAgentOptions = _ensure_sdk()
    return LocalAgentOptions(cwd=str(STACK_DIR), setting_sources=["project"])


def _run_agent_prompt(
    prompt: str,
    *,
    owner: str,
    agent_kv_key: str,
    model: str | None = None,
    reset_agent: bool = False,
) -> str:
    """Full agent with tools (send + wait). Must run inside cursor_session."""
    api_key = _api_key()
    if not api_key:
        return "CURSOR_API_KEY not configured in secrets/.env.cursor"

    Agent, AgentOptions, CursorAgentError, _ = _ensure_sdk()
    use_model = model or _model()
    agent_id = None if reset_agent else kv_get(agent_kv_key)

    try:
        if agent_id:
            agent_ctx = Agent.resume(
                agent_id,
                AgentOptions(
                    api_key=api_key,
                    model=use_model,
                    local=_local_opts(),
                ),
            )
        else:
            agent_ctx = Agent.create(
                AgentOptions(
                    api_key=api_key,
                    model=use_model,
                    local=_local_opts(),
                ),
            )
    except Exception:
        agent_ctx = Agent.create(
            AgentOptions(
                api_key=api_key,
                model=use_model,
                local=_local_opts(),
            ),
        )

    try:
        with agent_ctx as agent:
            kv_set(agent_kv_key, agent.agent_id)
            run = agent.send(prompt)
            result = run.wait()
            text = (result.result or "").strip()
            if result.status == "error":
                log_run("cursor", "error", text[:500])
                return f"Run failed: {text[:500]}"
            log_run("cursor", "finished", text[:500])
            return text
    except CursorAgentError as e:
        return f"Cursor startup failed: {e.message}"


def run_cursor_prompt(
    prompt: str,
    one_shot: bool = False,
    *,
    owner: str = "cursor",
    agent_kv_key: str = KV_DAILY_AGENT,
    model: str | None = None,
    reset_agent: bool = False,
) -> str:
    """Run Cursor agent. Uses exclusive session lock."""
    try:
        with cursor_session(owner):
            if one_shot:
                Agent, AgentOptions, CursorAgentError, _ = _ensure_sdk()
                api_key = _api_key()
                if not api_key:
                    return "CURSOR_API_KEY not configured in secrets/.env.cursor"
                try:
                    result = Agent.prompt(
                        prompt,
                        AgentOptions(
                            api_key=api_key,
                            model=model or _model(),
                            local=_local_opts(),
                        ),
                    )
                    return result.result or f"Status: {result.status}"
                except CursorAgentError as e:
                    return f"Cursor startup failed: {e.message}"
            return _run_agent_prompt(
                prompt,
                owner=owner,
                agent_kv_key=agent_kv_key,
                model=model,
                reset_agent=reset_agent,
            )
    except CursorBusyError as e:
        return str(e)


def run_bounty_agent_prompt(prompt: str, *, phase: str, reset: bool = False) -> str:
    """Deep bounty phase — full agent with project skills + tools."""
    return run_cursor_prompt(
        prompt,
        one_shot=False,
        owner=f"bounty:{phase}",
        agent_kv_key=KV_BOUNTY_AGENT,
        model=_bounty_model(),
        reset_agent=reset,
    )


def run_daily_agent(context: str, light_mode: bool) -> str:
    from orchestrator.config import TASKS_DIR

    mode_note = (
        "ОБЛЕГЧЁННЫЙ РЕЖИМ: без finance-сделок и тяжёлых PDF. Только health и критичные правки сайта."
        if light_mode
        else "ПОЛНЫЙ РЕЖИМ: улучшения сайта, income backlog, finance proposals."
    )
    harness = (TASKS_DIR / "daily_prompt.md").read_text(encoding="utf-8")
    prompt = f"""Ты автономный агент для /opt/personal-stack.

{mode_note}

{context}

---

{harness}

Работай только в /opt/personal-stack. Используй инструменты (curl, чтение файлов, правки).
Начни с секции ## План в daily-логе, затем выполни bounded work.
"""
    summary = run_cursor_prompt(
        prompt,
        one_shot=False,
        owner="daily",
        agent_kv_key=KV_DAILY_AGENT,
        reset_agent=True,
    )
    from orchestrator.memory import append_daily_section

    if not summary.startswith("Cursor ") and "Run failed" not in summary[:20]:
        append_daily_section("Итог", summary[:1500])
    return summary


def run_ask(prompt: str) -> str:
    return run_cursor_prompt(_wrap_ask_prompt(prompt), one_shot=True, owner="ask")


def _wrap_ask_prompt(user_text: str) -> str:
    return f"""Режим: только ответ на вопрос (read-only).

Пользователь спрашивает:
{user_text}

Правила:
- НЕ изменяй файлы, НЕ запускай команды с побочными эффектами, НЕ коммить.
- Отвечай по-русски, кратко и по делу.
- Можно использовать Markdown (списки, `code`, **жирный**) — бот отрендерит форматирование.
- Если нужен доступ к коду — читай workspace /opt/personal-stack.
"""


def _wrap_task_prompt(user_text: str) -> str:
    return f"""Режим: выполнение задачи с правками кода.

Задача пользователя:
{user_text}

Правила:
- Работай только в /opt/personal-stack.
- Перед правками репозиторий уже синхронизирован с origin/main (git pull выполнен).
- НЕ трогай secrets/ и не выводи секреты.
- НЕ коммить и НЕ push сам — commit, push и deploy выполнит бот после ответа.
- Отвечай с Markdown (заголовки ##, списки, `code`, таблицы) — бот отрендерит Rich Message.
- Любой URL в ответе проверь curl -fsSI или curl -fsS (ожидается HTTP 200). Не давай ссылки с 404/5xx.
- Если добавляешь файлы за nginx/docker — перезапусти нужный контейнер и снова проверь URL.
- Для Happ routing после build-happ-routing.sh: cd vpn/hysteria2 && docker compose up -d hy2-subscription.
- В конце дай краткое резюме по-русски: что изменил и зачем (1–5 пунктов).
"""


def run_task(prompt: str) -> str:
    return run_cursor_prompt(
        _wrap_task_prompt(prompt),
        one_shot=False,
        owner="task",
        agent_kv_key=KV_TASK_AGENT,
    )


def _stream_agent(prompt: str, on_text, *, one_shot: bool, owner: str) -> str:
    api_key = _api_key()
    if not api_key:
        msg = "CURSOR_API_KEY не настроен в secrets/.env.cursor"
        on_text(msg)
        return msg

    Agent, AgentOptions, CursorAgentError, _ = _ensure_sdk()
    accumulated = ""

    try:
        with cursor_session(owner):
            if one_shot:
                agent_ctx = Agent.create(
                    AgentOptions(
                        api_key=api_key,
                        model=_model(),
                        local=_local_opts(),
                    ),
                )
                agent_kv_key = None
            else:
                agent_kv_key = KV_TASK_AGENT
                agent_id = kv_get(agent_kv_key)
                try:
                    if agent_id:
                        agent_ctx = Agent.resume(
                            agent_id,
                            AgentOptions(
                                api_key=api_key,
                                model=_model(),
                                local=_local_opts(),
                            ),
                        )
                    else:
                        agent_ctx = Agent.create(
                            AgentOptions(
                                api_key=api_key,
                                model=_model(),
                                local=_local_opts(),
                            ),
                        )
                except Exception:
                    agent_ctx = Agent.create(
                        AgentOptions(
                            api_key=api_key,
                            model=_model(),
                            local=_local_opts(),
                        ),
                    )

            with agent_ctx as agent:
                if agent_kv_key:
                    kv_set(agent_kv_key, agent.agent_id)
                run = agent.send(prompt)
                for chunk in run.iter_text():
                    if chunk:
                        accumulated += chunk
                        on_text(accumulated)
                result = run.wait()
                final = (result.result or accumulated or "").strip()
                if final and final != accumulated:
                    accumulated = final
                    on_text(accumulated)
                if result.status == "error":
                    err = f"Ошибка агента: {final[:500]}"
                    on_text(err)
                    log_run("cursor", "error", err[:500])
                    return err
                log_run("cursor", "finished", final[:500])
                return final
    except CursorBusyError as e:
        err = str(e)
        on_text(err)
        return err
    except CursorAgentError as e:
        err = f"Не удалось запустить агента: {e.message}"
        on_text(err)
        return err
    except Exception as e:
        err = f"Сбой при выполнении: {e}"
        on_text(err)
        logger.exception("_stream_agent failed")
        return err


def run_ask_streaming(prompt: str, on_text) -> str:
    """Read-only Q&A with streaming."""
    return _stream_agent(_wrap_ask_prompt(prompt), on_text, one_shot=True, owner="ask")


def run_task_streaming(prompt: str, on_text) -> str:
    """Task with code changes; commit/deploy handled by caller."""
    return _stream_agent(_wrap_task_prompt(prompt), on_text, one_shot=False, owner="task")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    text = run_ask(" ".join(sys.argv[1:]) or "Say hello and confirm you can access the workspace.")
    print(text)
