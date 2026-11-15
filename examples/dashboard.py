"""bootstrap-python 演示：一个用 Python 组件描述、渲染成 Bootstrap 5 的后台页面。

运行（在仓库根目录）::

    python examples/dashboard.py        # 生成 examples/dashboard.html

页面覆盖：导航栏、面包屑、统计卡片、标签页表格、列表组、折叠面板、模态框、抽屉、
分页、进度条、Toast、提示气泡等常见组合。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bootstrap_ui import (
    Accordion,
    AccordionItem,
    Alert,
    Badge,
    Box,
    Breadcrumb,
    BreadcrumbItem,
    Button,
    ButtonGroup,
    Card,
    Checkbox,
    Col,
    Color,
    Dropdown,
    DropdownItem,
    Form,
    FormGroup,
    Heading,
    Hr,
    Icon,
    Input,
    InputGroup,
    ListGroup,
    ListItem,
    Modal,
    Navbar,
    NavItem,
    Offcanvas,
    Page,
    Pagination,
    Progress,
    RadioGroup,
    Row,
    Select,
    Small,
    Span,
    Stack,
    Table,
    TableColumn,
    Tabs,
    TabItem,
    Textarea,
    Toast,
    ToastContainer,
    Tooltip,
)

# ---------------------------------------------------------------- 小组件（组合现有组件）


def avatar(letter: str, color: str = "primary") -> Box:
    """圆形头像占位。"""
    return Box(
        class_name=(
            f"rounded-circle bg-{color}-subtle text-{color} d-flex align-items-center "
            "justify-content-center fw-semibold flex-shrink-0"
        ),
        style={"width": "2rem", "height": "2rem", "font-size": ".85rem"},
        children=[letter],
    )


def user_cell(name: str, letter: str, color: str = "primary") -> Box:
    return Box(
        class_name="d-flex align-items-center gap-2",
        children=[avatar(letter, color), Span(text=name, weight="semibold")],
    )


def status_badge(status: str) -> Badge:
    colors = {"正常": Color.success, "待审核": Color.warning, "已停用": Color.secondary}
    return Badge(text=status, color=colors.get(status, Color.secondary), pill=True)


def stat_card(title: str, value: str, icon: str, color: str, delta: str, up: bool = True, percent: int = 60):
    """统计卡片：图标 + 数值 + 环比 + 进度条。"""
    return Col(
        md=6,
        xl=3,
        body=[
            Card(
                body=[
                    Stack(
                        direction="horizontal",
                        gap=3,
                        children=[
                            Box(
                                class_name=(
                                    f"d-flex align-items-center justify-content-center rounded-3 "
                                    f"bg-{color} bg-opacity-10 text-{color}"
                                ),
                                style={"width": "3rem", "height": "3rem"},
                                children=[Icon(name=icon, size="1.35rem")],
                            ),
                            Box(
                                children=[
                                    Span(text=title, color="body-secondary"),
                                    Heading(text=value, level=3, size="4", class_name="mb-0"),
                                ]
                            ),
                        ],
                    ),
                    Hr(class_name="my-3"),
                    Box(
                        class_name="d-flex justify-content-between align-items-center",
                        children=[
                            Span(
                                text=delta,
                                color="success" if up else "danger",
                                weight="semibold",
                                body=[Icon(name="arrow-up-short" if up else "arrow-down-short")],
                            ),
                            Small(text="较上周"),
                        ],
                    ),
                    Progress(
                        value=percent,
                        color=Color(color),
                        height="4px",
                        show_value=False,
                        class_name="mt-2",
                    ),
                ]
            )
        ],
    )


# ---------------------------------------------------------------- 表格数据

ORDER_COLUMNS = [
    TableColumn(label="订单号", key="no"),
    TableColumn(label="客户", key="customer"),
    TableColumn(label="金额", key="amount", align="end"),
    TableColumn(label="状态", key="status", align="center"),
    TableColumn(label="下单时间", key="time", width=160),
]

ORDERS = [
    {"no": "#A-1042", "customer": "张伟", "amount": "¥ 1,280.00", "status": status_badge("正常"), "time": "11-15 09:12"},
    {"no": "#A-1041", "customer": "李娜", "amount": "¥ 620.00", "status": status_badge("待审核"), "time": "11-15 08:47"},
    {"no": "#A-1040", "customer": "王强", "amount": "¥ 3,450.00", "status": status_badge("正常"), "time": "11-14 21:05"},
    {"no": "#A-1039", "customer": "刘洋", "amount": "¥ 99.00", "status": status_badge("已停用"), "time": "11-14 19:33"},
    {"no": "#A-1038", "customer": "陈静", "amount": "¥ 780.00", "status": status_badge("正常"), "time": "11-14 16:20"},
]

PRODUCT_COLUMNS = [
    TableColumn(label="商品", key="name"),
    TableColumn(label="销量", key="sold", align="end", width=100),
    TableColumn(label="库存占比", key="stock", width=220),
]

PRODUCTS = [
    {"name": "机械键盘 K8", "sold": "1,204", "stock": Progress(value=72, color=Color.success, height="6px", show_value=False)},
    {"name": "无线鼠标 M3", "sold": "986", "stock": Progress(value=54, color=Color.primary, height="6px", show_value=False)},
    {"name": "显示器支架", "sold": "512", "stock": Progress(value=31, color=Color.warning, height="6px", show_value=False)},
    {"name": "USB-C 扩展坞", "sold": "318", "stock": Progress(value=12, color=Color.danger, height="6px", show_value=False)},
]

REGION_COLUMNS = [
    TableColumn(label="地区", key="region"),
    TableColumn(label="订单数", key="count", align="end", width=100),
    TableColumn(label="占比", key="share", width=220),
]

REGIONS = [
    {"region": "华东", "count": "482", "share": Progress(value=42, height="6px", show_value=False)},
    {"region": "华南", "count": "316", "share": Progress(value=28, color=Color.info, height="6px", show_value=False)},
    {"region": "华北", "count": "204", "share": Progress(value=18, color=Color.warning, height="6px", show_value=False)},
    {"region": "其他", "count": "126", "share": Progress(value=12, color=Color.secondary, height="6px", show_value=False)},
]

USER_COLUMNS = [
    TableColumn(label="用户", key="user"),
    TableColumn(label="邮箱", key="email"),
    TableColumn(label="角色", key="role", align="center", width=100),
    TableColumn(label="状态", key="status", align="center", width=100),
    TableColumn(
        label="最后登录",
        key="last",
        width=150,
    ),
    TableColumn(label="操作", key="action", align="end", width=150, nowrap=True),
]

USERS = [
    {
        "user": user_cell("张伟", "张"),
        "email": "zhang.wei@acme.com",
        "role": "管理员",
        "status": status_badge("正常"),
        "last": "11-15 09:12",
        "action": ButtonGroup(
            buttons=[
                Button(text="编辑", size="sm", color=Color.light, icon="pencil", toggle_modal="user-modal"),
                Button(text="更多", size="sm", color=Color.light, icon="three-dots", tooltip="更多操作"),
            ]
        ),
    },
    {
        "user": user_cell("李娜", "李", "success"),
        "email": "li.na@acme.com",
        "role": "普通用户",
        "status": status_badge("正常"),
        "last": "11-15 08:47",
        "action": ButtonGroup(
            buttons=[
                Button(text="编辑", size="sm", color=Color.light, icon="pencil", toggle_modal="user-modal"),
                Button(text="更多", size="sm", color=Color.light, icon="three-dots"),
            ]
        ),
    },
    {
        "user": user_cell("王强", "王", "warning"),
        "email": "wang.qiang@acme.com",
        "role": "普通用户",
        "status": status_badge("待审核"),
        "last": "11-14 21:05",
        "action": ButtonGroup(
            buttons=[
                Button(text="编辑", size="sm", color=Color.light, icon="pencil", toggle_modal="user-modal"),
                Button(text="更多", size="sm", color=Color.light, icon="three-dots"),
            ]
        ),
    },
    {
        "user": user_cell("刘洋", "刘", "secondary"),
        "email": "liu.yang@acme.com",
        "role": "只读",
        "status": status_badge("已停用"),
        "last": "10-28 11:30",
        "action": ButtonGroup(
            buttons=[
                Button(text="编辑", size="sm", color=Color.light, icon="pencil", toggle_modal="user-modal"),
                Button(text="更多", size="sm", color=Color.light, icon="three-dots"),
            ]
        ),
    },
]

# ---------------------------------------------------------------- 页面结构

navbar = Navbar(
    brand="Acme 控制台",
    brand_icon="grid-1x2-fill",
    items=[
        NavItem(text="概览", href="#", icon="speedometer2", active=True),
        NavItem(text="订单", href="#", icon="bag"),
        NavItem(text="客户", href="#", icon="people"),
        NavItem(text="报表", href="#", icon="bar-chart"),
    ],
    actions=[
        Dropdown(
            text="惜月",
            as_button=True,
            color=Color.light,
            as_nav_item=False,
            items=[
                DropdownItem(text="个人资料", icon="person"),
                DropdownItem(text="偏好设置", icon="gear"),
                DropdownItem(divider=True),
                DropdownItem(text="退出登录", icon="box-arrow-right"),
            ],
        )
    ],
    expand="lg",
)

toolbar = Row(
    justify="between",
    align="center",
    children=[
        Col(
            width="auto",
            body=[
                Heading(text="数据概览", level=1, size="3", class_name="mb-0"),
                Span(text="2025 年 11 月 15 日 · 星期六", color="body-secondary"),
            ],
        ),
        Col(
            width="auto",
            body=[
                Box(
                    class_name="d-flex gap-2",
                    children=[
                        ButtonGroup(
                            buttons=[
                                Button(text="导出", color=Color.light, icon="download"),
                                Button(text="刷新", color=Color.light, icon="arrow-clockwise"),
                            ]
                        ),
                        Button(text="新增用户", icon="plus-lg", toggle_modal="user-modal"),
                        Button(text="筛选", color=Color.light, icon="funnel", toggle_offcanvas="filter-panel"),
                    ],
                )
            ],
        ),
    ],
)

stats = Row(
    gutter=3,
    children=[
        stat_card("今日订单", "1,284", "bag-check", "primary", "+12.5%", percent=72),
        stat_card("销售额", "¥ 86,420", "currency-yen", "success", "+8.2%", percent=58),
        stat_card("新增客户", "96", "person-plus", "info", "-3.1%", up=False, percent=41),
        stat_card("待处理工单", "17", "exclamation-circle", "warning", "+2", percent=24),
    ],
)

overview_tabs = Card(
    body=[
        Tabs(
            items=[
                TabItem(label="近期订单", body=[Table(columns=ORDER_COLUMNS, rows=ORDERS, striped=True, small=False)]),
                TabItem(label="热销商品", body=[Table(columns=PRODUCT_COLUMNS, rows=PRODUCTS)]),
                TabItem(label="地区分布", body=[Table(columns=REGION_COLUMNS, rows=REGIONS)]),
            ]
        )
    ]
)

side_panel = Card(
    title="待办事项",
    subtitle="本周 · 共 6 项",
    actions=[Tooltip(text="", content="标记为全部完成", icon="check2-circle")],
    body=[
        ListGroup(
            flush=True,
            items=[
                ListItem(text="审核新注册用户", icon="person-check", badge="3"),
                ListItem(text="确认采购合同", icon="file-earmark-text", badge="1"),
                ListItem(text="回复客户工单", icon="chat-dots", badge="2"),
            ],
        ),
        Hr(class_name="my-3"),
        Box(
            class_name="d-flex justify-content-between small mb-1",
            children=[Span(text="本周目标"), Span(text="68%", weight="semibold")],
        ),
        Progress(value=68, height="6px", show_value=False, class_name="mb-3"),
        Accordion(
            flush=True,
            items=[
                AccordionItem(
                    title="如何导出报表？",
                    body=["在工具栏点击「导出」，可选择 CSV 或 Excel 格式。"],
                ),
                AccordionItem(
                    title="如何调整权限？",
                    body=["进入「客户」页面，在操作列点击「编辑」即可修改角色。"],
                ),
            ],
        ),
    ],
)

user_toolbar = Row(
    gutter=2,
    align="center",
    class_name="mb-3",
    children=[
        Col(md=4, body=[InputGroup(control=Input(name="q", placeholder="搜索姓名或邮箱"), prepend="@")]),
        Col(
            md=3,
            body=[
                Select(
                    name="status_filter",
                    options=[("全部状态", ""), ("正常", "active"), ("待审核", "pending"), ("已停用", "disabled")],
                )
            ],
        ),
        Col(
            width="auto",
            body=[
                Button(text="查询", color=Color.primary, icon="search"),
                Button(text="重置", color=Color.light, icon="arrow-counterclockwise", class_name="ms-2"),
            ],
        ),
    ],
)

user_table = Table(columns=USER_COLUMNS, rows=USERS, striped=True)

user_card = Card(
    title="用户列表",
    subtitle="共 128 位用户，当前显示第 1 - 4 条",
    actions=[
        Button(text="导入", color=Color.light, size="sm", icon="upload"),
        Button(text="新建", size="sm", icon="plus-lg", toggle_modal="user-modal"),
    ],
    body=[
        user_toolbar,
        user_table,
        Box(
            class_name="d-flex flex-wrap justify-content-between align-items-center gap-2 mt-3",
            children=[
                Small(text="第 1 - 4 条 / 共 128 条"),
                Pagination(current=1, total=32, href="?page={page}", size="sm", show_edges=False),
            ],
        ),
    ],
)

notification = Alert(
    color=Color.warning,
    title="系统维护通知：",
    icon="exclamation-triangle",
    body=["今晚 23:00 - 24:00 将进行数据库升级，期间可能出现短暂不可用。"],
)

modal = Modal(
    id="user-modal",
    title="新增用户",
    size="lg",
    body=[
        Form(
            id="user-form",
            action="/api/users",
            submit_label=None,
            body=[
                Row(
                    gutter=3,
                    children=[
                        Col(
                            md=6,
                            body=[
                                FormGroup(
                                    label="姓名",
                                    required=True,
                                    control=Input(name="name", placeholder="请输入姓名", required=True),
                                )
                            ],
                        ),
                        Col(
                            md=6,
                            body=[
                                FormGroup(
                                    label="邮箱",
                                    required=True,
                                    control=Input(name="email", type="email", placeholder="name@acme.com", required=True),
                                )
                            ],
                        ),
                        Col(
                            md=6,
                            body=[
                                FormGroup(
                                    label="角色",
                                    control=Select(
                                        name="role",
                                        placeholder="请选择角色",
                                        options=[("管理员", "admin"), ("普通用户", "user"), ("只读", "viewer")],
                                    ),
                                )
                            ],
                        ),
                        Col(
                            md=6,
                            body=[
                                FormGroup(
                                    label="状态",
                                    control=Select(
                                        name="status",
                                        options=[("正常", "active"), ("待审核", "pending"), ("已停用", "disabled")],
                                    ),
                                )
                            ],
                        ),
                        Col(
                            width=12,
                            body=[
                                FormGroup(
                                    label="备注",
                                    control=Textarea(name="remark", rows=3, placeholder="可选，最多 200 字"),
                                    help="备注仅内部可见。",
                                )
                            ],
                        ),
                        Col(
                            width=12,
                            body=[
                                Checkbox(name="notify", label="创建后发送邮件通知", checked=True, switch=True)
                            ],
                        ),
                    ],
                )
            ],
        )
    ],
    footer=[
        Button(text="取消", color=Color.secondary, outline=True, attrs={"data-bs-dismiss": "modal"}),
        Button(text="保存", icon="check2", type="submit", attrs={"form": "user-form"}),
    ],
)

offcanvas = Offcanvas(
    id="filter-panel",
    title="筛选条件",
    placement="end",
    body=[
        Form(
            action="#",
            submit_label="应用筛选",
            reset_label="重置",
            body=[
                FormGroup(
                    label="状态",
                    control=Select(name="f_status", options=[("全部", ""), ("正常", "active"), ("待审核", "pending")]),
                ),
                FormGroup(
                    label="角色",
                    control=RadioGroup(
                        name="f_role",
                        value="user",
                        inline=False,
                        options=[("管理员", "admin"), ("普通用户", "user"), ("只读", "viewer")],
                    ),
                ),
                FormGroup(label="注册日期起", control=Input(name="f_from", type="date")),
                FormGroup(label="注册日期止", control=Input(name="f_to", type="date")),
                Checkbox(name="f_only_online", label="只看在线用户", switch=True),
            ],
        )
    ],
)

toasts = ToastContainer(
    children=[
        Toast(
            color=Color.success,
            title="保存成功",
            icon="check-circle",
            body=["用户「张伟」已创建。"],
        )
    ]
)

page = Page(
    title="Acme 控制台 · 数据概览",
    lang="zh-CN",
    navbar=navbar,
    toolbar=toolbar,
    body=[
        Breadcrumb(items=[BreadcrumbItem(text="首页", href="#"), BreadcrumbItem(text="数据概览")]),
        notification,
        stats,
        Row(
            gutter=4,
            align="start",
            class_name="mt-1",
            children=[
                Col(xl=8, body=[overview_tabs]),
                Col(xl=4, body=[side_panel]),
            ],
        ),
        user_card,
        modal,
        offcanvas,
        toasts,
    ],
    footer=Box(
        class_name="border-top py-3 mt-4",
        children=[
            Box(
                class_name="container d-flex flex-wrap justify-content-between small text-body-secondary",
                children=[
                    Span(text="© 2025 Acme Inc."),
                    Span(text="由 bootstrap-python 渲染 · Bootstrap 5.3"),
                ],
            )
        ],
    ),
    custom_css="""
    .card { border-color: var(--bs-border-color-translucent); }
    .breadcrumb { --bs-breadcrumb-divider: '›'; }
    """,
    custom_js="""
  // 演示：点击「查询」时给个轻提示
  document.querySelectorAll('button').forEach(function (btn) {
    if (btn.textContent.trim() === '查询') {
      btn.addEventListener('click', function () {
        var el = document.querySelector('.toast');
        if (el) { bootstrap.Toast.getOrCreateInstance(el).show(); }
      });
    }
  });
""",
)


if __name__ == "__main__":
    target = Path(__file__).with_name("dashboard.html")
    target.write_text(page.render(), encoding="utf-8")
    print(f"已生成 {target}（{target.stat().st_size} 字节）")
