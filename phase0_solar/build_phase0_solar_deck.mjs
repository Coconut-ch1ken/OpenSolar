import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { Presentation, PresentationFile } = require("@oai/artifact-tool");

const OUT_DIR = path.resolve("phase0_solar");
const PPTX_PATH = path.join(OUT_DIR, "phase0_on_solar_pipeline.pptx");
const PREVIEW_DIR = path.join(OUT_DIR, "preview");
const MANIFEST_PATH = path.join(OUT_DIR, "deck_manifest.json");

const W = 1280;
const H = 720;

const C = {
  paper: "#F7F5EF",
  ink: "#18212B",
  muted: "#5B6470",
  line: "#D8D2C6",
  green: "#007F68",
  amber: "#C47A2C",
  red: "#B33A3A",
  blue: "#245C96",
  paleGreen: "#DDEFE9",
  paleAmber: "#F3E5D2",
  paleBlue: "#DDE8F3",
  white: "#FFFFFF",
  transparent: "#00000000",
};

const fonts = {
  title: "Aptos Display",
  body: "Aptos",
  mono: "Aptos Mono",
};

const notes = {
  cover: `This deck introduces the Phase 0 on Solar pipeline. The core idea is moving the current paper-specific reproduction workflow into Solar as a reusable capability. Solar should receive a paper, repository, objective, and budget, then coordinate claim extraction, benchmark contracts, execution or replay, evidence mapping, verdict comparison, reporting, and final verification. The important distinction to emphasize is that this is not a new executor. It is a workflow migration that reuses Solar Harness for intake, routing, physical operators, benchmark execution, evidence storage, and gates.`,
  why: `Phase 0 is needed because paper claims often mix natural-language statements, tables, benchmark setup, model routes, code instructions, and result interpretation. Without a Solar-native pipeline, every verification run becomes a custom manual process. Solar gives us a standard capability boundary, reusable operators, artifact traces, and verifier gates. The highest-risk semantic issue is separating claim verdict from execution readiness. A run path being ready means we can run it; it does not mean the paper claim is reproduced.`,
  architecture: `This is the target architecture. The user submits a paper, repository, and verification objective. Solar intake packages that request. The new logical operator, ResearchClaimVerifier, coordinates domain work but delegates execution to existing physical operators and BenchmarkRunner. Evidence is parsed into explicit metrics and linked to claims. The comparator writes claim-level verdicts, and the final verifier gate decides whether the report is acceptable. Harness internals such as capsule resolution, routing, leases, guard/resource attachment, and result envelopes are intentionally hidden from the presentation workflow.`,
  workflow: `This slide is the high-level workflow used for the rest of the presentation. It compresses the full implementation plan into ten business steps. Setup happens once. Each paper then moves from intake, to evidence ingestion, to claim extraction, to contract writing, to preflight, to execution or replay, to evidence mapping, to comparison, and finally report verification. The two human gates are contract approval and execution approval. Blocked paths should return to the relevant earlier step rather than continuing with guessed evidence.`,
};

const stepNotes = [
  {
    id: 0,
    title: "One-time setup",
    subtitle: "Teach Solar what Phase 0 means.",
    tool: "capability_capsules.py, logical-operators.json, existing physical operators",
    add: "cap.phase0-claim-verification, ResearchClaimVerifier, schemas, comparator, golden fixture",
    outputs: "capsule, registry entry, logical binding, schema module, tests",
    failure: "Missing setup blocks the pipeline before runtime dispatch.",
    notes: `Step 0 is not repeated for every paper. It installs the Phase 0 domain layer into Solar. The capability capsule declares inputs, outputs, invariants, effects, guard/resource needs, and verifier conditions. The logical operator ResearchClaimVerifier gives Solar a model-neutral routing label. The schemas define BenchmarkClaim, BenchmarkContract, ObservedMetric, ClaimComparison, Phase0VerdictStatus, ExecutionReadinessStatus, HumanReviewDecision, Phase0RunManifest, Phase0EvidenceMap, and Phase0VerificationSummary. The comparator enforces verdict policy. The golden fixture from AI4Research-B ensures that the known SkillGen result remains not_reproduced at paper level and blocked for the full paper claim.`,
  },
  {
    id: 1,
    title: "Intake paper verification request",
    subtitle: "Turn a user request into a Solar task.",
    tool: "scripts/solar-codex-intake.sh, core/harness/submitCoreToHarness()",
    add: "Pipeline request payload: paper, repo, objective, target claims, budget",
    outputs: "verification_request.json, requirement_ir.json",
    failure: "Missing paper/repo/budget returns to user before claim work starts.",
    notes: `Step 1 packages the user's request into a structured Solar task. The user should provide the paper or paper path, the official repository or source code path, the verification objective, target scope, and budget constraints. Solar intake should preserve source metadata and route the request through existing Core-to-Harness intake. This step is not about verifying claims yet. It only decides whether the request is complete enough to start the pipeline.`,
  },
  {
    id: 2,
    title: "Ingest paper and repo evidence",
    subtitle: "Collect the evidence base before extracting claims.",
    tool: "Solar knowledge/QMD/MinerU path, ResearchScout, ResearchSynthesizer, EvidenceItem, CitationSpan",
    add: "Source map over paper sections, tables, appendix, repo files, configs, prior artifacts",
    outputs: "source_map.json, paper_evidence.json, repo_evidence.json",
    failure: "Missing official source marks affected claims blocked or not_testable; no guessing.",
    notes: `Step 2 reads the paper and codebase into an evidence graph. The paper side includes abstract, method, experimental setup, tables, figures, appendix, and any claimed benchmark metrics. The repo side includes README, scripts, configs, data split instructions, model/provider settings, and official reproduction commands. Prior AI4Research-B artifacts may be linked as context or golden fixture evidence. The output must be source-addressable so later claims can cite exact paper or artifact locations.`,
  },
  {
    id: 3,
    title: "Extract benchmark claims",
    subtitle: "Convert paper statements into structured claims.",
    tool: "Research Claim, ClaimEvidenceLink, EvidenceItem",
    add: "BenchmarkClaim: metric, dataset, split, config, expected value, tolerance",
    outputs: "paper_claims.json, claim_evidence_links.json",
    failure: "Ambiguous or non-benchmarkable claims go to human review.",
    notes: `Step 3 identifies claims that can be verified by benchmarks or artifact inspection. A benchmark claim must name the metric, dataset, split, configuration, expected value or direction, tolerance, and paper location. Claims that are broad or aggregate, such as full Table 1 average gains, must remain aggregate claims and cannot be satisfied by one smoke run. Non-benchmarkable statements can be marked out_of_scope or not_testable rather than forced into a fake metric.`,
  },
  {
    id: 4,
    title: "Write and approve benchmark contracts",
    subtitle: "Turn each claim into an executable check.",
    tool: "BenchmarkRunRequest, BenchmarkRunPlan, BenchmarkAdapter.plan(), VerifierLite",
    add: "BenchmarkContract, HumanReviewDecision",
    outputs: "benchmark_contracts.json, contract_review.json",
    failure: "Rejected/unclear contracts return to claim extraction; no execution before approval.",
    notes: `Step 4 translates claims into contracts. A contract defines the runnable target, required artifacts, metric definition, aggregation rule, tolerance, comparison logic, and approval state. If exact paper splits or configs are missing, the contract may use a reconstructed path, but that path must carry deviation notes. Reconstructed evidence can support at most partially_reproduced unless paper-equivalence is proven. Human review is important here because a wrong contract will produce misleading verdicts even if the benchmark runs successfully.`,
  },
  {
    id: 5,
    title: "Preflight and approve execution",
    subtitle: "Check whether the run path is operationally safe and ready.",
    tool: "BenchmarkDoctor, BenchmarkAdapter.doctor(), BenchmarkRunPlan, VerificationGate.check_destructive_action()",
    add: "ExecutionReadinessStatus, provider/cost policy, command approval",
    outputs: "execution_readiness.json, benchmark_doctor.json, approved_command_plan.json, command_approval.json",
    failure: "Dependency/model/API failures affect readiness only; readiness cannot upgrade claim verdict.",
    notes: `Step 5 checks the environment before running commands. It asks whether dependencies are installable, data is available, model/provider routes are usable, commands are safe, and budget is approved. This creates execution_readiness_status. The key rule is that readiness is not reproduction evidence. If a reconstructed adapter is ready, that only means we can execute it. It does not mean the paper claim is supported. External APIs, local model use, network access, or destructive shell actions require explicit approval or a dry-run path.`,
  },
  {
    id: 6,
    title: "Run benchmark or replay fixture",
    subtitle: "Produce observed evidence without inventing it.",
    tool: "BenchmarkRunner, BenchmarkAdapter.run(), BenchmarkRunResult, existing physical operators",
    add: "AI4Research-B adapter/replay runner; optional real benchmark adapter",
    outputs: "benchmark_run_result.json, stdout/stderr, raw artifacts",
    failure: "Preserve failed logs. Provider/API failures are readiness blockers; negative results stay not_reproduced.",
    notes: `Step 6 either executes approved commands or replays the completed AI4Research-B Phase 0 artifacts as a golden fixture. For live runs, BenchmarkRunner and existing physical operators should be used rather than creating a new executor. For migration testing, replay is enough to verify schema, evidence mapping, and comparator behavior. If a command fails, timeout occurs, provider returns 402, or a model route is missing, preserve the logs and classify the issue correctly. Negative executed evidence is still valid evidence and should remain not_reproduced.`,
  },
  {
    id: 7,
    title: "Parse metrics and map evidence",
    subtitle: "Convert raw run artifacts into claim-linked evidence.",
    tool: "BenchmarkAdapter.parse_result(), BenchmarkRunResult.artifacts, EvidenceItem, ClaimEvidenceLink",
    add: "ObservedMetric, Phase0RunManifest, Phase0EvidenceMap",
    outputs: "parsed_observed_results.json, run_manifest.json, evidence_map.json",
    failure: "Low-confidence metrics or broken evidence links block comparison.",
    notes: `Step 7 parses logs, result JSON, stdout/stderr, verification summaries, and artifact files into ObservedMetric records. Every observed metric must cite source artifacts and carry parser confidence. The run manifest ties a run id to its logs and artifacts. The evidence map ties paper claim, benchmark contract, run id, observed metric ids, paper evidence, run evidence, and limitations together. If any link breaks, the later verdict should fail rather than silently proceed.`,
  },
  {
    id: 8,
    title: "Compare claim vs observation",
    subtitle: "Assign verdicts only from evidence.",
    tool: "Evidence alignment/evaluator patterns",
    add: "ClaimComparison, Phase0VerdictStatus, comparator policy",
    outputs: "claim_comparison.json",
    failure: "No verdict without evidence ids. Smoke/reconstructed evidence cannot upgrade aggregate claims.",
    notes: `Step 8 is the semantic core. The comparator evaluates observed metrics against the benchmark contract and assigns claim_verdict_status. Allowed verdicts include reproduced, partially_reproduced, not_reproduced, not_testable, failed_to_run, blocked, and out_of_scope. The comparator must preserve execution_readiness_status separately. It must reject any attempt to mark a claim reproduced or partially_reproduced based only on plans, adapter readiness, downloaded repos, or command availability. One matrix entry cannot upgrade an aggregate Table 1 claim.`,
  },
  {
    id: 9,
    title: "Report, verify, and accept",
    subtitle: "Produce a gated final result and preserve trace.",
    tool: "ResearchSynthesizer, ReportAST, Verifier, VerifierLite, evaluate_final_closeout(), VerificationGate",
    add: "Phase0VerificationSummary, report template, golden fixture assertions",
    outputs: "phase0_verification_report.md, phase0_verification_summary.json, eval_json, accepted trace",
    failure: "Verifier rejects unsupported paper-level status or readiness-as-reproduction errors.",
    notes: `Step 9 generates the final report and summary, then sends them through verifier gates. The report must cite evidence ids, explain limitations, and derive paper-level status from claim-level verdicts. The golden fixture should preserve the known high-level conclusion from AI4Research-B: paper_level_status not_reproduced, full_paper_claim_status blocked, with counts partially_reproduced=3, blocked=7, not_reproduced=2. The final gate should reject unsupported paper-level claims, missing evidence, same-actor review risks, and any conflation of readiness with reproduction.`,
  },
];

function addShape(slide, { x, y, w, h, fill = C.transparent, line = C.transparent, lw = 0, radius = 0, name }) {
  return slide.shapes.add({
    geometry: radius ? "roundRect" : "rect",
    name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { fill: line, width: lw, style: "solid" },
  });
}

function addText(slide, text, { x, y, w, h, size = 24, color = C.ink, bold = false, typeface = fonts.body, align = "left", valign = "top", fill = C.transparent, line = C.transparent, insets = { left: 0, right: 0, top: 0, bottom: 0 } }) {
  const shape = addShape(slide, { x, y, w, h, fill, line, lw: line === C.transparent ? 0 : 1 });
  shape.text = text;
  shape.text.fontSize = size;
  shape.text.color = color;
  shape.text.bold = bold;
  shape.text.typeface = typeface;
  shape.text.alignment = align;
  shape.text.verticalAlignment = valign;
  shape.text.insets = insets;
  return shape;
}

function bg(slide) {
  addShape(slide, { x: 0, y: 0, w: W, h: H, fill: C.paper });
  addShape(slide, { x: 0, y: 0, w: 18, h: H, fill: C.green });
  addShape(slide, { x: 18, y: 0, w: 5, h: H, fill: C.amber });
}

function header(slide, kicker, title, n) {
  addText(slide, kicker.toUpperCase(), { x: 64, y: 34, w: 250, h: 24, size: 12, color: C.green, bold: true, typeface: fonts.mono, valign: "middle" });
  addText(slide, title, { x: 64, y: 62, w: 900, h: 68, size: 34, color: C.ink, bold: true, typeface: fonts.title });
  addShape(slide, { x: 64, y: 140, w: 1060, h: 1.2, fill: C.line });
  addText(slide, String(n).padStart(2, "0"), { x: 1168, y: 40, w: 48, h: 30, size: 14, color: C.muted, typeface: fonts.mono, align: "right" });
}

function bullet(slide, text, x, y, w, accent = C.green) {
  addShape(slide, { x, y: y + 8, w: 8, h: 8, fill: accent });
  addText(slide, text, { x: x + 20, y, w, h: 46, size: 19, color: C.ink, typeface: fonts.body });
}

function note(slide, text) {
  slide.speakerNotes.setText(text);
}

const workflowNodes = [
  { key: "A", step: 0, label: "One-time\nsetup" },
  { key: "B", step: 1, label: "Request\ncompilation" },
  { key: "C", step: 2, label: "Paper/repo\nevidence" },
  { key: "D", step: 3, label: "Claim\nextraction" },
  { key: "E", step: 4, label: "Contracts\ngeneration" },
  { key: "F", step: 4, label: "Human\nreview", decision: true },
  { key: "G", step: 5, label: "Preflight +\ncommand plan" },
  { key: "H", step: 5, label: "Execution\napproved?", decision: true },
  { key: "I", step: 6, label: "Run/replay\nevidence" },
  { key: "J", step: 7, label: "Parse + map\nevidence" },
  { key: "K", step: 8, label: "Compare\nverdicts" },
  { key: "L", step: 9, label: "Report +\nverifier gate" },
  { key: "M", step: 9, label: "Accepted\ntrace" },
];

function flowFill(node, highlighted) {
  if (highlighted) return C.green;
  if (node.decision) return C.paleAmber;
  if (node.step <= 1) return C.paleBlue;
  if (node.step <= 4) return C.paleGreen;
  if (node.step <= 7) return C.paleAmber;
  return "#E8DFE8";
}

const blockedRoutes = [
  { step: 4, key: "F", label: "no: revise contracts" },
  { step: 5, key: "H", label: "no: safer command" },
  { step: 9, key: "L", label: "fail: revise report" },
];

function drawArrowToBlocked(slide, source, blocked, lineY, label) {
  const startY = source.y + 4;
  if (lineY > startY) {
    addShape(slide, { x: source.x - 1, y: startY, w: 2, h: lineY - startY, fill: C.red });
  }
  const endX = blocked.x - 12;
  const startX = Math.min(source.x, endX - 12);
  addShape(slide, { x: startX, y: lineY, w: Math.max(8, endX - startX), h: 2, fill: C.red });
  addText(slide, ">", { x: endX - 4, y: lineY - 9, w: 12, h: 16, size: 12, color: C.red, bold: true, align: "center", valign: "middle" });
  addText(slide, label, { x: Math.min(startX + 8, blocked.x - 120), y: lineY - 16, w: 120, h: 12, size: 7.2, color: C.red, bold: true, align: "center" });
}

function drawWorkflowRail(slide, currentStep, { x = 40, y = 158, width = 1198, compact = true, blockedMode = "current" } = {}) {
  const gap = compact ? 8 : 10;
  const currentWidth = compact ? 104 : 94;
  const normalWidth = compact ? 66 : 78;
  const widths = workflowNodes.map((node) => (node.step === currentStep ? currentWidth : normalWidth));
  const totalWidth = widths.reduce((a, b) => a + b, 0) + gap * (workflowNodes.length - 1);
  let cursor = x + Math.max(0, (width - totalWidth) / 2);
  const centers = {};
  workflowNodes.forEach((node, i) => {
    const highlighted = node.step === currentStep;
    const w = widths[i];
    const h = highlighted ? 52 : 34;
    const top = y + (highlighted ? 0 : 9);
    const border = highlighted ? C.green : C.line;
    const fill = flowFill(node, highlighted);
    if (i > 0) {
      addShape(slide, { x: cursor - gap + 1, y: y + 25, w: gap - 2, h: 3, fill: highlighted ? C.green : C.line });
    }
    addShape(slide, { x: cursor, y: top, w, h, fill, line: border, lw: highlighted ? 2 : 1 });
    addText(slide, node.label, {
      x: cursor + 4,
      y: top + (highlighted ? 8 : 6),
      w: w - 8,
      h: h - 10,
      size: highlighted ? 10.5 : 7.8,
      color: highlighted ? C.white : C.ink,
      bold: true,
      align: "center",
      valign: "middle",
    });
    centers[node.key] = { x: cursor + w / 2, y: top + h };
    cursor += w + gap;
  });
  const branchY = y + 75;
  const blocked = { x: x + width - 116, y: branchY - 5, w: 96, h: 26 };
  const routes = blockedMode === "all" ? blockedRoutes : blockedRoutes.filter((route) => route.step === currentStep);
  routes.forEach((route, index) => {
    const source = centers[route.key];
    if (source) {
      const offset = blockedMode === "all" ? index * 18 - 12 : 0;
      drawArrowToBlocked(slide, source, blocked, branchY + 8 + offset, route.label);
    }
  });
  addShape(slide, { x: blocked.x, y: blocked.y, w: blocked.w, h: blocked.h, fill: "#F3DADA", line: C.red, lw: 1 });
  addText(slide, "Blocked / revise", { x: blocked.x + 5, y: blocked.y + 7, w: blocked.w - 10, h: 12, size: 7.8, color: C.red, bold: true, align: "center", valign: "middle" });
  return { height: 100, centers };
}

function tableCell(slide, text, { x, y, w, h, fill, line = C.line, size = 11.2, color = C.ink, bold = false, align = "left", valign = "top" }) {
  addShape(slide, { x, y, w, h, fill, line, lw: 1 });
  addText(slide, text, {
    x: x + 8,
    y: y + 8,
    w: w - 16,
    h: h - 14,
    size,
    color,
    bold,
    align,
    valign,
    insets: { left: 2, right: 2, top: 2, bottom: 2 },
  });
}

function drawStepTableRow(slide, step, y = 332) {
  const x0 = 42;
  const widths = [48, 148, 274, 244, 226, 252];
  const headers = ["Step", "Workflow step", "Module/tool used", "New tools", "Main outputs", "Gate / error handling"];
  const values = [String(step.id), step.title, step.tool, step.add, step.outputs, step.failure];
  let x = x0;
  headers.forEach((header, i) => {
    tableCell(slide, header, {
      x,
      y,
      w: widths[i],
      h: 34,
      fill: C.green,
      line: C.green,
      size: i === 0 ? 10.6 : 10,
      color: C.white,
      bold: true,
      align: i === 0 ? "center" : "left",
      valign: "middle",
    });
    x += widths[i];
  });
  x = x0;
  values.forEach((value, i) => {
    tableCell(slide, value, {
      x,
      y: y + 34,
      w: widths[i],
      h: 220,
      fill: i % 2 ? C.white : "#FBFAF7",
      size: i === 0 ? 23 : i === 1 ? 14.2 : 11.1,
      color: C.ink,
      bold: i <= 1,
      align: i === 0 ? "center" : "left",
      valign: i === 0 ? "middle" : "top",
    });
    x += widths[i];
  });
  addText(slide, "Source row: AI4Research-B/migration/adapt_skeleton.md", { x: x0, y: y + 270, w: 420, h: 16, size: 8.5, color: C.muted, typeface: fonts.mono });
}

function cover(p) {
  const slide = p.slides.add();
  bg(slide);
  addText(slide, "PHASE 0 ON SOLAR", { x: 68, y: 58, w: 400, h: 34, size: 14, color: C.green, bold: true, typeface: fonts.mono });
  addText(slide, "Paper-to-Claim Verification Pipeline", { x: 68, y: 126, w: 820, h: 150, size: 58, color: C.ink, bold: true, typeface: fonts.title });
  addText(slide, "A Solar-native workflow for extracting paper claims, proving them with benchmark evidence, and gating final verdicts.", { x: 72, y: 306, w: 690, h: 74, size: 23, color: C.muted });
  const labels = ["claim", "contract", "run", "evidence", "verdict"];
  labels.forEach((l, i) => {
    const x = 92 + i * 204;
    addShape(slide, { x, y: 506, w: 132, h: 50, fill: i % 2 ? C.paleAmber : C.paleGreen, line: C.line, lw: 1 });
    addText(slide, l, { x, y: 518, w: 132, h: 26, size: 18, bold: true, align: "center", valign: "middle" });
    if (i < labels.length - 1) addShape(slide, { x: x + 146, y: 529, w: 36, h: 3, fill: C.green });
  });
  addText(slide, "Source: AI4Research-B migration/adapt_skeleton.md", { x: 72, y: 650, w: 620, h: 20, size: 12, color: C.muted });
  note(slide, notes.cover);
}

function why(p) {
  const slide = p.slides.add();
  bg(slide);
  header(slide, "Why", "Solar turns Phase 0 from bespoke reproduction into a gated capability", 2);
  const cards = [
    ["Standardize", "Paper reading, repo inspection, benchmark execution, metric parsing, and verdict writing become one repeatable workflow.", C.paleBlue],
    ["Evidence discipline", "Every claim verdict must cite paper evidence, run artifacts, parsed metrics, and limitations.", C.paleGreen],
    ["Replayability", "The completed AI4Research-B Phase 0 paper becomes a golden fixture for regression checks.", C.paleAmber],
  ];
  cards.forEach((c, i) => {
    const x = 72 + i * 384;
    addShape(slide, { x, y: 190, w: 330, h: 260, fill: c[2], line: C.line, lw: 1 });
    addText(slide, c[0], { x: x + 24, y: 214, w: 270, h: 34, size: 28, bold: true, typeface: fonts.title });
    addText(slide, c[1], { x: x + 24, y: 276, w: 270, h: 112, size: 20, color: C.ink });
  });
  addShape(slide, { x: 100, y: 506, w: 1010, h: 72, fill: C.white, line: C.green, lw: 2 });
  addText(slide, "Critical invariant: execution_readiness_status can never upgrade claim_verdict_status.", { x: 126, y: 528, w: 960, h: 28, size: 24, bold: true, color: C.green, valign: "middle" });
  note(slide, notes.why);
}

function architecture(p) {
  const slide = p.slides.add();
  bg(slide);
  header(slide, "Architecture", "The new layer is domain semantics, not a new executor", 3);
  const boxes = [
    ["Paper + repo + objective", "User request"],
    ["Solar intake", "Harness request package"],
    ["ResearchClaimVerifier", "New logical operator"],
    ["BenchmarkRunner", "Existing execution path"],
    ["Evidence-backed verdict", "Comparator + report"],
    ["Verifier gate", "Solar acceptance"],
  ];
  boxes.forEach((b, i) => {
    const x = 78 + (i % 3) * 360;
    const y = 194 + Math.floor(i / 3) * 190;
    const fill = i === 2 ? C.paleGreen : i === 3 ? C.paleAmber : C.white;
    addShape(slide, { x, y, w: 292, h: 100, fill, line: C.line, lw: 1 });
    addText(slide, b[0], { x: x + 18, y: y + 20, w: 254, h: 30, size: 22, bold: true, typeface: fonts.title });
    addText(slide, b[1], { x: x + 18, y: y + 58, w: 254, h: 24, size: 16, color: C.muted });
    if (i % 3 < 2) addShape(slide, { x: x + 306, y: y + 48, w: 44, h: 4, fill: C.green });
  });
  addShape(slide, { x: 214, y: 312, w: 4, h: 54, fill: C.green });
  addShape(slide, { x: 574, y: 312, w: 4, h: 54, fill: C.green });
  addShape(slide, { x: 934, y: 312, w: 4, h: 54, fill: C.green });
  addText(slide, "Harness internally handles capsule resolution, routing, leases, inbox/result files, and traces.", { x: 88, y: 610, w: 980, h: 30, size: 18, color: C.muted });
  note(slide, notes.architecture);
}

function workflow(p) {
  const slide = p.slides.add();
  bg(slide);
  header(slide, "Workflow", "The adapt_skeleton flow is the source path for every step slide", 4);
  addText(slide, "The next 10 slides keep this full path visible, enlarge the current step, and paste the matching source row below it.", { x: 72, y: 154, w: 1000, h: 28, size: 20, color: C.muted });
  drawWorkflowRail(slide, null, { x: 44, y: 234, width: 1188, compact: false, blockedMode: "all" });
  addShape(slide, { x: 106, y: 394, w: 960, h: 76, fill: C.white, line: C.green, lw: 2 });
  addText(slide, "Human review and execution approval are explicit gates; rejection or verifier failure returns to Blocked / revise instead of fabricating evidence.", { x: 132, y: 414, w: 908, h: 34, size: 20, color: C.ink, bold: true, align: "center", valign: "middle" });
  addText(slide, "Harness internals are still omitted: capsule resolution, routing, leases, inbox/result envelopes, guard/resource attachment, accepted artifact records, and sprint traces.", { x: 96, y: 548, w: 1010, h: 42, size: 17, color: C.muted, align: "center" });
  note(slide, notes.workflow);
}

function stepSlide(p, step, slideNo) {
  const slide = p.slides.add();
  bg(slide);
  header(slide, `Step ${step.id}`, step.title, slideNo);
  addText(slide, step.subtitle, { x: 64, y: 145, w: 850, h: 28, size: 19, color: C.muted, typeface: fonts.title });
  drawWorkflowRail(slide, step.id, { x: 38, y: 190, width: 1200, compact: true, blockedMode: "all" });
  addText(slide, "Corresponding workflow table row", { x: 42, y: 306, w: 430, h: 18, size: 11, color: C.green, bold: true, typeface: fonts.mono });
  drawStepTableRow(slide, step, 330);
  note(slide, step.notes);
}

function reuse(p) {
  const slide = p.slides.add();
  bg(slide);
  header(slide, "Boundary", "Reuse the Solar runtime; add only the Phase 0 domain layer", 15);
  const rows = [
    ["Runtime", "Harness intake, routing, leases, inbox/result files", "Phase 0 task envelope fields"],
    ["Operators", "Existing physical operators, BenchmarkRunner, Verifier", "ResearchClaimVerifier logical operator"],
    ["Evidence", "EvidenceItem, Claim, ClaimEvidenceLink, CitationSpan", "BenchmarkClaim, ObservedMetric, EvidenceMap"],
    ["Verdict", "Evaluator and verification gate patterns", "ClaimComparison and comparator policy"],
    ["Regression", "Existing test harness", "Golden fixture from AI4Research-B Phase 0"],
  ];
  const x0 = 80, y0 = 180, widths = [180, 460, 430];
  ["Category", "Reuse from Solar", "Add for Phase 0"].forEach((h, i) => {
    addShape(slide, { x: x0 + widths.slice(0, i).reduce((a, b) => a + b, 0), y: y0, w: widths[i], h: 48, fill: C.green, line: C.green, lw: 1 });
    addText(slide, h, { x: x0 + widths.slice(0, i).reduce((a, b) => a + b, 0) + 14, y: y0 + 14, w: widths[i] - 28, h: 20, size: 16, color: C.white, bold: true });
  });
  rows.forEach((r, ri) => {
    const y = y0 + 48 + ri * 70;
    r.forEach((txt, ci) => {
      const x = x0 + widths.slice(0, ci).reduce((a, b) => a + b, 0);
      addShape(slide, { x, y, w: widths[ci], h: 70, fill: ri % 2 ? C.white : "#FBFAF7", line: C.line, lw: 1 });
      addText(slide, txt, { x: x + 14, y: y + 15, w: widths[ci] - 28, h: 38, size: ci === 0 ? 18 : 16, bold: ci === 0, color: C.ink });
    });
  });
  addText(slide, "MVP rule: no new physical operator, scheduler path, or ChatGPT-specific identity unless reuse fails.", { x: 100, y: 602, w: 1000, h: 30, size: 21, bold: true, color: C.red, align: "center" });
  note(slide, `The final slide defines the implementation boundary. The deck should leave the audience with a simple message: Phase 0 on Solar is a workflow migration, not a new executor. We reuse Solar's runtime, operators, benchmark primitives, evidence schemas, and verification gates. We add only what Solar lacks: the ResearchClaimVerifier logical operator, the capability capsule, Phase 0 claim/contract/metric/comparison schemas, comparator policy, and golden fixture tests. The MVP should keep the workflow inside one logical operator and delegate benchmark execution to BenchmarkRunner or a BenchmarkAdapter-compatible wrapper.`);
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  cover(presentation);
  why(presentation);
  architecture(presentation);
  workflow(presentation);
  stepNotes.forEach((s, i) => stepSlide(presentation, s, i + 5));
  reuse(presentation);
  const previews = [];
  for (let i = 0; i < presentation.slides.count; i += 1) {
    const slide = presentation.slides.getItem(i);
    const blob = await presentation.export({ slide, format: "png", scale: 0.6 });
    const buffer = Buffer.from(await blob.arrayBuffer());
    const previewPath = path.join(PREVIEW_DIR, `slide-${String(i + 1).padStart(2, "0")}.png`);
    await fs.writeFile(previewPath, buffer);
    previews.push(previewPath);
  }
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(PPTX_PATH);
  const stat = await fs.stat(PPTX_PATH);
  await fs.writeFile(MANIFEST_PATH, JSON.stringify({ pptx: PPTX_PATH, bytes: stat.size, slideCount: presentation.slides.count, previews }, null, 2) + "\n");
  console.log(JSON.stringify({ pptx: PPTX_PATH, bytes: stat.size, slideCount: presentation.slides.count }, null, 2));
}

main().catch((err) => {
  console.error(err.stack || err.message || String(err));
  process.exit(1);
});
