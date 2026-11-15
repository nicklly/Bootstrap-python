"""导航类组件：Navbar / Nav / NavItem / Dropdown / Pagination / Breadcrumb。"""

from __future__ import annotations

from typing import Any, ClassVar, Literal
from uuid import uuid4

from pydantic import Field

from .constants import Color, Size, value as enum_value
from .content import icon_name
from .types import Node, NodeLike, escape, render_attrs, render_children

__all__ = [
    "Navbar",
    "Nav",
    "NavItem",
    "Dropdown",
    "DropdownItem",
    "Pagination",
    "Breadcrumb",
    "BreadcrumbItem",
]


class NavItem(Node):
    """导航项，渲染为 ``<li class="nav-item"><a class="nav-link">``。"""

    TAG: ClassVar[str | None] = None

    text: str = ""
    href: str = "#"
    icon: str | None = None
    active: bool = False
    disabled: bool = False

    def render(self) -> str:
        classes = ["nav-link"]
        if self.active:
            classes.append("active")
        if self.disabled:
            classes.append("disabled")

        attrs: dict[str, Any] = {"class": " ".join(classes), "href": self.href}
        if self.active:
            attrs["aria-current"] = "page"
        if self.disabled:
            attrs["tabindex"] = "-1"
            attrs["aria-disabled"] = "true"
        if self.id:
            attrs["id"] = self.id

        icon = f'<i class="{icon_name(self.icon)} me-1"></i>' if self.icon else ""
        return f'<li class="nav-item"><a{render_attrs(attrs)}>{icon}{escape(self.text)}</a></li>'


class DropdownItem(Node):
    """下拉菜单项，``divider=True`` 时渲染为分割线。"""

    TAG: ClassVar[str | None] = None

    text: str = ""
    href: str = "#"
    active: bool = False
    disabled: bool = False
    divider: bool = False
    icon: str | None = None

    def render(self) -> str:
        if self.divider:
            return '<li><hr class="dropdown-divider"></li>'

        classes = ["dropdown-item"]
        if self.active:
            classes.append("active")
        if self.disabled:
            classes.append("disabled")

        attrs: dict[str, Any] = {"class": " ".join(classes), "href": self.href}
        if self.disabled:
            attrs["aria-disabled"] = "true"
            attrs["tabindex"] = "-1"

        icon = f'<i class="{icon_name(self.icon)} me-2"></i>' if self.icon else ""
        return f'<li><a{render_attrs(attrs)}>{icon}{escape(self.text)}</a></li>'


class Dropdown(Node):
    """下拉菜单。默认渲染为导航栏中的一项（``<li>`` 包裹）。"""

    TAG: ClassVar[str | None] = None

    text: str = ""
    items: list[DropdownItem | str] = Field(default_factory=list)
    color: Color = Color.primary
    """``as_button=True`` 时的按钮颜色"""

    as_button: bool = False
    """``True`` 时渲染为按钮样式的下拉菜单"""

    menu_end: bool = True
    dark: bool = False
    as_nav_item: bool = True

    def render(self) -> str:
        toggle_classes = ["dropdown-toggle"]
        if self.as_button:
            toggle_classes = ["btn", f"btn-{enum_value(self.color)}", "dropdown-toggle"]
        else:
            toggle_classes.insert(0, "nav-link")

        menu_classes = ["dropdown-menu", "dropdown-menu-dark" if self.dark else "dropdown-menu-end" if self.menu_end else ""]
        menu_class = " ".join(cls for cls in menu_classes if cls)

        toggle = (
            f'<a class="{" ".join(toggle_classes)}" href="#" role="button" '
            f'data-bs-toggle="dropdown" aria-expanded="false">{escape(self.text)}</a>'
        )
        items = "".join(
            item.render() if isinstance(item, DropdownItem) else DropdownItem(text=str(item)).render()
            for item in self.items
        )
        menu = f'<ul class="{menu_class}">{items}</ul>'

        if self.as_nav_item:
            return f'<li class="nav-item dropdown">{toggle}{menu}</li>'
        return f'<div class="dropdown">{toggle}{menu}</div>'


class Nav(Node):
    """独立导航（``.nav``），可用于侧边栏或标签式导航。"""

    TAG: ClassVar[str | None] = "ul"

    items: list[NavItem | Dropdown | str] = Field(default_factory=list)
    vertical: bool = False
    pills: bool = False
    fill: bool = False
    justified: bool = False

    def css_classes(self) -> list[str]:
        classes = ["nav"]
        if self.vertical:
            classes.append("flex-column")
        classes.append("nav-pills" if self.pills else "nav-tabs")
        if self.fill:
            classes.append("nav-fill")
        if self.justified:
            classes.append("nav-justified")
        return classes

    def render_content(self) -> str:
        return render_children(self.items)


class Navbar(Node):
    """顶部导航栏。"""

    TAG: ClassVar[str | None] = "nav"

    brand: str | None = None
    brand_href: str = "#"
    brand_icon: str | None = None

    items: list[NavItem | Dropdown | str] = Field(default_factory=list)
    """左侧导航项"""

    actions: list[NodeLike] = Field(default_factory=list)
    """右侧操作区（按钮、下拉菜单等）"""

    color: Color | None = None
    """``bg-{color}``，配合 ``dark=True`` 使用深色文字方案"""

    dark: bool = False
    expand: Literal["sm", "md", "lg", "xl", "xxl", False] = "lg"
    sticky: bool = False
    container: bool = True
    fluid: bool = True
    id: str = Field(default_factory=lambda: f"navbar-{uuid4().hex[:6]}")

    def css_classes(self) -> list[str]:
        classes = ["navbar"]
        if self.color:
            classes.append(f"bg-{enum_value(self.color)}")
        else:
            classes.append("bg-body-tertiary")
        if self.dark or self.color in {Color.dark, Color.primary}:
            classes.append("navbar-dark")
        if self.sticky:
            classes.append("sticky-top")
        if self.expand:
            classes.append(f"navbar-expand-{self.expand}")
        else:
            classes.append("navbar-expand")
        return classes

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("data-bs-theme", "dark" if (self.dark or self.color in {Color.dark, Color.primary}) else "light")
        return attrs

    def render_content(self) -> str:
        collapse_id = f"{self.id}-nav"
        brand_icon = f'<i class="{icon_name(self.brand_icon)} me-2"></i>' if self.brand_icon else ""
        brand = (
            f'<a class="navbar-brand" href="{escape(self.brand_href)}">{brand_icon}{escape(self.brand)}</a>'
            if self.brand
            else ""
        )
        toggler = (
            '<button class="navbar-toggler" type="button" data-bs-toggle="collapse" '
            f'data-bs-target="#{collapse_id}" aria-controls="{collapse_id}" '
            'aria-expanded="false" aria-label="切换导航"><span class="navbar-toggler-icon"></span></button>'
        )
        items = render_children(self.items)
        actions = render_children(self.actions)
        actions_html = f'<div class="d-flex align-items-center gap-2">{actions}</div>' if actions else ""

        inner = (
            f"{brand}{toggler}"
            f'<div class="collapse navbar-collapse" id="{collapse_id}">'
            f'<ul class="navbar-nav me-auto mb-2 mb-lg-0">{items}</ul>'
            f"{actions_html}</div>"
        )
        if self.container:
            wrapper = "container-fluid" if self.fluid else "container"
            inner = f'<div class="{wrapper}">{inner}</div>'
        return inner


class BreadcrumbItem(Node):
    """面包屑中的一项。"""

    TAG: ClassVar[str | None] = None

    text: str = ""
    href: str | None = None
    active: bool = False

    def render(self) -> str:
        classes = ["breadcrumb-item"]
        if self.active:
            classes.append("active")
        if self.href and not self.active:
            body = f'<a href="{escape(self.href)}">{escape(self.text)}</a>'
        else:
            body = escape(self.text)
        return f'<li class="{" ".join(classes)}">{body}</li>'


class Breadcrumb(Node):
    """面包屑导航。"""

    TAG: ClassVar[str | None] = "nav"

    items: list[BreadcrumbItem | str] = Field(default_factory=list)

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("aria-label", "breadcrumb")
        return attrs

    def render_content(self) -> str:
        nodes: list[str] = []
        for index, item in enumerate(self.items):
            if isinstance(item, BreadcrumbItem):
                node = item
            else:
                node = BreadcrumbItem(text=str(item))
            node.active = node.active or index == len(self.items) - 1
            nodes.append(node.render())
        return f'<ol class="breadcrumb mb-0">{"".join(nodes)}</ol>'


class Pagination(Node):
    """分页导航。"""

    TAG: ClassVar[str | None] = "nav"

    current: int = 1
    total: int = 1
    href: str = "?page={page}"
    """页码链接模板，``{page}`` 会被替换"""

    size: Size | None = None
    max_buttons: int = 7
    show_edges: bool = True
    align: Literal["start", "center", "end"] = "center"

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("aria-label", "分页")
        return attrs

    def _page_item(self, page: int, label: str, *, active: bool = False, disabled: bool = False) -> str:
        classes = ["page-item"]
        if active:
            classes.append("active")
        if disabled:
            classes.append("disabled")

        if active:
            inner = f'<span class="page-link">{escape(label)}</span>'
        elif disabled:
            inner = f'<span class="page-link">{escape(label)}</span>'
        else:
            inner = f'<a class="page-link" href="{escape(self.href.format(page=page))}">{escape(label)}</a>'
        return f'<li class="{" ".join(classes)}">{inner}</li>'

    def _window(self) -> list[int | None]:
        total = max(self.total, 1)
        current = min(max(self.current, 1), total)
        limit = max(self.max_buttons, 5)
        if total <= limit:
            return list(range(1, total + 1))

        half = (limit - 3) // 2
        start = max(2, current - half)
        end = min(total - 1, start + (limit - 3) - 1)
        start = max(2, end - (limit - 3) + 1)

        pages: list[int | None] = [1]
        if start > 2:
            pages.append(None)
        pages.extend(range(start, end + 1))
        if end < total - 1:
            pages.append(None)
        pages.append(total)
        return pages

    def render_content(self) -> str:
        total = max(self.total, 1)
        current = min(max(self.current, 1), total)
        parts: list[str] = []

        if self.show_edges:
            parts.append(self._page_item(1, "«", disabled=current == 1))
        parts.append(self._page_item(current - 1, "‹", disabled=current == 1))

        for page in self._window():
            if page is None:
                parts.append('<li class="page-item disabled"><span class="page-link">…</span></li>')
            else:
                parts.append(self._page_item(page, str(page), active=page == current))

        parts.append(self._page_item(current + 1, "›", disabled=current == total))
        if self.show_edges:
            parts.append(self._page_item(total, "»", disabled=current == total))

        size_class = f" pagination-{enum_value(self.size)}" if self.size else ""
        justify = {
            "start": "justify-content-start",
            "center": "justify-content-center",
            "end": "justify-content-end",
        }[self.align]
        return f'<ul class="pagination {justify}{size_class}">{"".join(parts)}</ul>'
