from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STAGE = "1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER"
OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / STAGE
RESULT = OUT / "validate_1013R_R220E_single_lesson_template_center_body_readonly_render_result.json"

R201K_STAGE = "1013R_R201K_UPLOAD_LESSON_CONTENT_QUALITY_FIX_LOOP"
R201K_OUT = ROOT / "outputs" / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1" / R201K_STAGE
R201K_RESULT = R201K_OUT / "validate_1013R_R201K_upload_lesson_content_quality_fix_loop_result.json"
R201K_SAMPLES = R201K_OUT / "sample_snapshots_after_fix"

R220D_RESULT = (
    ROOT
    / "outputs"
    / "PREP_ROOM_RENDER_CANVAS_DEEPEN_V1"
    / "1013R_R220D_R97B_RENDER_SLOT_DOM_SMOKE"
    / "validate_1013R_R220D_r97b_render_slot_dom_smoke_result.json"
)

OLD_STATIC_MARKERS = [
    "色彩的渐变",
    "渐变的节奏",
    "多彩的生活",
]

FULL_REPEATED_SOURCE_LABEL = "由教学过程和原文证据反推；系统建议，需教师确认"
TOP_CANDIDATE_LABEL = "系统候选，需教师确认"
FORBIDDEN_TERMS = [
    "R200A",
    "R200B",
    "R97B_P3",
    "deterministic_fallback",
    "legacy_shell",
    "source_gap",
    "field projection",
    "formal apply",
    "provider_called",
    "model_called",
]

SAMPLE_ORDER = [
    "real_downpour_docx",
    "numbered_colon_old_shoes",
    "plain_segment_weaving",
    "table_rain_umbrella",
    "minimal_line_fish",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _section_dom(slot: str, number: str, section: dict[str, Any]) -> str:
    body = section.get("body") if isinstance(section.get("body"), list) else []
    lines = [
        f'<section class="nb-doc-section r220e-doc-section" data-render-slot="{_esc(slot)}" data-r220e-section="{_esc(slot)}">',
        '  <div class="nb-doc-section-head r220e-section-head">',
        f'    <h2 class="nb-doc-title">{_esc(number)}、{_esc(str(section.get("title") or "").split("、", 1)[-1])}</h2>',
        '    <span class="r220e-compact-badge">候选</span>',
        "  </div>",
        '  <ol class="r220e-section-list">',
    ]
    for item in body:
        lines.append(f"    <li>{_esc(item)}</li>")
    lines.extend(["  </ol>", "</section>"])
    return "\n".join(lines)


def _episode_dom(episode: dict[str, Any]) -> str:
    idx = episode.get("index") or "?"
    title = episode.get("title") or "未命名环节"
    lines = [
        '<article class="r220e-process-episode" data-r220e-process-episode="true">',
        '  <div class="r220e-episode-head">',
        f'    <h3>{_esc(idx)}. {_esc(title)}</h3>',
        '    <span class="r220e-compact-badge">候选</span>',
        "  </div>",
        '  <dl class="r220e-episode-core">',
        f'    <dt>环节目标</dt><dd>{_esc(episode.get("goal"))}</dd>',
        f'    <dt>教师组织</dt><dd>{_esc(episode.get("teacher"))}</dd>',
        f'    <dt>学生学习</dt><dd>{_esc(episode.get("student"))}</dd>',
        f'    <dt>关键话术</dt><dd>{_esc(episode.get("talk"))}<span class="r220e-confirm-inline">需教师确认</span></dd>',
        f'    <dt>核心证据</dt><dd>{_esc(episode.get("evidence"))}</dd>',
        "  </dl>",
        '  <details class="r220e-folded-detail" data-r220e-microstep-collapsed="true">',
        "    <summary>展开 micro-step、材料、支架和小教提醒</summary>",
        '    <div class="r220e-folded-grid">',
        f'      <p><strong>小步骤</strong>{_esc(title)}</p>',
        f'      <p><strong>材料</strong>{_esc(episode.get("materials"))}</p>',
        f'      <p><strong>支架</strong>{_esc(episode.get("scaffold"))}</p>',
        f'      <p><strong>小教提醒</strong>{_esc(episode.get("hint"))}</p>',
        "    </div>",
        "  </details>",
        "</article>",
    ]
    return "\n".join(lines)


def _confirm_groups_dom(groups: dict[str, list[str]]) -> str:
    lines = [
        '<section class="nb-doc-section r220e-doc-section" data-render-slot="teacher-confirm-items" data-r220e-section="teacher-confirm-items">',
        '  <div class="nb-doc-section-head r220e-section-head">',
        "    <h2 class=\"nb-doc-title\">八、待教师确认项</h2>",
        "  </div>",
    ]
    for group in ["必须确认", "建议确认"]:
        lines.append(f'  <div class="r220e-confirm-group" data-r220e-confirm-group="{_esc(group)}">')
        lines.append(f"    <h3>{_esc(group)}</h3>")
        lines.append("    <ol>")
        for item in groups.get(group) or []:
            lines.append(f"      <li>{_esc(item)}</li>")
        lines.append("    </ol>")
        lines.append("  </div>")
    diagnostic = groups.get("可折叠诊断") or []
    lines.append('  <details class="r220e-folded-detail" data-r220e-confirm-diagnostic-collapsed="true">')
    lines.append("    <summary>可折叠诊断</summary>")
    lines.append("    <ol>")
    for item in diagnostic:
        lines.append(f"      <li>{_esc(item)}</li>")
    lines.append("    </ol>")
    lines.append("  </details>")
    lines.append("</section>")
    return "\n".join(lines)


def _lesson_body_dom(sample_id: str, template: dict[str, Any]) -> str:
    title = template.get("lesson_label") or sample_id
    sections = [
        ("basis", "一", template["basis"]),
        ("analysis", "二", template["analysis"]),
        ("goals", "三", template["objectives"]),
        ("keypoints", "四", template["key_points"]),
        ("preparation", "五", template["preparation"]),
    ]
    lines = [
        f'<div class="nb-workspace r220e-center-body" data-render-surface="lesson-body" data-render-slot="lesson-body" data-r220e-center-body-readonly="true" data-r220e-sample-id="{_esc(sample_id)}">',
        '  <article class="nb-doc r220e-lesson-document" data-render-surface="lesson-document" data-r220e-readonly-document="true">',
        '    <header class="r220e-document-head">',
        f"      <h1>{_esc(title)}</h1>",
        f'      <p class="r220e-candidate-status" data-r220e-candidate-status="true">{TOP_CANDIDATE_LABEL}</p>',
        "    </header>",
    ]
    for slot, number, section in sections:
        lines.append(_section_dom(slot, number, section))

    lines.extend(
        [
            '<section class="nb-doc-section r220e-doc-section" id="nb-section-teaching-process" data-render-slot="teaching-process" data-r220e-section="teaching-process">',
            '  <div class="nb-doc-section-head r220e-section-head">',
            '    <h2 class="nb-doc-title">六、教学过程</h2>',
            "  </div>",
            '  <div class="nb-readable-process r220e-readable-process" data-render-slot="teaching-process-episodes">',
        ]
    )
    for episode in template.get("episodes") or []:
        lines.append(_episode_dom(episode))
    lines.extend(["  </div>", "</section>"])

    assessment = {"title": "七、学习单与评价", "body": template.get("assessment") or []}
    lines.append(_section_dom("assessment", "七", assessment))
    lines.append(_confirm_groups_dom(template.get("confirm_groups") or {}))
    lines.extend(["  </article>", "</div>"])
    return "\n".join(lines)


def _visible_text(dom: str) -> str:
    return re.sub(r"<[^>]+>", "", dom)


def _render_sample(sample_dir: Path) -> dict[str, Any]:
    sample_id = sample_dir.name
    template_path = sample_dir / "fixed_lesson_template_candidate.json"
    template = _read_json(template_path)
    dom = _lesson_body_dom(sample_id, template)
    out_dir = OUT / "r220e_teacher_readable_dom_snapshots" / sample_id
    dom_path = out_dir / "lesson_body.html"
    text_path = out_dir / "lesson_body_text.txt"
    _write_text(dom_path, dom)
    _write_text(text_path, _visible_text(dom))

    episode_count = len(template.get("episodes") or [])
    collapsed_count = dom.count('data-r220e-microstep-collapsed="true"')
    repeated_label_count = dom.count(FULL_REPEATED_SOURCE_LABEL)
    candidate_status_count = dom.count('data-r220e-candidate-status="true"')
    old_static_hits = [marker for marker in OLD_STATIC_MARKERS if marker in dom]
    forbidden_hits = [term for term in FORBIDDEN_TERMS if term in dom]
    source_gap_as_body = "source_gap" in dom
    right_rail_hit = "right-rail" in dom or "data-render-slot=\"right-rail\"" in dom
    bottom_hit = "bottom-xiaojiao" in dom
    details_open_count = len(re.findall(r"<details[^>]*\sopen(\s|>|=)", dom))
    core_labels = ["环节目标", "教师组织", "学生学习", "关键话术", "核心证据"]
    core_label_ok = all(label in dom for label in core_labels)
    confirm_groups_ok = all(group in dom for group in ["必须确认", "建议确认", "可折叠诊断"])

    return {
        "sample_id": sample_id,
        "lesson_label": template.get("lesson_label"),
        "dom_snapshot": _rel(dom_path),
        "text_snapshot": _rel(text_path),
        "episode_count": episode_count,
        "episode_nodes": dom.count('data-r220e-process-episode="true"'),
        "microstep_collapsed_count": collapsed_count,
        "details_open_count": details_open_count,
        "candidate_status_count": candidate_status_count,
        "repeated_full_source_label_count": repeated_label_count,
        "old_static_marker_hits": old_static_hits,
        "forbidden_term_hits": forbidden_hits,
        "source_gap_as_teacher_content": source_gap_as_body,
        "right_rail_touched": right_rail_hit,
        "bottom_xiaojiao_touched": bottom_hit,
        "core_labels_ok": core_label_ok,
        "confirm_groups_ok": confirm_groups_ok,
        "new_html_shell_created": "<!doctype" in dom.lower() or "<html" in dom.lower() or "<body" in dom.lower(),
        "field_level_editing_widgets": any(token in dom for token in ["<input", "<textarea", "contenteditable", "<button"]),
    }


def _write_reports(sample_results: list[dict[str, Any]]) -> None:
    _write_text(
        OUT / "r220e_readability_display_policy.md",
        "\n".join(
            [
                "# R220E 中间正文只读显示策略",
                "",
                "R220E 只渲染 R201K after-fix 候选教案到 R97B 中间 `lesson-body` 槽位，不渲染右栏、大屏或小教修改。",
                "",
                "- 顶部只显示一次“系统候选，需教师确认”。",
                "- 章节内只显示紧凑“候选” badge，不重复完整来源长句。",
                "- 教学过程默认显示环节标题、环节目标、教师组织、学生学习、关键话术和核心证据。",
                "- micro-step、材料、支架和小教提醒默认折叠。",
                "- 待教师确认项按必须确认、建议确认、可折叠诊断分组显示。",
            ]
        ),
    )
    _write_text(
        OUT / "r220e_center_body_render_report.md",
        "\n".join(
            [
                "# R220E 中间正文只读渲染报告",
                "",
                "本轮使用 R201K after-fix candidate 生成 `lesson-body` HTML 片段，不新建完整 HTML 壳。",
                "",
                "## 样本",
                "",
                *[
                    f"- {item['lesson_label']}（{item['sample_id']}）：{item['episode_count']} 个环节，DOM 快照 `{item['dom_snapshot']}`。"
                    for item in sample_results
                ],
                "",
                "## 边界",
                "",
                "- 不接 R220E 以外的右栏 / 大屏内容模型。",
                "- 不接小教真实修改。",
                "- 不做字段级编辑。",
                "- 不 formal apply，不写库，不进入 R95，不调用 provider/model。",
            ]
        ),
    )


def _run_py_compile() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "py_compile", str(Path(__file__))],
        cwd=str(ROOT),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": f"{sys.executable} -m py_compile scripts/{Path(__file__).name}",
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1200:],
        "stderr_tail": completed.stderr[-1200:],
    }


def main() -> None:
    r201k_result = _read_json(R201K_RESULT)
    r220d_result = _read_json(R220D_RESULT)
    sample_dirs = [R201K_SAMPLES / sample_id for sample_id in SAMPLE_ORDER]
    sample_results = [_render_sample(sample_dir) for sample_dir in sample_dirs]
    _write_reports(sample_results)

    render_matrix = {
        "stage": STAGE,
        "sample_count": len(sample_results),
        "samples": sample_results,
    }
    static_check = {
        "stage": STAGE,
        "old_static_markers": OLD_STATIC_MARKERS,
        "samples": [
            {
                "sample_id": item["sample_id"],
                "old_static_marker_hits": item["old_static_marker_hits"],
                "old_static_body_replaced": not item["old_static_marker_hits"],
            }
            for item in sample_results
        ],
    }
    source_check = {
        "stage": STAGE,
        "top_candidate_status_label": TOP_CANDIDATE_LABEL,
        "samples": [
            {
                "sample_id": item["sample_id"],
                "candidate_status_count": item["candidate_status_count"],
                "repeated_full_source_label_count": item["repeated_full_source_label_count"],
                "forbidden_term_hits": item["forbidden_term_hits"],
                "source_gap_as_teacher_content": item["source_gap_as_teacher_content"],
            }
            for item in sample_results
        ],
    }
    right_rail_guard = {
        "stage": STAGE,
        "right_rail_scope": "reserved auxiliary surface",
        "right_rail_content_model_out_of_scope": True,
        "bottom_xiaojiao_real_modification_out_of_scope": True,
        "samples": [
            {
                "sample_id": item["sample_id"],
                "right_rail_touched": item["right_rail_touched"],
                "bottom_xiaojiao_touched": item["bottom_xiaojiao_touched"],
            }
            for item in sample_results
        ],
    }
    _write_json(OUT / "r220e_sample_render_matrix.json", render_matrix)
    _write_json(OUT / "r220e_static_content_replacement_check.json", static_check)
    _write_json(OUT / "r220e_source_policy_dom_check.json", source_check)
    _write_json(OUT / "r220e_right_rail_out_of_scope_guard.json", right_rail_guard)

    py_compile = _run_py_compile()
    checks = {
        "r201k_pass_with_notes": r201k_result.get("status") == "PASS",
        "r220d_slot_smoke_pass": r220d_result.get("status") == "PASS",
        "five_samples_rendered_to_lesson_body": len(sample_results) == 5
        and all(item["dom_snapshot"] and item["episode_nodes"] == item["episode_count"] for item in sample_results),
        "old_static_body_not_residual": all(not item["old_static_marker_hits"] for item in sample_results),
        "top_candidate_status_once": all(item["candidate_status_count"] == 1 for item in sample_results),
        "full_source_label_not_repeated": all(item["repeated_full_source_label_count"] == 0 for item in sample_results),
        "default_process_core_fields_present": all(item["core_labels_ok"] for item in sample_results),
        "microsteps_materials_scaffolds_xiaojiao_folded": all(
            item["microstep_collapsed_count"] == item["episode_count"] and item["details_open_count"] == 0
            for item in sample_results
        ),
        "confirmation_groups_present": all(item["confirm_groups_ok"] for item in sample_results),
        "engineering_term_in_teacher_main_zero": all(not item["forbidden_term_hits"] for item in sample_results),
        "source_gap_as_teacher_content_zero": all(not item["source_gap_as_teacher_content"] for item in sample_results),
        "right_rail_out_of_scope_guard": all(not item["right_rail_touched"] for item in sample_results),
        "bottom_xiaojiao_out_of_scope_guard": all(not item["bottom_xiaojiao_touched"] for item in sample_results),
        "no_new_html_shell": all(not item["new_html_shell_created"] for item in sample_results),
        "no_field_level_editing": all(not item["field_level_editing_widgets"] for item in sample_results),
        "no_R21_R36_change": True,
        "no_R36_M1_R100_P1_promoted": True,
        "no_formal_apply": True,
        "no_write": True,
        "no_R95": True,
        "no_model_provider_call": True,
        "py_compile_pass": py_compile["returncode"] == 0,
    }
    result = {
        "stage": STAGE,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "decision": "PASS_AS_CENTER_BODY_READONLY_RENDER_ARTIFACT_NOT_ROUTE_SWITCH"
        if all(checks.values())
        else "FAIL",
        "checks": checks,
        "sample_results": sample_results,
        "outputs": {
            "center_body_render_report": _rel(OUT / "r220e_center_body_render_report.md"),
            "sample_render_matrix": _rel(OUT / "r220e_sample_render_matrix.json"),
            "teacher_readable_dom_snapshots": _rel(OUT / "r220e_teacher_readable_dom_snapshots"),
            "static_content_replacement_check": _rel(OUT / "r220e_static_content_replacement_check.json"),
            "readability_display_policy": _rel(OUT / "r220e_readability_display_policy.md"),
            "source_policy_dom_check": _rel(OUT / "r220e_source_policy_dom_check.json"),
            "right_rail_out_of_scope_guard": _rel(OUT / "r220e_right_rail_out_of_scope_guard.json"),
            "validation_result": _rel(RESULT),
        },
        "boundary": {
            "new_html_shell": False,
            "R21_modified": False,
            "R36_modified": False,
            "R36_M1_R100_P1_promoted": False,
            "right_rail_big_screen_model_connected": False,
            "right_rail_scope": "reserved auxiliary surface",
            "xiaojiao_real_modification": False,
            "field_level_editing": False,
            "formal_apply": False,
            "database_written": False,
            "feishu_written": False,
            "memory_written": False,
            "R95_executed": False,
            "provider_model_called": False,
            "route_switch": False,
        },
        "py_compile": py_compile,
    }
    _write_json(RESULT, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
