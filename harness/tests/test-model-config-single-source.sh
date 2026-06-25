#!/usr/bin/env bash
set -euo pipefail

SOURCE_HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS_DIR="${HARNESS_DIR:-${SOLAR_HARNESS_DIR:-$SOURCE_HARNESS_DIR}}"

pass=0
fail=0

ok() { pass=$((pass + 1)); printf 'ok - %s\n' "$1"; }
not_ok() { fail=$((fail + 1)); printf 'not ok - %s\n' "$1"; }

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if grep -Fq "$needle" <<<"$haystack"; then
    ok "$label"
  else
    not_ok "$label: missing '$needle'"
    printf '%s\n' "$haystack"
  fi
}

source "$HARNESS_DIR/lib/harness-config.sh"

assert_eq() {
  local actual="$1" expected="$2" label="$3"
  if [[ "$actual" == "$expected" ]]; then
    ok "$label"
  else
    not_ok "$label: expected '$expected', got '$actual'"
  fi
}

assert_eq "$(python3 "$HARNESS_DIR/lib/model_registry.py" normalize codex)" "codex-gpt-5.5" "registry resolves codex to Codex GPT-5.5"
assert_eq "$(python3 "$HARNESS_DIR/lib/model_registry.py" normalize opus)" "claude-opus" "registry resolves opus to Claude Opus"
assert_eq "$(python3 "$HARNESS_DIR/lib/model_registry.py" normalize anthropic-sonnet)" "claude-sonnet" "registry resolves explicit Anthropic Sonnet"
assert_eq "$(python3 "$HARNESS_DIR/lib/model_registry.py" normalize sonnet)" "zhipu-glm-4.7" "registry preserves bare sonnet as Zhipu lab alias"
if python3 "$HARNESS_DIR/lib/model_registry.py" validate-main glm >/dev/null 2>&1; then
  not_ok "registry blocks GLM from main screen"
else
  ok "registry blocks GLM from main screen"
fi

matrix="$(solar_lab_builder_matrix)"
assert_eq "$matrix" "codex-gpt-5.5,codex-gpt-5.5,codex-gpt-5.5,codex-gpt-5.5" "config-backed matrix defaults to Codex GPT-5.5"

label="$(solar_lab_builder_matrix_label "$matrix")"
assert_contains "$label" "Codex GPT-5.5" "matrix label shows Codex GPT-5.5"

slot4="$(
  SOLAR_BUILDER_SLOT=lab-builder-4 \
  bash "$HARNESS_DIR/lib/persona-config.sh" --print-config lab-builder
)"
assert_contains "$slot4" "DISPLAY_MODEL='Codex GPT-5.5 (Codex) (lab-builder-4)'" "slot 4 reads config and resolves to Codex GPT-5.5"
assert_contains "$slot4" "BASE_URL=''" "Codex does not use Zhipu/DeepSeek gateway"
assert_contains "$slot4" "MODEL_ID='codex-gpt-5.5'" "slot 4 exposes registry model id"
assert_contains "$slot4" "MODEL_PROVIDER='codex'" "slot 4 exposes Codex provider"

slot1="$(
  SOLAR_BUILDER_SLOT=lab-builder-1 \
  bash "$HARNESS_DIR/lib/persona-config.sh" --print-config lab-builder
)"
assert_contains "$slot1" "MODEL_ID='codex-gpt-5.5'" "slot 1 exposes Codex GPT-5.5 registry model id"

override="$(
  SOLAR_LAB_BUILDER_MODEL_MATRIX=glm,anthropic-sonnet \
  SOLAR_BUILDER_SLOT=lab-builder-2 \
  bash "$HARNESS_DIR/lib/persona-config.sh" --print-config lab-builder
)"
assert_contains "$override" "DISPLAY_MODEL='Claude Sonnet (Anthropic, lab-builder-2)'" "env override remains available for one-off testing"

tmp_cfg="$(mktemp)"
python3 - "$HARNESS_DIR/config/solar-user-config.json" "$tmp_cfg" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
models = data.setdefault("models", {})
for role in ("pm", "planner", "builder", "evaluator"):
    models[role] = "opus"
Path(sys.argv[2]).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
pm_opus="$(SOLAR_USER_CONFIG="$tmp_cfg" bash "$HARNESS_DIR/lib/persona-config.sh" --print-config pm)"
planner_opus="$(SOLAR_USER_CONFIG="$tmp_cfg" bash "$HARNESS_DIR/lib/persona-config.sh" --print-config planner)"
builder_opus="$(SOLAR_USER_CONFIG="$tmp_cfg" bash "$HARNESS_DIR/lib/persona-config.sh" --print-config builder)"
evaluator_opus="$(SOLAR_USER_CONFIG="$tmp_cfg" bash "$HARNESS_DIR/lib/persona-config.sh" --print-config evaluator)"
rm -f "$tmp_cfg"
assert_contains "$pm_opus" "MODEL_FLAG='--model claude-opus-4-8'" "PM reads main config and resolves to Opus"
assert_contains "$pm_opus" "MODEL_ID='claude-opus'" "PM exposes registry model id"
assert_contains "$planner_opus" "MODEL_FLAG='--model claude-opus-4-8'" "planner reads main config and resolves to Opus"
assert_contains "$builder_opus" "MODEL_FLAG='--model claude-opus-4-8'" "builder reads main config and resolves to Opus"
assert_contains "$evaluator_opus" "MODEL_FLAG='--model claude-opus-4-8'" "evaluator reads main config and resolves to Opus"
assert_contains "$pm_opus" "DISPLAY_MODEL='Claude Opus 4.8 (Anthropic)'" "PM display shows configured Opus route"

printf '=== RESULT: PASS=%d FAIL=%d ===\n' "$pass" "$fail"
[[ "$fail" -eq 0 ]]
