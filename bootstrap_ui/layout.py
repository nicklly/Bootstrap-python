"""页面与栅格布局组件：Page / Container / Row / Col / Stack / Hr。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Literal

from jinja2 import Environment, FileSystemLoader
from pydantic import Field

from .types import Node, NodeLike, escape, render_children

__all__ = ["Page", "Container", "Row", "Col", "Stack", "Hr", "Box", "Fragment"]

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=False,          # 内容在 Python 侧已经渲染并转义过，这里不能二次转义
    trim_blocks=True,
    lstrip_blocks=True,
)


class Page(Node):
    """完整的 HTML 页面（``<html>`` 文档），是渲染的入口。"""

    TAG: ClassVar[str | None] = None
    __default_template_path__: ClassVar[str] = "page.jinja2"

    title: str = "Bootstrap"
    """浏览器标题"""

    lang: str = "zh-CN"
    """``<html lang>``"""

    body: list[NodeLike] = Field(default_factory=list)
    """页面主体内容"""

    navbar: NodeLike | None = None
    """顶部导航栏（一般传 :class:`~bootstrap.nav.Navbar`）"""

    footer: NodeLike | None = None
    """页脚内容"""

    toolbar: NodeLike | None = None
    """主体内容上方的工具条（标题 + 按钮之类）"""

    container: bool = True
    """是否用容器包裹主体内容"""

    fluid: bool = False
    """容器是否全宽"""

    body_class: str | None = None
    """``<body>`` 的 class"""

    theme: Literal["light", "dark", "auto"] | None = None
    """Bootstrap 5.3 的 ``data-bs-theme``，用于内置暗色模式"""

    version: str = "5.3.3"
    """Bootstrap 版本号"""

    cdn: str = "https://cdn.jsdelivr.net/npm"
    """资源 CDN 前缀"""

    icons: bool = True
    """是否引入 bootstrap-icons"""

    icons_version: str = "1.11.3"
    """bootstrap-icons 版本号"""

    css: list[str] = Field(default_factory=list)
    """额外样式表地址"""

    js: list[str] = Field(default_factory=list)
    """额外脚本地址"""

    custom_css: str | None = None
    """内联样式"""

    custom_js: str | None = None
    """内联脚本（在 Bootstrap bundle 之后执行）"""

    head: str | None = None
    """原样插入 ``<head>`` 末尾的内容"""

    def render(self, template_name: str = "") -> str:
        """用 jinja2 模板渲染完整页面。"""
        template = _env.get_template(template_name or self.__default_template_path__)
        return template.render(
            lang=escape(self.lang),
            theme=self.theme,
            title=escape(self.title),
            icons=self.icons,
            icons_version=self.icons_version,
            cdn=self.cdn.rstrip("/"),
            version=self.version,
            css=self.css,
            page_css=self.custom_css or "",
            body_class=escape(self.body_class or ""),
            navbar=self.navbar.render() if isinstance(self.navbar, Node) else "",
            toolbar=render_children(self.toolbar, "\n") if self.toolbar is not None else "",
            body=render_children(self.body, "\n"),
            footer=self.footer.render() if isinstance(self.footer, Node) else "",
            js=self.js,
            page_js=self.custom_js or "",
            container=self.container,
            container_class="container-fluid" if self.fluid else "container",
            head=self.head or "",
        )

    def save(self, path: str | Path, encoding: str = "utf-8") -> Path:
        """把渲染结果写入文件。"""
        target = Path(path)
        target.write_text(self.render(), encoding=encoding)
        return target


class Container(Node):
    """固定宽度（或响应式）的内容容器。"""

    fluid: bool | Literal["sm", "md", "lg", "xl", "xxl"] = False
    """``True`` 全宽；字符串表示 ``container-{断点}``"""

    children: list[NodeLike] = Field(default_factory=list)

    def css_classes(self) -> list[str]:
        if self.fluid is True:
            return ["container-fluid"]
        if isinstance(self.fluid, str):
            return [f"container-{self.fluid}"]
        return ["container"]

    def render_content(self) -> str:
        return render_children(self.children, "\n")


class Row(Node):
    """栅格行（``.row``）。"""

    children: list[NodeLike] = Field(default_factory=list)

    gutter: int | str | None = None
    """列间距，渲染为 ``g-{gutter}``，如 3"""

    align: Literal["start", "center", "end", "baseline", "stretch"] | None = None
    """垂直对齐（align-items-*）"""

    justify: Literal["start", "center", "end", "between", "around", "evenly"] | None = None
    """水平分布（justify-content-*）"""

    cols: int | str | None = None
    """每行固定列数，渲染为 ``row-cols-{cols}``"""

    def css_classes(self) -> list[str]:
        classes = ["row"]
        if self.gutter is not None:
            classes.append(f"g-{self.gutter}")
        if self.align:
            classes.append(f"align-items-{self.align}")
        if self.justify:
            classes.append(f"justify-content-{self.justify}")
        if self.cols is not None:
            classes.append(f"row-cols-{self.cols}")
        return classes

    def render_content(self) -> str:
        return render_children(self.children, "\n")


class Col(Node):
    """栅格列（``.col``）。"""

    body: list[NodeLike] = Field(default_factory=list)

    width: int | str | None = None
    """默认宽度，1-12 或 ``auto``"""

    xs: int | str | None = None
    sm: int | str | None = None
    md: int | str | None = None
    lg: int | str | None = None
    xl: int | str | None = None
    xxl: int | str | None = None
    """各断点下的宽度"""

    offset: int | None = None
    """左侧偏移列数"""

    align_self: Literal["start", "center", "end", "baseline", "stretch"] | None = None
    """列自身在行内的垂直对齐"""

    def css_classes(self) -> list[str]:
        classes: list[str] = []
        if self.width is not None:
            classes.append(f"col-{self.width}")
        for breakpoint in ("xs", "sm", "md", "lg", "xl", "xxl"):
            item = getattr(self, breakpoint)
            if item is not None:
                classes.append(f"col-{breakpoint}-{item}")
        if self.offset is not None:
            classes.append(f"offset-{self.offset}")
        if self.align_self:
            classes.append(f"align-self-{self.align_self}")
        if not classes:
            classes.append("col")
        return classes

    def render_content(self) -> str:
        return render_children(self.body, "\n")


class Stack(Node):
    """垂直 / 水平堆叠（``.vstack`` / ``.hstack``）。"""

    direction: Literal["vertical", "horizontal"] = "vertical"

    gap: int | str | None = 3
    """间距，渲染为 ``gap-{gap}``"""

    children: list[NodeLike] = Field(default_factory=list)

    def css_classes(self) -> list[str]:
        classes = ["vstack" if self.direction == "vertical" else "hstack"]
        if self.gap is not None:
            classes.append(f"gap-{self.gap}")
        return classes

    def render_content(self) -> str:
        return render_children(self.children, "\n")


class Hr(Node):
    """分割线。"""

    TAG: ClassVar[str | None] = "hr"

    def css_classes(self) -> list[str]:
        return ["my-4"]


class Box(Node):
    """通用 div 容器，用来套用工具类或行内样式。"""

    children: list[NodeLike] = Field(default_factory=list)

    def render_content(self) -> str:
        return render_children(self.children, "\n")


class Fragment(Node):
    """不产生包裹标签的片段，用于把多个节点当成一个整体传入。"""

    TAG: ClassVar[str | None] = None

    children: list[NodeLike] = Field(default_factory=list)

    def render(self) -> str:
        return render_children(self.children, "\n")
