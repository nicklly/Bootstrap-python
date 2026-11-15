"""Bootstrap 5 的枚举常量。

覆盖场景固定、取值封闭的属性（颜色、尺寸、断点等）；对于 text-* 这类可扩展的
颜色值，组件里直接用 ``str``，以便使用 ``body-secondary`` 等额外取值。
"""

from __future__ import annotations

from enum import Enum
from typing import Any

__all__ = [
    "Color",
    "Size",
    "Alignment",
    "Justify",
    "Placement",
    "Breakpoint",
    "value",
]


class Color(str, Enum):
    """Bootstrap 主题色。"""

    primary = "primary"
    secondary = "secondary"
    success = "success"
    danger = "danger"
    warning = "warning"
    info = "info"
    light = "light"
    dark = "dark"


class Size(str, Enum):
    """控件尺寸。"""

    sm = "sm"
    lg = "lg"


class Alignment(str, Enum):
    """交叉轴对齐（align-items-*）。"""

    start = "start"
    center = "center"
    end = "end"
    baseline = "baseline"
    stretch = "stretch"


class Justify(str, Enum):
    """主轴分布（justify-content-*）。"""

    start = "start"
    center = "center"
    end = "end"
    between = "between"
    around = "around"
    evenly = "evenly"


class Placement(str, Enum):
    """浮层出现位置。"""

    start = "start"
    end = "end"
    top = "top"
    bottom = "bottom"


class Breakpoint(str, Enum):
    """响应式断点。"""

    sm = "sm"
    md = "md"
    lg = "lg"
    xl = "xl"
    xxl = "xxl"


def value(item: Any) -> Any:
    """取出枚举的值，非枚举原样返回。"""
    return item.value if isinstance(item, Enum) else item
