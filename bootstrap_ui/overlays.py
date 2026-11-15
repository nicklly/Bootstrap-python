"""浮层组件：Modal / Offcanvas / Toast / ToastContainer / Tooltip。"""

from __future__ import annotations

from typing import Any, ClassVar, Literal
from uuid import uuid4

from pydantic import Field

from .constants import Color, value as enum_value
from .content import icon_name
from .types import Node, NodeLike, escape, render_attrs, render_children

__all__ = ["Modal", "Offcanvas", "Toast", "ToastContainer", "Tooltip"]


class Modal(Node):
    """模态对话框。用 ``Button(toggle_modal="你的id")`` 打开。"""

    id: str = Field(default_factory=lambda: f"modal-{uuid4().hex[:6]}")
    title: str | None = None
    body: list[NodeLike] = Field(default_factory=list)
    footer: list[NodeLike] | None = None
    size: Literal["sm", "lg", "xl"] | None = None
    fullscreen: bool = False
    centered: bool = True
    scrollable: bool = False
    static_backdrop: bool = False
    close_button: bool = True

    def css_classes(self) -> list[str]:
        return ["modal", "fade"]

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("tabindex", "-1")
        attrs.setdefault("aria-hidden", "true")
        if self.title:
            attrs.setdefault("aria-labelledby", f"{self.id}-label")
        if self.static_backdrop:
            attrs["data-bs-backdrop"] = "static"
            attrs["data-bs-keyboard"] = "false"
        return attrs

    def render_content(self) -> str:
        dialog_classes = ["modal-dialog"]
        if self.size:
            dialog_classes.append(f"modal-{self.size}")
        if self.centered:
            dialog_classes.append("modal-dialog-centered")
        if self.scrollable:
            dialog_classes.append("modal-dialog-scrollable")
        if self.fullscreen:
            dialog_classes.append("modal-fullscreen")

        header = ""
        if self.title or self.close_button:
            title = (
                f'<h5 class="modal-title" id="{self.id}-label">{escape(self.title)}</h5>'
                if self.title
                else ""
            )
            close = (
                '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>'
                if self.close_button
                else ""
            )
            header = f'<div class="modal-header">{title}{close}</div>'

        footer = ""
        if self.footer:
            footer = f'<div class="modal-footer">{render_children(self.footer)}</div>'

        return (
            f'<div class="{" ".join(dialog_classes)}">'
            f'<div class="modal-content">{header}'
            f'<div class="modal-body">{render_children(self.body)}</div>'
            f"{footer}</div></div>"
        )


class Offcanvas(Node):
    """侧边抽屉。用 ``Button(toggle_offcanvas="你的id")`` 打开。"""

    id: str = Field(default_factory=lambda: f"offcanvas-{uuid4().hex[:6]}")
    title: str | None = None
    body: list[NodeLike] = Field(default_factory=list)
    footer: list[NodeLike] | None = None
    placement: Literal["start", "end", "top", "bottom"] = "start"
    close_button: bool = True
    static_backdrop: bool = False

    def css_classes(self) -> list[str]:
        return ["offcanvas", f"offcanvas-{self.placement}"]

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("tabindex", "-1")
        attrs.setdefault("aria-labelledby", f"{self.id}-label")
        if self.static_backdrop:
            attrs["data-bs-backdrop"] = "static"
            attrs["data-bs-keyboard"] = "false"
        return attrs

    def render_content(self) -> str:
        header = ""
        if self.title or self.close_button:
            title = (
                f'<h5 class="offcanvas-title" id="{self.id}-label">{escape(self.title)}</h5>'
                if self.title
                else ""
            )
            close = (
                '<button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="关闭"></button>'
                if self.close_button
                else ""
            )
            header = f'<div class="offcanvas-header">{title}{close}</div>'
        footer = (
            f'<div class="offcanvas-footer p-3 border-top">{render_children(self.footer)}</div>'
            if self.footer
            else ""
        )
        return f'{header}<div class="offcanvas-body">{render_children(self.body)}</div>{footer}'


class Toast(Node):
    """轻提示。页面脚本加载后会自动调用 ``show()``。"""

    id: str = Field(default_factory=lambda: f"toast-{uuid4().hex[:6]}")
    title: str | None = None
    body: list[NodeLike] = Field(default_factory=list)
    color: Color | None = None
    icon: str | None = None
    delay: int = 4000
    autohide: bool = True
    close_button: bool = True

    def css_classes(self) -> list[str]:
        classes = ["toast"]
        if self.color:
            classes.append(f"text-bg-{enum_value(self.color)}")
        return classes

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("role", "alert")
        attrs.setdefault("aria-live", "assertive")
        attrs.setdefault("aria-atomic", "true")
        attrs["data-bs-delay"] = self.delay
        attrs["data-bs-autohide"] = "true" if self.autohide else "false"
        return attrs

    def render_content(self) -> str:
        parts: list[str] = []
        if self.icon:
            parts.append(f'<i class="{icon_name(self.icon)} me-2"></i>')
        if self.title:
            parts.append(f'<strong class="d-block mb-1">{escape(self.title)}</strong>')
        parts.append(render_children(self.body))
        close = ""
        if self.close_button:
            close = (
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" '
                'data-bs-dismiss="toast" aria-label="关闭"></button>'
            )
        return f'<div class="d-flex"><div class="toast-body">{"".join(parts)}</div>{close}</div>'


class ToastContainer(Node):
    """Toast 的固定定位容器。"""

    children: list[NodeLike] = Field(default_factory=list)
    placement: Literal["top-start", "top-end", "bottom-start", "bottom-end"] = "bottom-end"

    def css_classes(self) -> list[str]:
        return ["toast-container", "position-fixed", "p-3", self.placement]


class Tooltip(Node):
    """带悬停提示的行内元素。"""

    TAG: ClassVar[str | None] = "span"

    text: str = ""
    content: str = ""
    placement: Literal["top", "bottom", "start", "end"] = "top"
    icon: str | None = None

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["data-bs-toggle"] = "tooltip"
        attrs["data-bs-placement"] = self.placement
        attrs["title"] = self.content
        return attrs

    def render_content(self) -> str:
        icon = f'<i class="{icon_name(self.icon)} me-1"></i>' if self.icon else ""
        return icon + escape(self.text)
