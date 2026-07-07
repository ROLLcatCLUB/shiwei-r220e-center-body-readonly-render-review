# R220E 中间正文只读渲染报告

本轮使用 R201K after-fix candidate 生成 `lesson-body` HTML 片段，不新建完整 HTML 壳。

## 样本

- 下雨啰（real_downpour_docx）：6 个环节，DOM 快照 `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER/r220e_teacher_readable_dom_snapshots/real_downpour_docx/lesson_body.html`。
- 旧鞋 / 足下生辉（numbered_colon_old_shoes）：5 个环节，DOM 快照 `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER/r220e_teacher_readable_dom_snapshots/numbered_colon_old_shoes/lesson_body.html`。
- 穿穿编编（plain_segment_weaving）：6 个环节，DOM 快照 `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER/r220e_teacher_readable_dom_snapshots/plain_segment_weaving/lesson_body.html`。
- 雨伞图案设计（table_rain_umbrella）：4 个环节，DOM 快照 `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER/r220e_teacher_readable_dom_snapshots/table_rain_umbrella/lesson_body.html`。
- 线条小鱼（minimal_line_fish）：3 个环节，DOM 快照 `outputs/PREP_ROOM_RENDER_CANVAS_DEEPEN_V1/1013R_R220E_SINGLE_LESSON_TEMPLATE_CENTER_BODY_READONLY_RENDER/r220e_teacher_readable_dom_snapshots/minimal_line_fish/lesson_body.html`。

## 边界

- 不接 R220E 以外的右栏 / 大屏内容模型。
- 不接小教真实修改。
- 不做字段级编辑。
- 不 formal apply，不写库，不进入 R95，不调用 provider/model。