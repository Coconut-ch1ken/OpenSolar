---
entity_type: "paper"
entity_id: "paper-skillgen-sample-paper"
title: "SKILLGEN: Verified Inference-Time Agent Skill Synthesis"
run_id: "codex-ingest-source-proof-check"
source_evidence: "artifacts/autosci/runs/codex-ingest-source-proof-check/research_paper.analyzed.json"
managed_by: "solar-autosci-workspace-projector"
---
# SKILLGEN: Verified Inference-Time Agent Skill Synthesis

## Source

- Paper id: `paper-skillgen-sample-paper`
- Source ref: `plugins/autosci/tests/fixtures/skillgen_sample_paper.md`
- Source type: `markdown`
- Parse status: `parsed`
- Evidence: `artifacts/autosci/runs/codex-ingest-source-proof-check/research_paper.analyzed.json`

## Abstract

The paper introduces SKILLGEN, a multi-agent inference-time framework for synthesizing reusable, auditable agent skills from successful and failed trajectories. It emphasizes contrastive induction, candidate verification, and empirical net-effect checks before deployment.

## Analysis

Prepared and parsed SKILLGEN: Verified Inference-Time Agent Skill Synthesis through the Solar AutoSci paper preparation backend and emitted Solar Evidence ABI paper evidence.

### Key Concepts

- paper source preparation
- arXiv source recovery
- Solar Evidence ABI

## Sections

### Abstract

Source anchor: `skillgen_sample_paper.md#abstract`

The paper introduces SKILLGEN, a multi-agent inference-time framework for synthesizing reusable, auditable agent skills from successful and failed trajectories. It emphasizes contrastive induction, candidate verification, and empirical net-effect checks before deployment.

### Method

Source anchor: `skillgen_sample_paper.md#method`

The workflow derives candidate skill procedures from trajectory data, compares success patterns and failure modes, and verifies whether the generated skill improves the base agent without introducing unacceptable regressions.

### Evidence Notes

Source anchor: `skillgen_sample_paper.md#evidence-notes`

This compact markdown fixture is derived from the SkillGen paper for Phase 9 Solar-native ingestion testing.

