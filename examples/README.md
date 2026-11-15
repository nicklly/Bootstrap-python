# 示例

## dashboard.py

用组件搭一个 Bootstrap 5 后台概览页，覆盖最常见的组合方式。

```bash
# 在仓库根目录执行
pip install -e .
python examples/dashboard.py     # 生成 examples/dashboard.html
```

生成结果 `dashboard.html` 可以直接用浏览器打开；Bootstrap 与图标资源从 jsdelivr CDN 加载，
所以需要联网。

页面包含：

- 导航栏（品牌 + 菜单 + 用户下拉菜单）
- 面包屑、可关闭的告警条
- 4 张统计卡（图标、环比、进度条）
- 标签页表格（订单 / 商品 / 地区，单元格内嵌 `Badge`、`Progress`）
- 待办列表组 + 折叠面板
- 带搜索工具条的用户表格、分页
- 新增用户弹窗、筛选抽屉、Toast

渲染效果见仓库根目录的 `docs/images/`。
