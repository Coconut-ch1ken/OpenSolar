# Paper Compile Checklist Diagnostics

Target: /Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/harness/artifacts/autosci/workspace
Resolved target: /Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/harness/artifacts/autosci/workspace
Status: inconclusive

| Check | Status | Detail |
| --- | --- | --- |
| target_resolved | ok | Resolved to /Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/harness/artifacts/autosci/workspace |
| latex_source_present | ok | 3 LaTeX source file(s) found. |
| compiled_pdf_present | warn | No compiled PDF was found. |
| bibliography_present | warn | No .bib files were found. |
| latexmk_available | warn | latexmk was not found on PATH; approved execution may use another allowlisted TeX executor. |
| tex_executor_available | ok | pdflatex=/Library/TeX/texbin/pdflatex, xelatex=/Library/TeX/texbin/xelatex, lualatex=/Library/TeX/texbin/lualatex |
| checklist_requested | ok | Checklist mode was requested. |
| auto_fix_requested | ok | Auto-fix was not requested. |
| compile_execution | warn | The bridge produced compile diagnostics only; it did not run a TeX executor or mutate sources. |
| approval_contract_verified | warn | Approval/runtime contract is incomplete; compile side effects were not executed by this bridge. |
| runtime_semantic_verified | warn | Runtime evidence did not pass compile-specific semantic checks. |

## Files

- latex_files: artifacts/autosci/workspace/raw/tmp/papers/2401-00003.tex, artifacts/autosci/workspace/raw/tmp/papers/skillgen-1.tex, artifacts/autosci/workspace/raw/tmp/papers/skillgen.tex
- pdf_files: N/A
- markdown_files: artifacts/autosci/workspace/README.md, artifacts/autosci/workspace/raw/README.md, artifacts/autosci/workspace/wiki/experiments/exp-001.md, artifacts/autosci/workspace/wiki/experiments/exp-native-001.md, artifacts/autosci/workspace/wiki/graph/context_brief.md, artifacts/autosci/workspace/wiki/graph/open_questions.md, artifacts/autosci/workspace/wiki/ideas/idea-001.md, artifacts/autosci/workspace/wiki/ideas/idea-duplicate-001.md, artifacts/autosci/workspace/wiki/ideas/idea-wiki-discovery-001.md, artifacts/autosci/workspace/wiki/ideas/idea-wiki-discovery-002.md, artifacts/autosci/workspace/wiki/index.md, artifacts/autosci/workspace/wiki/methods/method-001.md, artifacts/autosci/workspace/wiki/outputs/claims-ask-2277d32ac4.md, artifacts/autosci/workspace/wiki/outputs/claims-ask-7a544555ad.md, artifacts/autosci/workspace/wiki/outputs/claims-audit-format-latex-check.md, artifacts/autosci/workspace/wiki/outputs/claims-exp-design-0f52a1d9b5.md, artifacts/autosci/workspace/wiki/outputs/claims-exp-design-9888d7f734.md, artifacts/autosci/workspace/wiki/outputs/claims-exp-eval-c87c02a34a.md, artifacts/autosci/workspace/wiki/outputs/claims-exp-run-8b6d0a2615.md, artifacts/autosci/workspace/wiki/outputs/claims-exp-status-5a6b22da38.md, artifacts/autosci/workspace/wiki/outputs/claims-harness-dollarsurvey.md, artifacts/autosci/workspace/wiki/outputs/claims-harness-dollarsurvey2.md, artifacts/autosci/workspace/wiki/outputs/claims-ideate-95798047c0.md, artifacts/autosci/workspace/wiki/outputs/claims-ideate-b4632dc219.md, artifacts/autosci/workspace/wiki/outputs/claims-manual.md
- bibliography_files: N/A

## Limitations

- Paper compile currently performs a bounded checklist and diagnostics pass only.
- The bridge does not run a TeX executor, mutate source files, or claim PDF compilation without explicit approved execution.
- Approval/runtime evidence contract is not fully verified: approval_ref, allowlist_evidence, before_artifacts, runtime_evidence, after_artifacts
- No compiled PDF was found in the target path.
