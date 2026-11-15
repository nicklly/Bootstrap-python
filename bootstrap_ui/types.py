"""bootstrap-python 的渲染内核：Node 基类、属性序列化与 HTML 转义。

统一的输出约定：

    node.to_dict()   # 结构化描述（可 JSON 序列化，便于调试或传给前端）
    node.to_json()   # JSON 字符串
    node.render()    # HTML 字符串

设计要点
--------
1. 每个组件都是 ``Node`` 的子类，只描述「我是哪个标签、有哪些 Bootstrap 类、装什么内容」；
2. 文本内容默认转义，需要输出可信 HTML 时显式使用 :class:`RawHtml` / :func:`raw`；
3. 组件字段用 pydantic 校验（``extra="forbid"``），写错字段名会立刻报错，而不是静默失效。
"""

from __future__ import annotations

import html as _html
import json
from typing import Any, ClassVar, Iterable, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "Node",
    "RawHtml",
    "raw",
    "NodeLike",
    "escape",
    "render_attrs",
    "render_children",
    "VOID_TAGS",
]

#: HTML 中不需要闭合标签的元素
VOID_TAGS: frozenset[str] = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)


def escape(value: Any) -> str:
    """把任意值转成转义后的文本。"""
    if value is None:
        return ""
    return _html.escape(str(value), quote=True)


def render_attrs(attrs: dict[str, Any]) -> str:
    """把属性字典渲染成 `` key="value"`` 形式的片段。

    - ``None`` / ``False`` 直接跳过；
    - ``True`` 输出为布尔属性（如 ``required``）；
    - ``list`` / ``tuple`` 以空格连接（常用于 class）；
    - ``dict`` 序列化为 JSON（用于 data-* 配置）。
    """
    parts: list[str] = []
    for key, value in attrs.items():
        if value is None or value is False:
            continue
        name = str(key).rstrip("_")
        if value is True:
            parts.append(f" {name}")
            continue
        if isinstance(value, (list, tuple, set)):
            value = " ".join(str(item) for item in value if item is not None)
        elif isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        parts.append(f' {name}="{escape(value)}"')
    return "".join(parts)


def render_children(items: Any, separator: str = "") -> str:
    """渲染子节点序列，自动处理嵌套列表与文本转义。"""
    if items is None:
        return ""
    if isinstance(items, (str, bytes)) or isinstance(items, Node):
        items = [items]
    if not isinstance(items, Iterable):
        return escape(items)

    rendered: list[str] = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, Node):          # RawHtml 也是 Node，会走各自的 render
            rendered.append(item.render())
        elif isinstance(item, (list, tuple)):
            rendered.append(render_children(item, separator))
        else:
            rendered.append(escape(item))
    return separator.join(part for part in rendered if part != "")


class Node(BaseModel):
    """所有组件的基类。"""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    #: 组件对应的 HTML 标签，``None`` 表示不产生包裹标签
    TAG: ClassVar[str | None] = "div"

    id: str | None = None
    """元素 id"""

    class_name: str | None = Field(default=None, alias="class")
    """追加到元素上的自定义 class（Bootstrap 原生类名）"""

    style: str | dict[str, Any] | None = None
    """行内样式，字符串或 ``{"min-width": "10rem"}`` 这样的字典"""

    attrs: dict[str, Any] = Field(default_factory=dict)
    """其它原生 HTML 属性，例如 ``{"data-bs-toggle": "tooltip", "aria-label": "提示"}``"""

    # ------------------------------------------------------------------ 扩展点
    def css_classes(self) -> list[str]:
        """返回该组件的 Bootstrap 类名列表，子类按需覆写。"""
        return []

    def html_attrs(self) -> dict[str, Any]:
        """返回最终写进标签的属性字典。"""
        attrs: dict[str, Any] = {}

        classes = [cls for cls in self.css_classes() if cls]
        if self.class_name:
            classes.append(self.class_name)
        if classes:
            attrs["class"] = " ".join(classes)

        if self.id:
            attrs["id"] = self.id

        if self.style:
            attrs["style"] = _style_to_string(self.style)

        for key, value in self.attrs.items():
            attrs[key] = value
        return attrs

    def tag_name(self) -> str | None:
        """返回实际使用的标签名，需要动态标签的组件（如 Heading）可覆写。"""
        return self.TAG

    def render_content(self) -> str:
        """返回标签内部的内容。"""
        return ""

    def render(self) -> str:
        """渲染成 HTML 字符串。"""
        content = self.render_content()
        tag = self.tag_name()
        if tag is None:
            return content

        attrs = render_attrs(self.html_attrs())
        if tag in VOID_TAGS:
            return f"<{tag}{attrs}>"
        return f"<{tag}{attrs}>{content}</{tag}>"

    # ------------------------------------------------------------------ 输出
    def to_dict(self) -> dict[str, Any]:
        """结构化描述，便于调试或把界面定义传给前端。"""
        data = self.model_dump(
            by_alias=True,
            exclude_none=True,
            mode="json",
            serialize_as_any=True,   # 保留子类组件的全部字段，而不是退化成 Node
        )
        return _clean(data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def __str__(self) -> str:  # noqa: D105 - 方便 print(node)
        return self.render()


def _clean(data: Any) -> Any:
    """去掉序列化结果里的空字段（如 ``attrs: {}``），让 to_dict 更干净。"""
    if isinstance(data, dict):
        return {
            key: _clean(item)
            for key, item in data.items()
            if not (key in {"attrs", "style"} and not item)
        }
    if isinstance(data, list):
        return [_clean(item) for item in data]
    return data


def _style_to_string(style: str | dict[str, Any]) -> str:
    if isinstance(style, str):
        return style
    chunks: list[str] = []
    for key, value in style.items():
        if value is None:
            continue
        name = str(key).replace("_", "-")
        chunks.append(f"{name}: {value}")
    return "; ".join(chunks)


class RawHtml(Node):
    """原样输出的 HTML 片段（不再转义）。"""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    TAG: ClassVar[str | None] = None

    html: str = ""

    def render(self) -> str:
        return self.html


def raw(source: str) -> RawHtml:
    """快捷构造 :class:`RawHtml`。"""
    return RawHtml(html=source)


#: 可以放进容器里的内容：组件、文本、数字
NodeLike = Union[Node, str, int, float]
