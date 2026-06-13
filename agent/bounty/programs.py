"""Curated bug bounty programs relevant to web / JavaScript stack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Platform = Literal["hackerone", "bugcrowd", "intigriti"]


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
        focus="E-commerce platform, Liquid, APIs, merchant apps",
        notes="Strong web/API surface; good fit for JS/Node research.",
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
)


def program_by_index(index: int) -> BountyProgram:
    """Return a program, wrapping index for rotation."""
    return WEB_JS_PROGRAMS[index % len(WEB_JS_PROGRAMS)]
