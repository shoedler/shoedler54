/**
 * Watch config.yml next to this script and run `ergogen .` on changes.
 */

import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import process from "node:process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// current dir = where the script is
const cwd = __dirname;
const configPath = path.join(cwd, "config.yml");

const DEBOUNCE_MS = 250;

let debounceTimer = null;
let running = false;
let rerunRequested = false;

function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: "inherit", ...opts });
    p.on("exit", (code) =>
      code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`))
    );
    p.on("error", reject);
  });
}

async function build() {
  if (running) {
    rerunRequested = true;
    return;
  }

  running = true;
  rerunRequested = false;

  console.log("\n[watch] running: ergogen .");
  try {
    await run("ergogen", ["."], { cwd });
    console.log("[watch] done");
  } catch (e) {
    console.error("[watch] build failed:", e.message);
  } finally {
    running = false;
    if (rerunRequested) {
      console.log("[watch] rerun requested");
      await build();
    }
  }
}

function scheduleBuild(reason) {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => build().catch(() => {}), DEBOUNCE_MS);
  console.log(`[watch] ${reason}`);
}

console.log(`[watch] watching ${configPath}`);

// fs.watch is edge-triggered and a bit noisy → debounce handles it
fs.watch(cwd, (eventType, filename) => {
  if (!filename) return;
  if (filename === "config.yml") {
    scheduleBuild(`config.yml ${eventType}`);
  }
});

// Optional: initial build
build().catch(() => {});
