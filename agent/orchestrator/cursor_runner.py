"""Cursor SDK agent runner with resume support."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from orchestrator.config import STACK_DIR, load_env_file
from orchestrator.cursor_bridge import cleanup_cursor_bridge
from orchestrator.memory import append_daily_section, build_context_pack
from orchestrator.state import kv_get, kv_set, log_run

logger = logging.getLogger(__name__)


def _ensure_sdk():
    try:
        from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions
        return Agent, AgentOptions, CursorAgentError, LocalAgentOptions
    except ImportError:
        logger.error("cursor-sdk not installed")
        raise


def run_cursor_prompt(prompt: str, one_shot: bool = False) -> str:
    load_env_file(".env.cursor")
    api_key = os.environ.get("CURSOR_API_KEY")
    if not api_key:
        return "CURSOR_API_KEY not configured in secrets/.env.cursor"

    cleanup_cursor_bridge()
    Agent, AgentOptions, CursorAgentError, LocalAgentOptions = _ensure_sdk()
    cwd = str(STACK_DIR)

    try:
        if one_shot:
            try:
                result = Agent.prompt(
                    prompt,
                    AgentOptions(
                        api_key=api_key,
                        model="auto",
                        local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                    ),
                )
                return result.result or f"Status: {result.status}"
            except CursorAgentError as e:
                return f"Cursor startup failed: {e.message}"

        agent_id = kv_get("cursor_agent_id")
        try:
            if agent_id:
                agent_ctx = Agent.resume(
                    agent_id,
                    AgentOptions(
                        api_key=api_key,
                        model="auto",
                        local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                    ),
                )
            else:
                agent_ctx = Agent.create(
                    AgentOptions(
                        api_key=api_key,
                        model="auto",
                        local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                    ),
                )
        except Exception:
            agent_ctx = Agent.create(
                AgentOptions(
                    api_key=api_key,
                    model="auto",
                    local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                ),
            )

        with agent_ctx as agent:
            if not agent_id:
                kv_set("cursor_agent_id", agent.agent_id)
            run = agent.send(prompt)
            result = run.wait()
            summary = (result.result or "")[:2000]
            if result.status == "error":
                log_run("cursor", "error", summary)
                return f"Run failed: {summary}"
            log_run("cursor", "finished", summary)
            return summary
    finally:
        cleanup_cursor_bridge()


def run_daily_agent(context: str, light_mode: bool) -> str:
    mode_note = (
        "ОБЛЕГЧЁННЫЙ РЕЖИМ: без finance-сделок и тяжёлых PDF. Только health и критичные правки сайта."
        if light_mode
        else "ПОЛНЫЙ РЕЖИМ: улучшения сайта, bounty, finance."
    )
    prompt = f"""Ты автономный агент для /opt/personal-stack.

{mode_note}

{context}

Инструкции:
1. Проверь здоровье сайта; если лежит — почини и запусти scripts/redeploy-site.sh
2. Возьми не больше 1–2 пунктов из бэклога сайта; коммить изменения в site/
3. Bug bounty — **не дублируй**: semi-auto ресёрч запускает orchestrator (`bounty/scanner.py`). В daily-логе только краткий итог, если был ручной анализ.
4. Проанализируй finance; выводи JSON-предложения для risk engine (формат на английском)
5. Добавь уроки в agent/memory/lessons/, если узнал что-то полезное
6. Обнови agent/memory/daily/ сегодняшний лог разделами: Итог, Сайт, Финансы, Баг-баунти, Уроки — **на русском**

Работай только в /opt/personal-stack. Не раскрывай секреты.
"""
    summary = run_cursor_prompt(prompt, one_shot=True)
    append_daily_section("Итог", summary[:1500])
    return summary


def run_ask(prompt: str) -> str:
    return run_cursor_prompt(_wrap_ask_prompt(prompt), one_shot=True)


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
    return run_cursor_prompt(_wrap_task_prompt(prompt), one_shot=False)


def _stream_agent(prompt: str, on_text, *, one_shot: bool) -> str:
    load_env_file(".env.cursor")
    api_key = os.environ.get("CURSOR_API_KEY")
    if not api_key:
        msg = "CURSOR_API_KEY не настроен в secrets/.env.cursor"
        on_text(msg)
        return msg

    cleanup_cursor_bridge()
    Agent, AgentOptions, CursorAgentError, LocalAgentOptions = _ensure_sdk()
    cwd = str(STACK_DIR)
    accumulated = ""

    try:
        if one_shot:
            agent_ctx = Agent.create(
                AgentOptions(
                    api_key=api_key,
                    model="auto",
                    local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                ),
            )
        else:
            agent_id = kv_get("cursor_task_agent_id")
            try:
                if agent_id:
                    agent_ctx = Agent.resume(
                        agent_id,
                        AgentOptions(
                            api_key=api_key,
                            model="auto",
                            local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                        ),
                    )
                else:
                    agent_ctx = Agent.create(
                        AgentOptions(
                            api_key=api_key,
                            model="auto",
                            local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                        ),
                    )
            except Exception:
                agent_ctx = Agent.create(
                    AgentOptions(
                        api_key=api_key,
                        model="auto",
                        local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
                    ),
                )

        with agent_ctx as agent:
            if not one_shot:
                kv_set("cursor_task_agent_id", agent.agent_id)
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
    except CursorAgentError as e:
        err = f"Не удалось запустить агента: {e.message}"
        on_text(err)
        return err
    except Exception as e:
        err = f"Сбой при выполнении: {e}"
        on_text(err)
        logger.exception("_stream_agent failed")
        return err
    finally:
        cleanup_cursor_bridge()


def run_ask_streaming(prompt: str, on_text) -> str:
    """Read-only Q&A with streaming."""
    return _stream_agent(_wrap_ask_prompt(prompt), on_text, one_shot=True)


def run_task_streaming(prompt: str, on_text) -> str:
    """Task with code changes; commit/deploy handled by caller."""
    return _stream_agent(_wrap_task_prompt(prompt), on_text, one_shot=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    text = run_ask(" ".join(sys.argv[1:]) or "Say hello and confirm you can access the workspace.")
    print(text)
