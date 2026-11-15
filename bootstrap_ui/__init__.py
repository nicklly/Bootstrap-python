"""bootstrap-python：用 pydantic 模型描述 Bootstrap 5 界面，并渲染成 HTML。

快速开始::

    from bootstrap_ui import Page, Card, Table, Badge

    page = Page(title="示例", body=[
        Card(title="用户", body=[
            Table(columns=["ID", "姓名"], rows=[[1, "张三"], [2, "李四"]]),
        ]),
    ])
    print(page.render())

三个输出入口：``to_dict()``（结构化描述）、``to_json()``、``render()``（HTML）。
"""

from __future__ import annotations

__version__ = "0.1.0"

from .constants import Alignment, Breakpoint, Color, Justify, Placement, Size
from .types import Node, NodeLike, RawHtml, render_attrs, render_children, raw

from .layout import Box, Col, Container, Fragment, Hr, Page, Row, Stack
from .content import (
    Alert,
    Badge,
    Button,
    ButtonGroup,
    Card,
    CloseButton,
    Heading,
    Icon,
    Image,
    Link,
    ListGroup,
    ListItem,
    Paragraph,
    Small,
    Span,
    Strong,
)
from .nav import (
    Breadcrumb,
    BreadcrumbItem,
    Dropdown,
    DropdownItem,
    Nav,
    Navbar,
    NavItem,
    Pagination,
)
from .data import (
    Accordion,
    AccordionItem,
    Carousel,
    CarouselItem,
    Progress,
    Spinner,
    TabItem,
    Table,
    TableColumn,
    Tabs,
)
from .overlays import Modal, Offcanvas, Toast, ToastContainer, Tooltip
from .forms import (
    Checkbox,
    Fieldset,
    Form,
    FormGroup,
    Hidden,
    Input,
    InputGroup,
    Label,
    RadioGroup,
    Select,
    Textarea,
    field,
)

__all__ = [
    "__version__",
    # 内核
    "Node",
    "NodeLike",
    "RawHtml",
    "raw",
    "render_attrs",
    "render_children",
    # 常量
    "Color",
    "Size",
    "Alignment",
    "Justify",
    "Placement",
    "Breakpoint",
    # 布局
    "Page",
    "Container",
    "Row",
    "Col",
    "Stack",
    "Hr",
    "Box",
    "Fragment",
    # 内容
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
    # 导航
    "Navbar",
    "Nav",
    "NavItem",
    "Dropdown",
    "DropdownItem",
    "Breadcrumb",
    "BreadcrumbItem",
    "Pagination",
    # 数据
    "Table",
    "TableColumn",
    "Progress",
    "Spinner",
    "Accordion",
    "AccordionItem",
    "Tabs",
    "TabItem",
    "Carousel",
    "CarouselItem",
    # 浮层
    "Modal",
    "Offcanvas",
    "Toast",
    "ToastContainer",
    "Tooltip",
    # 表单
    "Form",
    "FormGroup",
    "field",
    "Label",
    "Input",
    "Textarea",
    "Select",
    "Checkbox",
    "RadioGroup",
    "InputGroup",
    "Fieldset",
    "Hidden",
]
