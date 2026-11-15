# Changelog

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-11-15

首个版本，已发布到 [PyPI](https://pypi.org/project/bootstrap-python/0.1.0/)。

### 新增

- `Node` 渲染内核：`css_classes()` / `html_attrs()` / `render_content()` 三层扩展点，
  默认转义、`RawHtml` 显式放行、`to_dict()` / `to_json()` / `render()` 三种输出。
- 页面与布局：`Page`（jinja2 模板、CDN、暗色主题、自定义 CSS/JS）、`Container`、`Row`、`Col`、
  `Stack`、`Box`、`Fragment`、`Hr`。
- 内容组件：`Heading`、`Paragraph`、`Span`、`Strong`、`Small`、`Link`、`Image`、`Icon`、
  `Badge`、`Alert`、`Card`、`ListGroup`、`Button`、`ButtonGroup`、`CloseButton`。
- 导航：`Navbar`、`Nav`、`NavItem`、`Dropdown`、`Breadcrumb`、`Pagination`。
- 数据展示：`Table`、`TableColumn`、`Progress`、`Spinner`、`Tabs`、`Accordion`、`Carousel`。
- 浮层：`Modal`、`Offcanvas`、`Toast`、`ToastContainer`、`Tooltip`。
- 表单：`Form`、`FormGroup`、`field()`、`Label`、`Input`、`Textarea`、`Select`、`Checkbox`
  （含 switch 形态）、`RadioGroup`、`InputGroup`、`Fieldset`、`Hidden`。
- 常量：`Color`、`Size`、`Alignment`、`Justify`、`Placement`、`Breakpoint`。
- 示例：`examples/dashboard.py` 生成后台概览页 `examples/dashboard.html`。
- 测试：24 项单元测试，含 HTML 标签闭合检查。

[0.1.0]: https://pypi.org/project/bootstrap-python/0.1.0/
