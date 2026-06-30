# Paper Compile Checklist Diagnostics

Target: artifacts/autosci/phase19/paper-compile-proof-inputs/paper
Resolved target: /Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/harness/artifacts/autosci/phase19/paper-compile-proof-inputs/paper
Status: completed

| Check | Status | Detail |
| --- | --- | --- |
| target_resolved | ok | Resolved to /Users/jamesyuan/Developer/Github Repos (On Git)/OpenSolar/harness/artifacts/autosci/phase19/paper-compile-proof-inputs/paper |
| latex_source_present | ok | 1 LaTeX source file(s) found. |
| compiled_pdf_present | ok | 1 structurally valid PDF file(s) found. |
| bibliography_present | warn | No .bib files were found. |
| latexmk_available | warn | latexmk was not found on PATH; approved execution may use another allowlisted TeX executor. |
| tex_executor_available | ok | pdflatex=/Library/TeX/texbin/pdflatex, xelatex=/Library/TeX/texbin/xelatex, lualatex=/Library/TeX/texbin/lualatex |
| checklist_requested | ok | Checklist mode was requested. |
| auto_fix_requested | ok | Auto-fix was not requested. |
| compile_execution | ok | Approved executor/runtime evidence verifies LaTeX/PDF compilation. |
| approval_contract_verified | ok | Approval, allowlist, runtime, and before/after evidence are verified. |
| runtime_semantic_verified | ok | Runtime evidence passed compile-specific semantic checks. |
| unconfirmed_marker_scan | ok | No [UNCONFIRMED] markers were found in scanned source files. |
| anonymity_check | ok | Anonymous mode requested and no explicit non-anonymous author blocks were found. |
| page_limit_check | ok | Verified page count 1.0 is within limit 8.0. |
| font_size_check | ok | Verified minimum font size 9.962599754333496 is >= required 9.5. |
| venue_submission_profile | ok | Venue submission profile loaded with source-backed requirements. |
| pdf_inspection | ok | PDF inspection evidence loaded with verified page and font measurements. |
| publication_submission_audit | ok | Publication submission audit evidence verified checklist readiness. |
| publication_submission_boundary | ok | Submission readiness boundary passed. |

## Submission Checks

| Check | Status | Detail |
| --- | --- | --- |
| unconfirmed_marker_scan | ok | No [UNCONFIRMED] markers were found in scanned source files. |
| anonymity_check | ok | Anonymous mode requested and no explicit non-anonymous author blocks were found. |
| page_limit_check | ok | Verified page count 1.0 is within limit 8.0. |
| font_size_check | ok | Verified minimum font size 9.962599754333496 is >= required 9.5. |

## Submission Boundary

- status: submission_ready
- submission_ready: True
- blocking_checks: N/A
- venue_status: venue_submission_ready
- venue_submission_ready: True
- venue_blocking_checks: N/A
- submission_audit_status: submission_audit_ready
- submission_audit_ready: True
- submission_audit_blocking_checks: N/A
- portal_submission_completed: False
- submission_profile_status: loaded
- submission_profile_path: artifacts/autosci/phase19/paper-compile-proof-inputs/submission-profile.json
- pdf_inspection_status: loaded
- pdf_inspection_path: artifacts/autosci/phase19/paper-compile-proof-inputs/pdf-inspection.json
- submission_audit_evidence_status: loaded
- submission_audit_path: artifacts/autosci/phase19/paper-compile-proof-inputs/submission-audit.json

## Files

- latex_files: artifacts/autosci/phase19/paper-compile-proof-inputs/paper/main.tex
- pdf_files: artifacts/autosci/phase19/paper-compile-proof-inputs/paper/main.pdf
- markdown_files: N/A
- bibliography_files: N/A

## Limitations

- Paper compile runtime was verified from supplied approval-gated evidence; this bridge did not execute a TeX executor.
