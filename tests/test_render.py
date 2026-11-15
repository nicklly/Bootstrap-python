"""bootstrap-python 的渲染测试：直接运行 ``python -m unittest discover tests``。"""

from __future__ import annotations

import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bootstrap_ui import (  # noqa: E402
    Accordion,
    AccordionItem,
    Badge,
    Button,
    Card,
    Col,
    Color,
    Form,
    FormGroup,
    Heading,
    Image,
    Input,
    Modal,
    Page,
    Row,
    Select,
    Span,
    Table,
    TableColumn,
    Tabs,
    TabItem,
    raw,
)
from bootstrap_ui.types import VOID_TAGS  # noqa: E402


class _Balance(HTMLParser):
    """检查标签是否正确闭合。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"多余的 </{tag}>")
            return
        if self.stack[-1] == tag:
            self.stack.pop()
            return
        self.errors.append(f"期望 </{self.stack[-1]}>，实际 </{tag}>")
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass


def assert_balanced(test: unittest.TestCase, html: str) -> None:
    checker = _Balance()
    checker.feed(html)
    checker.close()
    test.assertEqual(checker.errors, [], "标签未正确闭合")
    test.assertEqual(checker.stack, [], "存在未闭合标签")


class TestRender(unittest.TestCase):
    def test_text_is_escaped(self) -> None:
        html = Span(text="<script>alert(1)</script>").render()
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_raw_bypasses_escaping(self) -> None:
        self.assertEqual(raw("<b>粗体</b>").render(), "<b>粗体</b>")

    def test_attributes(self) -> None:
        node = Button(text="保存", color=Color.primary, size="sm", id="save", class_name="me-2")
        html = node.render()
        self.assertIn('class="btn btn-primary btn-sm me-2"', html)
        self.assertIn('id="save"', html)
        self.assertIn('<button', html)

    def test_style_dict(self) -> None:
        html = Span(text="x", style={"min_width": "10rem", "color": "red"}).render()
        self.assertIn('style="min-width: 10rem; color: red"', html)

    def test_void_elements(self) -> None:
        html = Image(src="/a.png", alt="图").render()
        self.assertEqual(html.count("</img>"), 0)
        self.assertIn('src="/a.png"', html)

    def test_heading_level(self) -> None:
        self.assertTrue(Heading(text="标题", level=1).render().startswith("<h1"))
        self.assertTrue(Heading(text="标题", level=3).render().startswith("<h3"))

    def test_badge_and_progress(self) -> None:
        self.assertIn("text-bg-success", Badge(text="正常", color=Color.success).render())

    def test_form_control_and_feedback(self) -> None:
        html = Input(name="email", type="email", required=True, invalid=True, invalid_feedback="必填").render()
        self.assertIn('id="field-email"', html)
        self.assertIn("is-invalid", html)
        self.assertIn("invalid-feedback", html)

    def test_form_group_label_for(self) -> None:
        html = FormGroup(label="姓名", control=Input(name="name")).render()
        self.assertIn('for="field-name"', html)
        self.assertIn('id="field-name"', html)

    def test_select_options_and_placeholder(self) -> None:
        html = Select(
            name="role",
            placeholder="请选择",
            options=[("管理员", "admin"), {"label": "用户", "value": "user", "disabled": True}],
        ).render()
        self.assertIn('disabled selected>请选择', html)
        self.assertIn('<option value="admin">管理员</option>', html)
        self.assertIn('<option value="user" disabled>用户</option>', html)

    def test_select_value_selected(self) -> None:
        html = Select(name="role", value="user", options=[("管理员", "admin"), ("用户", "user")]).render()
        self.assertIn('<option value="user" selected>用户</option>', html)

    def test_table_dict_rows(self) -> None:
        table = Table(
            columns=[TableColumn(label="ID", key="id"), TableColumn(label="名称", key="name")],
            rows=[{"id": 1, "name": "甲"}, {"id": 2, "name": "乙"}],
        ).render()
        self.assertIn("<th scope=\"col\">ID</th>", table)
        self.assertIn("<td>甲</td>", table)
        self.assertIn("table-striped", Table(columns=["A"], rows=[[1]], striped=True).render())

    def test_table_empty_state(self) -> None:
        html = Table(columns=["A", "B"], rows=[]).render()
        self.assertIn('colspan="2"', html)
        self.assertIn("暂无数据", html)

    def test_table_auto_columns_from_dict(self) -> None:
        html = Table(rows=[{"a": 1, "b": 2}]).render()
        self.assertIn("<th scope=\"col\">a</th>", html)
        self.assertIn("<th scope=\"col\">b</th>", html)

    def test_tabs_first_active(self) -> None:
        html = Tabs(items=[TabItem(label="一", body=["A"]), TabItem(label="二", body=["B"])]).render()
        self.assertIn("nav-link active", html)
        self.assertIn("tab-pane fade show active", html)
        self.assertEqual(html.count('role="tabpanel"'), 2)

    def test_accordion_expands_first(self) -> None:
        html = Accordion(items=[AccordionItem(title="Q1", body=["A"]), AccordionItem(title="Q2")]).render()
        self.assertIn("accordion-collapse collapse show", html)
        self.assertIn('data-bs-parent=', html)

    def test_modal_markup(self) -> None:
        html = Modal(id="m1", title="标题", body=["内容"], footer=[Button(text="关闭")]).render()
        self.assertIn('id="m1"', html)
        self.assertIn("modal-dialog-centered", html)
        self.assertIn('aria-labelledby="m1-label"', html)

    def test_button_toggle_modal(self) -> None:
        html = Button(text="打开", toggle_modal="m1").render()
        self.assertIn('data-bs-toggle="modal"', html)
        self.assertIn('data-bs-target="#m1"', html)

    def test_page_shell(self) -> None:
        html = Page(title="标题<script>", body=[Card(body=["内容"])]).render()
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn("bootstrap@5.3.3/dist/css/bootstrap.min.css", html)
        self.assertIn("bootstrap.bundle.min.js", html)
        self.assertIn("&lt;script&gt;", html.split("<title>")[1].split("</title>")[0] + "&lt;script&gt;")

    def test_nested_layout_is_balanced(self) -> None:
        page = Page(
            title="结构测试",
            body=[
                Row(
                    gutter=3,
                    children=[
                        Col(md=6, body=[Card(title="A", body=[Table(columns=["x"], rows=[[1]])])]),
                        Col(md=6, body=[Card(title="B", body=[Form(body=[FormGroup(label="L", control=Input(name="n"))])])]),
                    ],
                )
            ],
        )
        assert_balanced(self, page.render())

    def test_to_dict_keeps_subclass_fields(self) -> None:
        data = Card(title="卡片", body=[Badge(text="x")]).to_dict()
        self.assertIn("title", data)
        self.assertEqual(data["body"][0]["text"], "x")

    def test_to_dict_uses_class_alias(self) -> None:
        self.assertEqual(Span(text="x", class_name="fw-bold").to_dict()["class"], "fw-bold")


class TestDemoPage(unittest.TestCase):
    """对生成出来的 examples/dashboard.html 做结构检查。"""

    demo = ROOT / "examples" / "dashboard.html"

    @unittest.skipUnless(demo.exists(), "dashboard.html 尚未生成，先运行 python examples/dashboard.py")
    def test_demo_is_balanced(self) -> None:
        assert_balanced(self, self.demo.read_text(encoding="utf-8"))

    @unittest.skipUnless(demo.exists(), "dashboard.html 尚未生成，先运行 python examples/dashboard.py")
    def test_demo_contains_key_sections(self) -> None:
        html = self.demo.read_text(encoding="utf-8")
        for marker in ("Acme 控制台", "数据概览", "user-modal", "filter-panel", "toast-container", "pagination"):
            self.assertIn(marker, html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
