#!/usr/bin/env bash
# Guard model routing single-source invariants.
set -euo pipefail

SOURCE_HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS_DIR="${HARNESS_DIR:-${SOLAR_HARNESS_DIR:-$SOURCE_HARNESS_DIR}}"
PASS=0
FAIL=0

ok() { PASS=$((PASS + 1)); printf 'ok - %s\n' "$1"; }
not_ok() { FAIL=$((FAIL + 1)); printf 'not ok - %s\n' "$1"; }

assert_file() {
  local path="$1" label="$2"
  [[ -f "$path" ]] && ok "$label" || not_ok "$label: missing $path"
}

assert_contains() {
  local path="$1" needle="$2" label="$3"
  if grep -Fq "$needle" "$path"; then
    ok "$label"
  else
    not_ok "$label: missing '$needle' in $path"
  fi
}

assert_not_contains() {
  local path="$1" needle="$2" label="$3"
  if grep -Fq "$needle" "$path"; then
    not_ok "$label: forbidden '$needle' in $path"
  else
    ok "$label"
  fi
}

assert_file "$HARNESS_DIR/config/model-registry.json" "model registry exists"
assert_file "$HARNESS_DIR/lib/model_registry.py" "model registry helper exists"

assert_contains "$HARNESS_DIR/lib/harness-config.sh" "solar_model_registry()" "harness config reads registry helper"
assert_contains "$HARNESS_DIR/lib/persona-config.sh" "solar_model_alias_canonical" "persona config normalizes through registry"
assert_contains "$HARNESS_DIR/quota-footer.sh" "MODEL_ID" "footer consumes persona model id"
assert_contains "$HARNESS_DIR/integrations/solar-config-server.py" "model_registry_options" "config UI exports registry model options"
assert_contains "$HARNESS_DIR/lib/graph_node_dispatcher.py" "_models_for_pane" "graph dispatcher resolves worker models through registry"
assert_contains "$HARNESS_DIR/solar-harness.sh" "claude_clean_env_prefix" "launcher uses shared clean env prefix"
assert_contains "$HARNESS_DIR/pane-launcher.sh" "prepare_sanitized_claude_settings" "pane launcher sanitizes Claude settings"
assert_contains "$HARNESS_DIR/pane-launcher.sh" "setting-sources" "pane launcher pins setting sources"
assert_contains "$HARNESS_DIR/pane-launcher.sh" "data.pop(\"env\", None)" "pane launcher strips global Claude env overrides"
assert_contains "$HARNESS_DIR/start-incarnation.sh" "prepare_sanitized_claude_settings" "watchdog launcher sanitizes Claude settings"
assert_contains "$HARNESS_DIR/start-incarnation.sh" "setting-sources" "watchdog launcher pins setting sources"
assert_contains "$HARNESS_DIR/start-incarnation.sh" "data.pop(\"env\", None)" "watchdog launcher strips global Claude env overrides"
assert_contains "$HARNESS_DIR/solar-harness.sh" "models_live_route_check" "models doctor checks live pane route"
assert_contains "$HARNESS_DIR/solar-harness.sh" "route:" "main-status exposes live pane route"

assert_not_contains "$HARNESS_DIR/solar-harness.sh" "models set-main <opus|sonnet>" "main model help does not advertise ambiguous bare sonnet"
assert_not_contains "$HARNESS_DIR/solar-harness.sh" "glm,glm,glm,deepseek" "launcher has no legacy DeepSeek lab default"
assert_not_contains "$HARNESS_DIR/integrations/solar-config-server.py" "const modelOptions =" "config UI model options are not const-hardcoded"
assert_not_contains "$HARNESS_DIR/integrations/solar-config-server.py" "deepseek-r1" "config UI does not expose stale DeepSeek R1 option"
assert_not_contains "$HARNESS_DIR/lib/graph_node_dispatcher.py" 'models = ["sonnet", "glm-5.1", "deepseek"]' "graph dispatcher has no title-guessed model list"
assert_contains "$HARNESS_DIR/solar-harness.sh" "models doctor" "models doctor command is advertised"

python3 - "$HARNESS_DIR" <<'PY'
import importlib.util
import json
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
sys.path.insert(0, str(root / "lib"))

from model_registry import load_registry, normalize

reg = load_registry(root / "config" / "model-registry.json")
checks = [
    (normalize(reg, "codex"), "codex-gpt-5.5", "codex canonical"),
    (normalize(reg, "opus"), "claude-opus", "opus canonical"),
    (normalize(reg, "anthropic-sonnet"), "claude-sonnet", "explicit anthropic sonnet canonical"),
    (normalize(reg, "sonnet"), "zhipu-glm-4.7", "bare sonnet remains zhipu lab alias"),
]
for actual, expected, label in checks:
    if actual != expected:
        raise SystemExit(f"{label}: expected {expected}, got {actual}")

config_spec = importlib.util.spec_from_file_location("solar_config_server", root / "integrations" / "solar-config-server.py")
config_mod = importlib.util.module_from_spec(config_spec)
config_spec.loader.exec_module(config_mod)
opts = config_mod.model_registry_options()
model_values = [x["value"] for x in opts["model_options"]]
for required in ("codex", "opus", "anthropic-sonnet"):
    if required not in model_values:
        raise SystemExit(f"config UI model values missing {required}: {model_values}")

os.environ["HARNESS_DIR"] = str(root)
os.environ["SOLAR_HARNESS_SESSION"] = "solar-harness"
dispatcher_spec = importlib.util.spec_from_file_location("graph_node_dispatcher", root / "lib" / "graph_node_dispatcher.py")
dispatcher = importlib.util.module_from_spec(dispatcher_spec)
dispatcher_spec.loader.exec_module(dispatcher)
worker_models = {
    "main_builder": dispatcher._models_for_pane("solar-harness:0.2"),
    "lab1": dispatcher._models_for_pane("solar-harness-lab:0.0"),
    "lab4": dispatcher._models_for_pane("solar-harness-lab:0.3"),
}
if "codex-gpt-5.5" not in worker_models["main_builder"]:
    raise SystemExit(f"main builder not registry-configured Codex: {worker_models['main_builder']}")
if "codex-gpt-5.5" not in worker_models["lab1"]:
    raise SystemExit(f"lab1 not registry-configured Codex: {worker_models['lab1']}")
if "codex-gpt-5.5" not in worker_models["lab4"]:
    raise SystemExit(f"lab4 not registry-configured Codex: {worker_models['lab4']}")

os.environ["SOLAR_MULTI_TASK_OPERATORS"] = str(root / "config" / "physical-operators.json")
runner_spec = importlib.util.spec_from_file_location("multi_task_runner", root / "lib" / "multi_task_runner.py")
runner = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(runner)
default_builder = runner.select_profile({
    "role": "builder",
    "operator_selector": {"task_type": "implementation"},
})
if default_builder.get("operator_id") not in {"mini-codex-gpt55-medium-builder-1", "mini-codex-gpt55-medium-builder-2"}:
    raise SystemExit(f"default implementation builder is not Codex GPT-5.5: {default_builder}")
if default_builder.get("model") != "gpt-5.5":
    raise SystemExit(f"default implementation builder model is not gpt-5.5: {default_builder}")

codex_builder = runner.select_profile({
    "role": "builder",
    "operator_selector": {"provider": "openai", "model": "codex", "task_type": "implementation"},
})
if codex_builder.get("operator_id") not in {"mini-codex-gpt55-medium-builder-1", "mini-codex-gpt55-medium-builder-2"}:
    raise SystemExit(f"explicit Codex builder is not GPT-5.5: {codex_builder}")
if codex_builder.get("model") != "gpt-5.5":
    raise SystemExit(f"explicit Codex builder model is not gpt-5.5: {codex_builder}")

print(json.dumps({
    "ok": True,
    "worker_models": worker_models,
    "default_builder": {
        "operator_id": default_builder.get("operator_id"),
        "model": default_builder.get("model"),
    },
    "codex_builder": {
        "operator_id": codex_builder.get("operator_id"),
        "model": codex_builder.get("model"),
    },
}, ensure_ascii=False))
PY
ok "functional registry guard passed"

printf '=== RESULT: PASS=%d FAIL=%d ===\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]
