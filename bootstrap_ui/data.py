"""数据展示组件：Table / Progress / Spinner / Accordion / Tabs / Carousel。"""

from __future__ import annotations

from typing import Any, ClassVar, Literal
from uuid import uuid4

from pydantic import Field

from .constants import Color, value as enum_value
from .content import icon_name
from .types import Node, NodeLike, escape, render_attrs, render_children

__all__ = [
    "TableColumn",
    "Table",
    "Progress",
    "Spinner",
    "AccordionItem",
    "Accordion",
    "TabItem",
    "Tabs",
    "CarouselItem",
    "Carousel",
]


class TableColumn(Node):
    """表格列定义。"""

    TAG: ClassVar[str | None] = None

    label: str = ""
    key: str | None = None
    """从字典行里取值的键名，缺省用 ``label``"""

    width: int | str | None = None
    align: Literal["start", "center", "end"] | None = None
    nowrap: bool = False


class Table(Node):
    """数据表格。行可以是「列表的列表」，也可以是「字典的列表」。"""

    columns: list[TableColumn | str] = Field(default_factory=list)
    rows: list[Any] = Field(default_factory=list)
    caption: str | None = None
    footer: list[Any] | None = None
    """汇总行单元格"""

    striped: bool = False
    hover: bool = True
    bordered: bool = False
    borderless: bool = False
    small: bool = False
    responsive: bool = True
    vertical_align: Literal["top", "middle", "bottom"] | None = "middle"
    empty_text: str = "暂无数据"

    def _columns(self) -> list[TableColumn]:
        if self.columns:
            return [
                column if isinstance(column, TableColumn) else TableColumn(label=str(column))
                for column in self.columns
            ]
        # 没有显式列定义时，用第一行字典的键推导
        first = self.rows[0] if self.rows else None
        if isinstance(first, dict):
            return [TableColumn(label=str(key), key=str(key)) for key in first]
        return []

    def css_classes(self) -> list[str]:
        classes = ["table"]
        if self.striped:
            classes.append("table-striped")
        if self.hover:
            classes.append("table-hover")
        if self.bordered:
            classes.append("table-bordered")
        if self.borderless:
            classes.append("table-borderless")
        if self.small:
            classes.append("table-sm")
        if self.vertical_align:
            classes.append(f"align-{self.vertical_align}")
        return classes

    def _cell(self, value: Any, column: TableColumn, tag: str = "td") -> str:
        if isinstance(value, Node):
            inner = value.render()
        elif value is None:
            inner = ""
        else:
            inner = escape(value)
        classes: list[str] = []
        if column.align == "center":
            classes.append("text-center")
        elif column.align == "end":
            classes.append("text-end")
        if column.nowrap:
            classes.append("text-nowrap")
        attrs = f' class="{" ".join(classes)}"' if classes else ""
        return f"<{tag}{attrs}>{inner}</{tag}>"

    def render_content(self) -> str:
        columns = self._columns()
        head_cells = []
        for column in columns:
            attrs: dict[str, Any] = {"scope": "col"}
            if column.width is not None:
                attrs["style"] = f"width: {column.width}px" if isinstance(column.width, int) else f"width: {column.width}"
            head_cells.append(f"<th{render_attrs(attrs)}>{escape(column.label)}</th>")
        head = f'<thead><tr>{"".join(head_cells)}</tr></thead>'

        body_rows: list[str] = []
        for row in self.rows:
            if isinstance(row, dict):
                cells = [self._cell(row.get(column.key or column.label), column) for column in columns]
            elif isinstance(row, (list, tuple)):
                cells = [
                    self._cell(row[index] if index < len(row) else None, column)
                    for index, column in enumerate(columns)
                ]
            else:  # 单值行
                cells = [self._cell(row, columns[0])] if columns else []
            body_rows.append(f"<tr>{''.join(cells)}</tr>")

        if not body_rows:
            colspan = max(len(columns), 1)
            body_rows.append(
                f'<tr><td colspan="{colspan}" class="text-center text-body-secondary py-4">'
                f"{escape(self.empty_text)}</td></tr>"
            )
        body = f"<tbody>{''.join(body_rows)}</tbody>"

        foot = ""
        if self.footer:
            cells = [
                self._cell(value, columns[index] if index < len(columns) else TableColumn(), "th")
                for index, value in enumerate(self.footer)
            ]
            foot = f"<tfoot><tr>{''.join(cells)}</tr></tfoot>"

        caption = f"<caption>{escape(self.caption)}</caption>" if self.caption else ""
        table = f'<table{render_attrs(self.html_attrs())}>{caption}{head}{body}{foot}</table>'
        if self.responsive:
            return f'<div class="table-responsive">{table}</div>'
        return table

    def render(self) -> str:
        return self.render_content()


class Progress(Node):
    """进度条。"""

    value: float = 0
    max: float = 100
    color: Color | None = Color.primary
    height: str | None = None
    striped: bool = False
    animated: bool = False
    show_value: bool = True
    label: str | None = None

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("role", "progressbar")
        attrs["aria-valuenow"] = self.value
        attrs["aria-valuemin"] = 0
        attrs["aria-valuemax"] = self.max
        if self.height:
            attrs["style"] = f"height: {self.height}" + (f"; {attrs['style']}" if "style" in attrs else "")
        return attrs

    def css_classes(self) -> list[str]:
        return ["progress"]

    def render_content(self) -> str:
        total = self.max or 100
        percent = 0 if total <= 0 else min(max(self.value / total * 100, 0), 100)
        classes = ["progress-bar"]
        if self.color:
            classes.append(f"bg-{enum_value(self.color)}")
        if self.striped:
            classes.append("progress-bar-striped")
        if self.animated:
            classes.append("progress-bar-animated")
        label = self.label if self.label is not None else (f"{percent:.0f}%" if self.show_value else "")
        return f'<div class="{" ".join(classes)}" style="width: {percent:.1f}%">{escape(label)}</div>'


class Spinner(Node):
    """加载指示器。"""

    kind: Literal["border", "grow"] = "border"
    color: Color | None = None
    small: bool = False
    label: str | None = None

    def css_classes(self) -> list[str]:
        classes = [f"spinner-{self.kind}"]
        if self.small:
            classes.append(f"spinner-{self.kind}-sm")
        if self.color:
            classes.append(f"text-{enum_value(self.color)}")
        return classes

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs.setdefault("role", "status")
        return attrs

    def render_content(self) -> str:
        hidden = f'<span class="visually-hidden">{escape(self.label or "加载中…")}</span>'
        if self.label:
            return f'{hidden}<span class="ms-2">{escape(self.label)}</span>'
        return hidden


class AccordionItem(Node):
    """折叠面板中的一项。"""

    TAG: ClassVar[str | None] = None

    title: str = ""
    body: list[NodeLike] = Field(default_factory=list)
    expanded: bool = False


class Accordion(Node):
    """折叠面板组。"""

    id: str = Field(default_factory=lambda: f"accordion-{uuid4().hex[:6]}")
    items: list[AccordionItem] = Field(default_factory=list)
    flush: bool = False
    always_open: bool = False
    """``True`` 时允许多个面板同时展开"""

    def css_classes(self) -> list[str]:
        classes = ["accordion"]
        if self.flush:
            classes.append("accordion-flush")
        return classes

    def render_content(self) -> str:
        parts: list[str] = []
        for index, item in enumerate(self.items):
            item_id = f"{self.id}-item-{index}"
            expanded = item.expanded or (index == 0 and not any(i.expanded for i in self.items))
            button_classes = "accordion-button" + ("" if expanded else " collapsed")
            body_classes = "accordion-collapse collapse" + (" show" if expanded else "")
            parent = "" if self.always_open else f' data-bs-parent="#{self.id}"'
            parts.append(
                '<div class="accordion-item">'
                f'<h2 class="accordion-header" id="{item_id}-header">'
                f'<button class="{button_classes}" type="button" data-bs-toggle="collapse" '
                f'data-bs-target="#{item_id}-body" aria-expanded="{"true" if expanded else "false"}" '
                f'aria-controls="{item_id}-body">{escape(item.title)}</button></h2>'
                f'<div id="{item_id}-body" class="{body_classes}" aria-labelledby="{item_id}-header"{parent}>'
                f'<div class="accordion-body">{render_children(item.body)}</div></div></div>'
            )
        return "".join(parts)


class TabItem(Node):
    """标签页中的一页。"""

    TAG: ClassVar[str | None] = None

    label: str = ""
    body: list[NodeLike] = Field(default_factory=list)
    icon: str | None = None
    active: bool = False
    disabled: bool = False


class Tabs(Node):
    """标签页（Bootstrap nav-tabs + tab-content）。"""

    id: str = Field(default_factory=lambda: f"tabs-{uuid4().hex[:6]}")
    items: list[TabItem] = Field(default_factory=list)
    pill: bool = False
    fade: bool = True
    vertical: bool = False

    def _is_active(self, index: int) -> bool:
        if any(item.active for item in self.items):
            return self.items[index].active
        return index == 0

    def render_content(self) -> str:
        nav_classes = "nav nav-pills flex-column me-3" if self.vertical else ("nav nav-pills" if self.pill else "nav nav-tabs")
        if not self.vertical:
            nav_classes += " mb-3"
        nav_links: list[str] = []
        panes: list[str] = []

        for index, item in enumerate(self.items):
            tab_id = f"{self.id}-tab-{index}"
            pane_id = f"{self.id}-pane-{index}"
            active = self._is_active(index)
            link_classes = ["nav-link"]
            if active:
                link_classes.append("active")
            if item.disabled:
                link_classes.append("disabled")
            icon = f'<i class="{icon_name(item.icon)} me-1"></i>' if item.icon else ""
            nav_links.append(
                f'<li class="nav-item" role="presentation">'
                f'<button class="{" ".join(link_classes)}" id="{tab_id}" type="button" '
                f'data-bs-toggle="tab" data-bs-target="#{pane_id}" role="tab" '
                f'aria-controls="{pane_id}" aria-selected="{"true" if active else "false"}"'
                f'{" disabled" if item.disabled else ""}>{icon}{escape(item.label)}</button></li>'
            )
            pane_classes = ["tab-pane"]
            if self.fade:
                pane_classes.append("fade")
            if active:
                pane_classes.append("show active")
            panes.append(
                f'<div class="{" ".join(pane_classes)}" id="{pane_id}" role="tabpanel" '
                f'aria-labelledby="{tab_id}" tabindex="0">{render_children(item.body)}</div>'
            )

        nav = f'<ul class="{nav_classes}" role="tablist">{ "".join(nav_links) }</ul>'
        content = f'<div class="tab-content flex-grow-1">{"".join(panes)}</div>'
        if self.vertical:
            return f'<div class="d-flex align-items-start">{nav}{content}</div>'
        return f"{nav}{content}"

    def html_attrs(self) -> dict[str, Any]:
        return {k: v for k, v in super().html_attrs().items() if k in {"id", "class", "style", "data-bs-theme"}}

    def render(self) -> str:
        attrs = render_attrs(self.html_attrs())
        if attrs:
            return f"<div{attrs}>{self.render_content()}</div>"
        return self.render_content()


class CarouselItem(Node):
    """轮播中的一张。"""

    TAG: ClassVar[str | None] = None

    image: str = ""
    title: str | None = None
    text: str | None = None
    alt: str = ""
    active: bool = False


class Carousel(Node):
    """轮播图。"""

    id: str = Field(default_factory=lambda: f"carousel-{uuid4().hex[:6]}")
    items: list[CarouselItem] = Field(default_factory=list)
    controls: bool = True
    indicators: bool = True
    interval: int = 5000
    fade: bool = False
    height: str | None = "20rem"

    def render_content(self) -> str:
        slides: list[str] = []
        dots: list[str] = []
        for index, item in enumerate(self.items):
            active = item.active or (index == 0 and not any(i.active for i in self.items))
            active_class = " active" if active else ""
            caption = ""
            if item.title or item.text:
                title = f"<h5>{escape(item.title)}</h5>" if item.title else ""
                text = f'<p class="mb-0">{escape(item.text)}</p>' if item.text else ""
                caption = f'<div class="carousel-caption d-none d-md-block">{title}{text}</div>'
            image_style = f' style="object-fit: cover; height: {self.height};"' if self.height else ""
            slides.append(
                f'<div class="carousel-item{active_class}">'
                f'<img src="{escape(item.image)}" class="d-block w-100" alt="{escape(item.alt)}"{image_style}>'
                f"{caption}</div>"
            )
            dots.append(
                f'<li data-bs-target="#{self.id}" data-bs-slide-to="{index}" class="{active_class.strip()}"></li>'
            )

        indicators_html = (
            f'<div class="carousel-indicators">{"".join(dots)}</div>' if self.indicators else ""
        )
        controls_html = (
            f'<button class="carousel-control-prev" type="button" data-bs-target="#{self.id}" data-bs-slide="prev">'
            f'<span class="carousel-control-prev-icon" aria-hidden="true"></span>'
            f'<span class="visually-hidden">上一张</span></button>'
            f'<button class="carousel-control-next" type="button" data-bs-target="#{self.id}" data-bs-slide="next">'
            f'<span class="carousel-control-next-icon" aria-hidden="true"></span>'
            f'<span class="visually-hidden">下一张</span></button>'
            if self.controls
            else ""
        )
        return indicators_html + f'<div class="carousel-inner">{"".join(slides)}</div>' + controls_html

    def css_classes(self) -> list[str]:
        classes = ["carousel", "slide"]
        if self.fade:
            classes.append("carousel-fade")
        return classes

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["data-bs-ride"] = "carousel"
        attrs["data-bs-interval"] = self.interval
        return attrs
