"""Curated bug bounty programs relevant to web / JavaScript stack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Platform = Literal["hackerone", "bugcrowd", "intigriti", "immunefi", "hackenproof"]


@dataclass(frozen=True)
class BountyProgram:
    name: str
    platform: Platform
    url: str
    team_handle: str
    focus: str
    notes: str = ""


# Public program pages — verify scope on each platform before testing.
WEB_JS_PROGRAMS: tuple[BountyProgram, ...] = (
    BountyProgram(
        name="Shopify",
        platform="hackerone",
        url="https://hackerone.com/shopify",
        team_handle="shopify",
        focus="E-commerce platform, Liquid, Admin/Storefront GraphQL, Partner apps",
        notes="Primary target: IDOR on Admin API, OAuth apps, checkout logic. Use two dev stores.",
    ),
    BountyProgram(
        name="GitLab",
        platform="hackerone",
        url="https://hackerone.com/gitlab",
        team_handle="gitlab",
        focus="Git hosting, CI/CD, web UI, GraphQL",
        notes="Ruby/JS stack; extensive self-hosted and SaaS scope.",
    ),
    BountyProgram(
        name="Cloudflare",
        platform="hackerone",
        url="https://hackerone.com/cloudflare",
        team_handle="cloudflare",
        focus="CDN, Workers, DNS, dashboard",
        notes="Edge compute and web infrastructure; read scope carefully.",
    ),
    BountyProgram(
        name="Stripe",
        platform="hackerone",
        url="https://hackerone.com/stripe",
        team_handle="stripe",
        focus="Payments API, Dashboard, Connect, webhooks",
        notes="High-quality program; strict rules on live payment data.",
    ),
    BountyProgram(
        name="Node.js",
        platform="hackerone",
        url="https://hackerone.com/nodejs",
        team_handle="nodejs",
        focus="Node.js runtime, npm ecosystem coordination",
        notes="Core runtime and ecosystem; aligns with JS stack skills.",
    ),
    BountyProgram(
        name="Automattic",
        platform="hackerone",
        url="https://hackerone.com/automattic",
        team_handle="automattic",
        focus="WordPress.com, WooCommerce, PHP/JS plugins",
        notes="Large WordPress/JS plugin surface.",
    ),
    BountyProgram(
        name="Slack",
        platform="hackerone",
        url="https://hackerone.com/slack",
        team_handle="slack",
        focus="Workspace apps, APIs, OAuth, web client",
        notes="Enterprise messaging; web and API heavy.",
    ),
    BountyProgram(
        name="Mozilla",
        platform="bugcrowd",
        url="https://bugcrowd.com/mozilla",
        team_handle="mozilla",
        focus="Firefox, web services, MDN-adjacent properties",
        notes="Browser and web platform research.",
    ),
    BountyProgram(
        name="Datadog",
        platform="hackerone",
        url="https://hackerone.com/datadog",
        team_handle="datadog",
        focus="Observability SaaS, agents, dashboard",
        notes="SaaS dashboard and API testing.",
    ),
    BountyProgram(
        name="IKEA",
        platform="intigriti",
        url="https://app.intigriti.com/programs/ikea/ikea/detail",
        team_handle="ikea",
        focus="Retail web apps, APIs, mobile backends",
        notes="Public Intigriti program with web scope.",
    ),
    BountyProgram(
        name="0x / Matcha",
        platform="immunefi",
        url="https://immunefi.com/bug-bounty/0x/",
        team_handle="0x",
        focus="Matcha website, swap API, gasless API, DEX meta-aggregator",
        notes="Payout: USDC on-chain (Immunefi). Web & App tier — IDOR, auth, API abuse. Verify scope before testing.",
    ),
    BountyProgram(
        name="edgeX",
        platform="immunefi",
        url="https://immunefi.com/bug-bounty/edgex/",
        team_handle="edgex",
        focus="Perp/spot trading web UI, REST + WebSocket quote APIs",
        notes="Payout: USDC/USDT via Immunefi. Web & App assets: pro.edgex.exchange, quote/spot APIs. No live fund theft.",
    ),
    BountyProgram(
        name="Backpack",
        platform="hackenproof",
        url="https://hackenproof.com/programs/backpack",
        team_handle="backpack",
        focus="Exchange web client, REST/WebSocket APIs, wallet flows",
        notes="Payout: USDC (Base) via HackenProof balance → crypto wallet. Web & API scope; triaged by HackenProof.",
    ),
    BountyProgram(
        name="GMX",
        platform="immunefi",
        url="https://immunefi.com/bug-bounty/gmx/",
        team_handle="gmx",
        focus="Perp DEX web UI (app.gmx.io), marketing site, trading/API flows",
        notes="Payout: ETH or USDC via Immunefi (max $5M). Websites & Applications: gmx.io, app.gmx.io. No KYC flag on program; verify scope before testing. Added 2026-07-16 (BB-08).",
    ),
    BountyProgram(
        name="1inch Web",
        platform="immunefi",
        url="https://immunefi.com/bug-bounty/1inch-web/",
        team_handle="1inch-web",
        focus="1inch marketing/web surface (1inch.com) — Websites & Applications only",
        notes="Payout: USDC on Ethereum via Immunefi (max $50k web). Dedicated web program (not smart-contract lanes). KYC required for payout. Only listed assets in scope — verify table before testing. Added 2026-07-17 (BB-09).",
    ),
    BountyProgram(
        name="ENS",
        platform="immunefi",
        url="https://immunefi.com/bug-bounty/ens/",
        team_handle="ens",
        focus="ENS Web & App (NextJS): app.ens.domains, ens.domains, metadata.ens.domains + public repos",
        notes="Payout: USDC on Ethereum via Immunefi (web Critical flat $25k; High $5–20k). Track B Websites & Applications; NextJS stack fit. KYC generally not required. ens.dev OOS; no mainnet SC testing without local fork. Verify scope table before testing. Added 2026-07-18 (BB-10).",
    ),
    BountyProgram(
        name="Lido",
        platform="immunefi",
        url="https://immunefi.com/bug-bounty/lido/",
        team_handle="lido",
        focus="Lido Web & App: stake.lido.fi, lido.fi, operators.lido.fi, csm.lido.fi, dao.lido.fi + auxiliary services",
        notes="Payout: USDC/USDS/DAI/USDT on Ethereum via Immunefi (web Critical $50–100k; High $5–50k). KYC not required. PoC required for all web severities. Domains not listed paid at discretion; no mainnet SC testing without local fork. Verify scope table before testing. Added 2026-07-19 (BB-11).",
    ),
    BountyProgram(
        name="Sky",
        platform="immunefi",
        url="https://immunefi.com/bug-bounty/sky/",
        team_handle="sky",
        focus="Sky (MakerDAO) Web & App: app.sky.money, sky.money, vote.sky.money, chainlog.sky.money",
        notes="Payout: DAI or USDS via Immunefi/governance spell (web Critical up to $100k; High $5k). KYC not required. PoC required. vote.makerdao.com Critical-only; chainlog DoS OOS. No mainnet SC testing without local fork. Verify scope table before testing. Added 2026-07-20 (BB-12).",
    ),
)


def program_by_index(index: int) -> BountyProgram:
    """Return a program, wrapping index for rotation."""
    return WEB_JS_PROGRAMS[index % len(WEB_JS_PROGRAMS)]
