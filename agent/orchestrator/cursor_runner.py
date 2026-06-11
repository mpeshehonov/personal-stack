"""Cursor SDK agent runner with resume support."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from orchestrator.config import STACK_DIR, load_env_file
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

    Agent, AgentOptions, CursorAgentError, LocalAgentOptions = _ensure_sdk()
    cwd = str(STACK_DIR)

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


def run_daily_agent(context: str, light_mode: bool) -> str:
    mode_note = (
        "LIGHT MODE: skip finance trades and heavy PDF rebuild. Focus on health report and critical site fixes only."
        if light_mode
        else "FULL MODE: site improvements, bounty research, finance analysis."
    )
    prompt = f"""You are the autonomous agent for /opt/personal-stack.

{mode_note}

{context}

Instructions:
1. Check site health; if down, fix and run scripts/redeploy-site.sh
2. Pick at most 1-2 items from site backlog; commit changes to site/
3. Research bug bounty opportunities; draft reports only (never submit)
4. Analyze finance opportunities; output JSON proposals for risk engine
5. Append lessons to agent/memory/lessons/ if you learned something durable
6. Update agent/memory/daily/ today log with sections: Summary, Site, Finance, Bug Bounty, Lessons

Work only inside /opt/personal-stack. Never expose secrets.
"""
    summary = run_cursor_prompt(prompt)
    append_daily_section("Summary", summary[:1500])
    return summary


def run_ask(prompt: str) -> str:
    return run_cursor_prompt(prompt, one_shot=True)


def run_ask_streaming(prompt: str, on_text) -> str:
    """Run one-shot agent with incremental text callbacks. on_text(accumulated: str)."""
    load_env_file(".env.cursor")
    api_key = os.environ.get("CURSOR_API_KEY")
    if not api_key:
        msg = "CURSOR_API_KEY не настроен в secrets/.env.cursor"
        on_text(msg)
        return msg

    Agent, AgentOptions, CursorAgentError, LocalAgentOptions = _ensure_sdk()
    cwd = str(STACK_DIR)
    accumulated = ""

    try:
        with Agent.create(
            AgentOptions(
                api_key=api_key,
                model="auto",
                local=LocalAgentOptions(cwd=cwd, setting_sources=[]),
            ),
        ) as agent:
            run = agent.send(prompt)
            for chunk in run.iter_text():
                accumulated += chunk
                on_text(accumulated)
            result = run.wait()
            final = (result.result or accumulated or "").strip()
            if final and final != accumulated:
                on_text(final)
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
        logger.exception("run_ask_streaming failed")
        return err


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    text = run_ask(" ".join(sys.argv[1:]) or "Say hello and confirm you can access the workspace.")
    print(text)
