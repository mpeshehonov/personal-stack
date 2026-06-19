#!/usr/bin/env node
/** Reassign order field in index.json — best projects first, games last. */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const indexPath = path.join(__dirname, "../content/projects/index.json");

const ORDER = [
  "x5-procurement",
  "potalonu-seat-map",
  "sendonate-donations",
  "zodiaclab",
  "nlmk-iron-registration",
  "smartfish-management",
  "citilink-migration",
  "bizone-thread-intelligence",
  "potalonu-tickets",
  "marketplace-nda",
  "in2view",
  "rostelecom-yaga",
  "sbertech-opensearch",
  "smartfish-kkm",
  "smartfish-backend",
  "smartfish-landing",
  "smartfish-bots",
  "stratwise",
  "quan2um",
  "beauty-shop",
  "fitomarket",
  "energosoft",
  "baucenter",
  "specdep",
  "energoshop-workshop",
  "zenit-tickets",
  "aurumline-webview",
  "duckmaster",
  "handstars",
  "it-simulator",
];

const FEATURED = new Set([
  "x5-procurement",
  "potalonu-seat-map",
  "sendonate-donations",
  "zodiaclab",
  "nlmk-iron-registration",
  "smartfish-management",
]);

const projects = JSON.parse(fs.readFileSync(indexPath, "utf8"));
const bySlug = Object.fromEntries(projects.map((p) => [p.slug, p]));

const missing = ORDER.filter((s) => !bySlug[s]);
if (missing.length) {
  console.error("Missing slugs in index.json:", missing.join(", "));
  process.exit(1);
}

const extra = projects.filter((p) => !ORDER.includes(p.slug));
if (extra.length) {
  console.error("Slugs not in ORDER:", extra.map((p) => p.slug).join(", "));
  process.exit(1);
}

const reordered = ORDER.map((slug, i) => ({
  ...bySlug[slug],
  order: i + 1,
  featured: FEATURED.has(slug),
}));

fs.writeFileSync(indexPath, JSON.stringify(reordered, null, 2) + "\n");
console.log("Reordered", reordered.length, "projects");
