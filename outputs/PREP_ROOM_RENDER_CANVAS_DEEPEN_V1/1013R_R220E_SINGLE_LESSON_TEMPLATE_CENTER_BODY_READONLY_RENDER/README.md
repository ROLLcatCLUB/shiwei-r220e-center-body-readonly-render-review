# 1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER

R220E returns to the render line after R201K. It renders the R201K after-fix uploaded-lesson candidate into the R97B center `lesson-body` reading surface as readonly DOM fragments.

## Decision

```text
PASS_AS_CENTER_BODY_READONLY_RENDER_ARTIFACT_NOT_ROUTE_SWITCH
```

This is not a full route switch and not formal apply. It creates center-body render artifacts for review.

## Scope

- Uses R201K after-fix candidate content.
- Renders five samples:
  - `real_downpour_docx` / 下雨啰
  - `numbered_colon_old_shoes` / 旧鞋 / 足下生辉
  - `plain_segment_weaving` / 穿穿编编
  - `table_rain_umbrella` / 雨伞图案设计
  - `minimal_line_fish` / 线条小鱼
- Targets only the center `lesson-body` / `teaching-process` reading surface.
- Does not render right rail, big screen, or bottom Xiaojiao modification surfaces.

## Display Policy

- Top candidate status appears once: `系统候选，需教师确认`.
- Section-level long source labels are compressed into a small `候选` badge.
- Teaching process default view shows:
  - episode title
  - episode goal
  - teacher organization
  - student learning
  - key teacher talk
  - core evidence
- Micro-step, materials, scaffolds, and Xiaojiao hints are folded in `<details>` by default.
- Teacher confirmation items are grouped as must confirm, suggested confirm, and folded diagnostic.

## Boundary

- No new HTML shell.
- No R21/R36 modification.
- No R36/M1/R100-P1 promotion.
- No right rail / big screen model connection.
- No Xiaojiao real modification.
- No field-level editing.
- No formal apply.
- No database / Feishu / memory write.
- No R95.
- No provider/model call.

## Main Files

- `r220e_center_body_render_report.md`
- `r220e_sample_render_matrix.json`
- `r220e_teacher_readable_dom_snapshots/*/lesson_body.html`
- `r220e_static_content_replacement_check.json`
- `r220e_readability_display_policy.md`
- `r220e_source_policy_dom_check.json`
- `r220e_right_rail_out_of_scope_guard.json`
- `validate_1013R_R220E_single_lesson_template_center_body_readonly_render_result.json`

## Validation

All required checks passed:

- five samples rendered to lesson-body
- old static `色彩的渐变` body not residual
- candidate status appears once
- full repeated source label not repeated
- default process core fields present
- micro-step/materials/scaffolds/Xiaojiao folded
- confirmation groups present
- no engineering terms in teacher main
- no source gap as teacher content
- right rail and bottom Xiaojiao out of scope
- no field-level editing
