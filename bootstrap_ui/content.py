"""基础内容组件：标题、文本、链接、图片、图标、徽标、提示框、卡片、列表组、按钮。"""

from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import Field

from .constants import Color, Size, value as enum_value
from .types import Node, NodeLike, escape, render_attrs, render_children

__all__ = [
    "Heading",
    "Paragraph",
    "Span",
    "Strong",
    "Small",
    "Link",
    "Image",
    "Icon",
    "Badge",
    "Alert",
    "Card",
    "ListGroup",
    "ListItem",
    "Button",
    "ButtonGroup",
    "CloseButton",
    "icon_name",
]


def icon_name(name: str) -> str:
    """把 ``plus``、``bi-plus``、``bi bi-plus`` 统一成 ``bi bi-plus``。"""
    cleaned = name.strip().removeprefix("bi ").removeprefix("bi-")
    return f"bi bi-{cleaned}"


class Heading(Node):
    """标题，``<h1>`` ~ ``<h6>``。"""

    TAG: ClassVar[str | None] = None

    text: str = ""
    level: int = 2
    """1-6，默认 2"""

    size: Literal["1", "2", "3", "4", "5", "6"] | None = None
    """视觉字号（class ``h1``~``h6``），与语义 level 解耦"""

    body: list[NodeLike] = Field(default_factory=list)

    def tag_name(self) -> str | None:
        level = min(max(self.level, 1), 6)
        return f"h{level}"

    def css_classes(self) -> list[str]:
        return [f"h{self.size}"] if self.size else []

    def render_content(self) -> str:
        return escape(self.text) + render_children(self.body)


class Paragraph(Node):
    """段落。"""

    TAG: ClassVar[str | None] = "p"

    text: str = ""
    body: list[NodeLike] = Field(default_factory=list)

    lead: bool = False
    """引导段落（``.lead``）"""

    muted: bool = False
    """次要文字色（``text-body-secondary``）"""

    def css_classes(self) -> list[str]:
        classes: list[str] = []
        if self.lead:
            classes.append("lead")
        if self.muted:
            classes.append("text-body-secondary")
        return classes

    def render_content(self) -> str:
        return escape(self.text) + render_children(self.body)


class Span(Node):
    """行内文本片段。"""

    TAG: ClassVar[str | None] = "span"

    text: str = ""
    body: list[NodeLike] = Field(default_factory=list)

    color: str | None = None
    """``text-*`` 的颜色名，如 ``danger``、``body-secondary``"""

    muted: bool = False
    weight: Literal["bold", "semibold", "normal", "light"] | None = None
    nowrap: bool = False

    def css_classes(self) -> list[str]:
        classes: list[str] = []
        if self.color:
            classes.append(f"text-{self.color}")
        if self.muted:
            classes.append("text-body-secondary")
        if self.weight:
            classes.append(f"fw-{self.weight}")
        if self.nowrap:
            classes.append("text-nowrap")
        return classes

    def render_content(self) -> str:
        return escape(self.text) + render_children(self.body)


class Strong(Span):
    """加粗文本。"""

    TAG: ClassVar[str | None] = "strong"


class Small(Span):
    """小号文本。"""

    TAG: ClassVar[str | None] = "small"

    def css_classes(self) -> list[str]:
        classes = super().css_classes()
        if not any(cls.startswith("text-") for cls in classes):
            classes.append("text-body-secondary")
        return classes


class Link(Node):
    """超链接。"""

    TAG: ClassVar[str | None] = "a"

    text: str = ""
    body: list[NodeLike] = Field(default_factory=list)

    href: str = "#"
    target: Literal["_blank", "_self", "_parent", "_top"] | None = None
    color: str | None = None
    no_underline: bool = False
    icon: str | None = None

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["href"] = self.href
        if self.target:
            attrs["target"] = self.target
            if self.target == "_blank":
                attrs.setdefault("rel", "noopener noreferrer")
        return attrs

    def css_classes(self) -> list[str]:
        classes: list[str] = []
        if self.color:
            classes.append(f"link-{self.color}")
        if self.no_underline:
            classes.append("text-decoration-none")
        return classes

    def render_content(self) -> str:
        icon = f'<i class="{icon_name(self.icon)} me-1"></i>' if self.icon else ""
        return icon + escape(self.text) + render_children(self.body)


class Image(Node):
    """图片。"""

    TAG: ClassVar[str | None] = "img"

    src: str = ""
    alt: str = ""

    width: int | str | None = None
    height: int | str | None = None

    fluid: bool = False
    """响应式图片（``img-fluid``）"""

    rounded: bool | str = False
    """``True`` → ``rounded``；字符串 → ``rounded-3`` 之类"""

    circle: bool = False
    """圆形（``rounded-circle``）"""

    thumbnail: bool = False
    """缩略图边框（``img-thumbnail``）"""

    lazy: bool = True

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["src"] = self.src
        attrs["alt"] = self.alt
        if self.width is not None:
            attrs["width"] = self.width
        if self.height is not None:
            attrs["height"] = self.height
        if self.lazy:
            attrs["loading"] = "lazy"
        return attrs

    def css_classes(self) -> list[str]:
        classes: list[str] = []
        if self.fluid:
            classes.append("img-fluid")
        if self.circle:
            classes.append("rounded-circle")
        elif self.rounded:
            classes.append("rounded" if self.rounded is True else f"rounded-{self.rounded}")
        if self.thumbnail:
            classes.append("img-thumbnail")
        return classes


class Icon(Node):
    """Bootstrap Icons 图标。"""

    TAG: ClassVar[str | None] = "i"

    name: str = "circle"
    size: str | int | None = None
    color: str | None = None
    spin: bool = False

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["aria-hidden"] = "true"
        styles: list[str] = []
        if self.size is not None:
            size = f"{self.size}px" if isinstance(self.size, int) else str(self.size)
            styles.append(f"font-size: {size}")
        if self.color:
            styles.append(f"color: var(--bs-{self.color})")
        if styles:
            attrs["style"] = "; ".join(styles) + (f"; {attrs['style']}" if "style" in attrs else "")
        return attrs

    def css_classes(self) -> list[str]:
        classes = icon_name(self.name).split()
        if self.spin:
            classes.append("spinner-border spinner-border-sm")
        return classes


class Badge(Node):
    """徽标。"""

    TAG: ClassVar[str | None] = "span"

    text: str = ""
    color: Color = Color.primary
    pill: bool = False
    icon: str | None = None

    def css_classes(self) -> list[str]:
        classes = [f"badge text-bg-{enum_value(self.color)}"]
        if self.pill:
            classes.append("rounded-pill")
        return classes

    def render_content(self) -> str:
        icon = f'<i class="{icon_name(self.icon)} me-1"></i>' if self.icon else ""
        return icon + escape(self.text)


class Alert(Node):
    """提示框。"""

    color: Color = Color.info
    body: list[NodeLike] = Field(default_factory=list)
    title: str | None = None
    icon: str | None = None
    dismissible: bool = True
    show: bool = True

    def css_classes(self) -> list[str]:
        classes = [f"alert alert-{enum_value(self.color)}"]
        if self.dismissible:
            classes.append("alert-dismissible")
        if self.show and self.dismissible:
            classes.append("fade show")
        return classes

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("role", "alert")
        return attrs

    def render_content(self) -> str:
        parts: list[str] = []
        if self.icon:
            parts.append(f'<i class="{icon_name(self.icon)} me-2"></i>')
        if self.title:
            parts.append(f"<strong>{escape(self.title)}</strong> ")
        parts.append(render_children(self.body))
        if self.dismissible:
            parts.append(
                '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="关闭"></button>'
            )
        return "".join(parts)


class Card(Node):
    """卡片。"""

    body: list[NodeLike] = Field(default_factory=list)
    title: str | None = None
    subtitle: str | None = None
    header: list[NodeLike] | None = None
    """自定义页眉内容，设置后忽略 title/subtitle"""

    footer: list[NodeLike] | None = None
    actions: list[NodeLike] = Field(default_factory=list)
    """放在页眉右侧的操作按钮"""

    image: str | None = None
    image_position: Literal["top", "bottom"] = "top"
    color: Color | None = None
    body_class: str | None = None

    def css_classes(self) -> list[str]:
        classes = ["card", "h-100"]
        if self.color:
            classes.append(f"text-bg-{enum_value(self.color)}")
        return classes

    def _render_header(self) -> str:
        left: list[str] = []
        if self.header:
            left.append(render_children(self.header))
        else:
            if self.title:
                left.append(f'<h5 class="card-title mb-0">{escape(self.title)}</h5>')
            if self.subtitle:
                left.append(f'<div class="small opacity-75 mt-1">{escape(self.subtitle)}</div>')
        actions = render_children(self.actions)
        if not left and not actions:
            return ""

        left_html = "".join(left)
        if actions:
            return (
                '<div class="card-header d-flex justify-content-between align-items-center gap-2">'
                f'<div>{left_html}</div><div class="d-flex gap-2">{actions}</div></div>'
            )
        return f'<div class="card-header">{left_html}</div>'

    def render_content(self) -> str:
        parts: list[str] = []
        image = f'<img src="{escape(self.image)}" class="card-img-top" alt="">' if self.image else ""
        if image and self.image_position == "top":
            parts.append(image)
        parts.append(self._render_header())
        body_class = f"card-body {self.body_class}" if self.body_class else "card-body"
        parts.append(f'<div class="{body_class}">{render_children(self.body)}</div>')
        if self.footer:
            parts.append(f'<div class="card-footer">{render_children(self.footer)}</div>')
        if image and self.image_position == "bottom":
            parts.append(image)
        return "".join(parts)


class ListItem(Node):
    """列表组中的一项。"""

    TAG: ClassVar[str | None] = None

    text: str = ""
    body: list[NodeLike] = Field(default_factory=list)
    href: str | None = None
    active: bool = False
    disabled: bool = False
    color: str | None = None
    badge: str | None = None
    icon: str | None = None

    def render(self) -> str:
        classes = ["list-group-item"]
        if self.href:
            classes.append("list-group-item-action")
        if self.active:
            classes.append("active")
        if self.disabled:
            classes.append("disabled")
        if self.color:
            classes.append(f"list-group-item-{self.color}")
        if self.class_name:
            classes.append(self.class_name)

        content: list[str] = []
        if self.icon:
            content.append(f'<i class="{icon_name(self.icon)} me-2"></i>')
        content.append(escape(self.text))
        content.append(render_children(self.body))
        if self.badge:
            content.append(f'<span class="badge text-bg-secondary float-end">{escape(self.badge)}</span>')

        attrs = {"class": " ".join(classes)}
        if self.id:
            attrs["id"] = self.id
        if self.disabled:
            attrs["aria-disabled"] = "true"
        inner = "".join(content)
        if self.href and not self.disabled:
            return f'<a href="{escape(self.href)}"{render_attrs(attrs)}>{inner}</a>'
        return f'<div{render_attrs(attrs)}>{inner}</div>'


class ListGroup(Node):
    """列表组。"""

    items: list[ListItem | str] = Field(default_factory=list)
    flush: bool = False
    numbered: bool = False
    horizontal: bool = False

    def css_classes(self) -> list[str]:
        classes = ["list-group"]
        if self.flush:
            classes.append("list-group-flush")
        if self.numbered:
            classes.append("list-group-numbered")
        if self.horizontal:
            classes.append("list-group-horizontal")
        return classes

    def render_content(self) -> str:
        parts: list[str] = []
        for item in self.items:
            if isinstance(item, ListItem):
                parts.append(item.render())
            else:
                parts.append(ListItem(text=str(item)).render())
        return "".join(parts)


class Button(Node):
    """按钮。``href`` 存在时渲染为 ``<a>``。"""

    text: str = ""
    color: Color = Color.primary
    outline: bool = False
    size: Size | None = None
    type: Literal["button", "submit", "reset"] = "button"
    href: str | None = None
    icon: str | None = None
    block: bool = False
    disabled: bool = False
    active: bool = False

    toggle_modal: str | None = None
    """点击打开指定 id 的模态框，自动补 ``data-bs-toggle/target``"""

    toggle_offcanvas: str | None = None
    """点击打开指定 id 的抽屉"""

    dismiss: Literal["modal", "offcanvas", "alert", "toast"] | None = None
    """点击关闭指定类型的浮层"""

    tooltip: str | None = None
    """鼠标悬停提示（由页面脚本初始化）"""

    def tag_name(self) -> str | None:
        return "a" if self.href else "button"

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        if self.href:
            attrs["href"] = self.href
        else:
            attrs["type"] = self.type
        if self.disabled:
            if self.href:
                attrs["aria-disabled"] = "true"
                attrs["tabindex"] = "-1"
            else:
                attrs["disabled"] = True
        if self.toggle_modal:
            attrs["data-bs-toggle"] = "modal"
            attrs["data-bs-target"] = f"#{self.toggle_modal.lstrip('#')}"
        elif self.toggle_offcanvas:
            attrs["data-bs-toggle"] = "offcanvas"
            attrs["data-bs-target"] = f"#{self.toggle_offcanvas.lstrip('#')}"
        if self.dismiss:
            attrs["data-bs-dismiss"] = self.dismiss
        if self.tooltip:
            attrs["title"] = self.tooltip
            attrs.setdefault("data-bs-toggle", "tooltip")
        return attrs

    def css_classes(self) -> list[str]:
        variant = f"btn-outline-{enum_value(self.color)}" if self.outline else f"btn-{enum_value(self.color)}"
        classes = ["btn", variant]
        if self.size:
            classes.append(f"btn-{enum_value(self.size)}")
        if self.block:
            classes.append("w-100")
        if self.active:
            classes.append("active")
        if self.disabled:
            classes.append("disabled")
        return classes

    def render_content(self) -> str:
        icon = f'<i class="{icon_name(self.icon)} me-1"></i>' if self.icon else ""
        return icon + escape(self.text)


class ButtonGroup(Node):
    """按钮组。"""

    buttons: list[NodeLike] = Field(default_factory=list)
    vertical: bool = False
    size: Size | None = None

    def css_classes(self) -> list[str]:
        classes = ["btn-group"]
        if self.vertical:
            classes.append("btn-group-vertical")
        if self.size:
            classes.append(f"btn-group-{enum_value(self.size)}")
        return classes

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("role", "group")
        return attrs

    def render_content(self) -> str:
        return render_children(self.buttons)


class CloseButton(Node):
    """关闭按钮（``.btn-close``）。"""

    TAG: ClassVar[str | None] = "button"

    dismiss: Literal["modal", "offcanvas", "alert", "toast"] = "modal"
    white: bool = False

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["type"] = "button"
        attrs["data-bs-dismiss"] = self.dismiss
        attrs["aria-label"] = "关闭"
        return attrs

    def css_classes(self) -> list[str]:
        classes = ["btn-close"]
        if self.white:
            classes.append("btn-close-white")
        return classes
