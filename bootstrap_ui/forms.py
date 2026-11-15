"""表单组件：Form / FormGroup / Label / Input / Textarea / Select / Checkbox / RadioGroup /
InputGroup / Fieldset / Hidden。

用法上分成两层：控件只渲染自身（``<input>``、``<select>`` …），
由 :class:`FormGroup` 负责「标签 + 控件 + 帮助文本」的组合，
与 Bootstrap 文档的结构一一对应。
"""

from __future__ import annotations

import re
from typing import Any, ClassVar, Literal

from pydantic import Field

from .constants import Color, Size, value as enum_value
from .content import Button
from .types import Node, NodeLike, escape, render_attrs, render_children

__all__ = [
    "Form",
    "FormGroup",
    "Label",
    "Input",
    "Textarea",
    "Select",
    "Checkbox",
    "RadioGroup",
    "InputGroup",
    "Fieldset",
    "Hidden",
    "field",
    "field_id",
]


def field_id(name: str) -> str:
    """把字段名转成合法的 HTML id，例如 ``user[name]`` → ``field-user-name``。"""
    return "field-" + re.sub(r"[^\w-]+", "-", name).strip("-")


def _normalize_options(options: list[Any] | None):
    """把各种选项写法统一成 ``(label, value, disabled)``，支持 optgroup。

    - ``"男"``                     → label=value="男"
    - ``("男", 1)`` / ``["男", 1]`` → label="男", value=1
    - ``{"label": "男", "value": 1, "disabled": True}``
    - ``{"label": "分组", "options": [...]}`` → optgroup
    """
    for option in options or []:
        if isinstance(option, dict):
            if "options" in option:
                yield ("group", option.get("label", ""), list(option.get("options") or []))
                continue
            label = option.get("label", option.get("value"))
            value = option.get("value", label)
            yield (label, value, bool(option.get("disabled", False)))
        elif isinstance(option, (list, tuple)):
            values = list(option)
            label = values[0] if values else ""
            value = values[1] if len(values) > 1 else label
            yield (label, value, bool(values[2]) if len(values) > 2 else False)
        else:
            yield (option, option, False)


class Form(Node):
    """表单。"""

    TAG: ClassVar[str | None] = "form"

    action: str = ""
    method: Literal["get", "post"] = "post"
    enctype: str | None = None
    body: list[NodeLike] = Field(default_factory=list)
    inline: bool = False
    novalidate: bool = False
    submit_label: str | None = "提交"
    submit_color: Color = Color.primary
    reset_label: str | None = None

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["action"] = self.action
        attrs["method"] = self.method
        if self.enctype:
            attrs["enctype"] = self.enctype
        if self.novalidate:
            attrs["novalidate"] = True
        return attrs

    def css_classes(self) -> list[str]:
        return ["row", "row-cols-lg-auto", "g-3", "align-items-center"] if self.inline else []

    def render_content(self) -> str:
        parts = [render_children(self.body)]
        if self.submit_label or self.reset_label:
            buttons: list[str] = []
            if self.submit_label:
                buttons.append(
                    Button(text=self.submit_label, type="submit", color=self.submit_color).render()
                )
            if self.reset_label:
                buttons.append(
                    Button(text=self.reset_label, type="reset", color=Color.secondary, outline=True).render()
                )
            parts.append(f'<div class="d-flex gap-2 mt-4">{"".join(buttons)}</div>')
        return "".join(parts)


class Label(Node):
    """表单标签。"""

    TAG: ClassVar[str | None] = "label"

    text: str = ""
    for_: str | None = Field(default=None, alias="for")
    required: bool = False

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        if self.for_:
            attrs["for"] = self.for_
        return attrs

    def css_classes(self) -> list[str]:
        return ["form-label"]

    def render_content(self) -> str:
        star = '<span class="text-danger ms-1">*</span>' if self.required else ""
        return escape(self.text) + star


class _Control(Node):
    """表单控件的公共行为：id 推导、校验反馈。"""

    TAG: ClassVar[str | None] = None

    name: str = ""
    invalid: bool = False
    valid: bool = False
    invalid_feedback: str | None = None
    valid_feedback: str | None = None

    def control_id(self) -> str:
        return self.id or field_id(self.name)

    def validation_classes(self) -> list[str]:
        classes: list[str] = []
        if self.invalid:
            classes.append("is-invalid")
        elif self.valid:
            classes.append("is-valid")
        return classes

    def feedback(self) -> str:
        parts: list[str] = []
        if self.invalid_feedback:
            parts.append(f'<div class="invalid-feedback">{escape(self.invalid_feedback)}</div>')
        if self.valid_feedback:
            parts.append(f'<div class="valid-feedback">{escape(self.valid_feedback)}</div>')
        return "".join(parts)


class Input(_Control):
    """单行输入框。"""

    TAG: ClassVar[str | None] = "input"

    type: str = "text"
    value: Any = None
    placeholder: str | None = None
    size: Size | None = None
    required: bool = False
    disabled: bool = False
    readonly: bool = False
    autocomplete: str | None = None

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["type"] = self.type
        attrs["name"] = self.name
        attrs.setdefault("id", self.control_id())
        if self.value is not None:
            attrs["value"] = self.value
        if self.placeholder:
            attrs["placeholder"] = self.placeholder
        if self.required:
            attrs["required"] = True
        if self.disabled:
            attrs["disabled"] = True
        if self.readonly:
            attrs["readonly"] = True
        if self.autocomplete:
            attrs["autocomplete"] = self.autocomplete
        return attrs

    def css_classes(self) -> list[str]:
        classes = ["form-control"]
        if self.size:
            classes.append(f"form-control-{enum_value(self.size)}")
        classes.extend(self.validation_classes())
        return classes

    def render(self) -> str:
        return super().render() + self.feedback()


class Textarea(_Control):
    """多行文本输入框。"""

    TAG: ClassVar[str | None] = "textarea"

    value: str | None = None
    rows: int = 3
    placeholder: str | None = None
    required: bool = False
    disabled: bool = False
    readonly: bool = False

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["name"] = self.name
        attrs.setdefault("id", self.control_id())
        attrs["rows"] = self.rows
        if self.placeholder:
            attrs["placeholder"] = self.placeholder
        if self.required:
            attrs["required"] = True
        if self.disabled:
            attrs["disabled"] = True
        if self.readonly:
            attrs["readonly"] = True
        return attrs

    def css_classes(self) -> list[str]:
        return ["form-control", *self.validation_classes()]

    def render_content(self) -> str:
        return escape(self.value or "")

    def render(self) -> str:
        return super().render() + self.feedback()


class Select(_Control):
    """下拉选择框。"""

    TAG: ClassVar[str | None] = "select"

    options: list[Any] = Field(default_factory=list)
    value: Any = None
    multiple: bool = False
    size: Size | None = None
    placeholder: str | None = None
    required: bool = False
    disabled: bool = False

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["name"] = self.name
        attrs.setdefault("id", self.control_id())
        if self.multiple:
            attrs["multiple"] = True
        if self.required:
            attrs["required"] = True
        if self.disabled:
            attrs["disabled"] = True
        return attrs

    def css_classes(self) -> list[str]:
        classes = ["form-select"]
        if self.size:
            classes.append(f"form-select-{enum_value(self.size)}")
        classes.extend(self.validation_classes())
        return classes

    def _options_html(self) -> str:
        selected = self.value if isinstance(self.value, (list, tuple, set)) else [self.value]
        selected_values = {str(item) for item in selected if item is not None}
        parts: list[str] = []

        if self.placeholder and not self.multiple and not selected_values:
            parts.append(f'<option value="" disabled selected>{escape(self.placeholder)}</option>')

        for label, value, disabled in _normalize_options(self.options):
            if label == "group":
                group_options = "".join(
                    self._option_html(*item, selected_values) for item in _normalize_options(value)
                )
                parts.append(f'<optgroup label="{escape(value)}">{group_options}</optgroup>')
            else:
                parts.append(self._option_html(label, value, disabled, selected_values))
        return "".join(parts)

    @staticmethod
    def _option_html(label: Any, value: Any, disabled: bool, selected_values: set[str]) -> str:
        attrs: list[str] = [f'value="{escape(value)}"']
        if disabled:
            attrs.append("disabled")
        if str(value) in selected_values:
            attrs.append("selected")
        return f'<option {" ".join(attrs)}>{escape(label)}</option>'

    def render_content(self) -> str:
        return self._options_html()

    def render(self) -> str:
        return super().render() + self.feedback()


class Checkbox(Node):
    """复选框 / 开关。"""

    TAG: ClassVar[str | None] = None

    name: str = ""
    label: str | None = None
    value: str = "on"
    checked: bool = False
    switch: bool = False
    inline: bool = False
    disabled: bool = False
    required: bool = False

    def render(self) -> str:
        checkbox_id = self.id or field_id(self.name)
        input_classes = ["form-check-input"]
        wrapper_classes = ["form-check"]
        if self.switch:
            wrapper_classes.append("form-switch")
        if self.inline:
            wrapper_classes.append("form-check-inline")

        attrs: dict[str, Any] = {
            "class": " ".join(input_classes),
            "type": "checkbox",
            "id": checkbox_id,
            "name": self.name,
            "value": self.value,
        }
        if self.checked:
            attrs["checked"] = True
        if self.disabled:
            attrs["disabled"] = True
        if self.required:
            attrs["required"] = True

        label = (
            f'<label class="form-check-label" for="{checkbox_id}">{escape(self.label)}</label>'
            if self.label
            else ""
        )
        return f'<div class="{" ".join(wrapper_classes)}"><input{render_attrs(attrs)}>{label}</div>'


class RadioGroup(Node):
    """单选组。"""

    TAG: ClassVar[str | None] = None

    name: str = ""
    options: list[Any] = Field(default_factory=list)
    value: Any = None
    inline: bool = True
    disabled: bool = False
    required: bool = False

    def render(self) -> str:
        parts: list[str] = []
        for index, (label, value, disabled) in enumerate(_normalize_options(self.options)):
            radio_id = f"{field_id(self.name)}-{index}"
            attrs: dict[str, Any] = {
                "class": "form-check-input",
                "type": "radio",
                "id": radio_id,
                "name": self.name,
                "value": value,
            }
            if self.value is not None and str(value) == str(self.value):
                attrs["checked"] = True
            if disabled or self.disabled:
                attrs["disabled"] = True
            if self.required:
                attrs["required"] = True
            wrapper = "form-check form-check-inline" if self.inline else "form-check"
            parts.append(
                f'<div class="{wrapper}"><input{render_attrs(attrs)}>'
                f'<label class="form-check-label" for="{radio_id}">{escape(label)}</label></div>'
            )
        return "".join(parts)


class InputGroup(Node):
    """输入框组合（前置 / 后置附加内容）。"""

    control: NodeLike | None = None
    prepend: NodeLike | None = None
    append: NodeLike | None = None
    size: Size | None = None

    def css_classes(self) -> list[str]:
        classes = ["input-group"]
        if self.size:
            classes.append(f"input-group-{enum_value(self.size)}")
        return classes

    def render_content(self) -> str:
        parts: list[str] = []
        if self.prepend is not None:
            parts.append(f'<span class="input-group-text">{render_children(self.prepend)}</span>')
        parts.append(render_children(self.control))
        if self.append is not None:
            parts.append(f'<span class="input-group-text">{render_children(self.append)}</span>')
        return "".join(parts)


class Fieldset(Node):
    """字段分组。"""

    TAG: ClassVar[str | None] = "fieldset"

    legend: str | None = None
    body: list[NodeLike] = Field(default_factory=list)
    disabled: bool = False

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        if self.disabled:
            attrs["disabled"] = True
        return attrs

    def css_classes(self) -> list[str]:
        return ["mb-3"]

    def render_content(self) -> str:
        legend = f"<legend>{escape(self.legend)}</legend>" if self.legend else ""
        return legend + render_children(self.body)


class Hidden(Node):
    """隐藏字段。"""

    TAG: ClassVar[str | None] = "input"

    name: str = ""
    value: Any = None

    def html_attrs(self) -> dict[str, Any]:
        attrs = super().html_attrs()
        attrs["type"] = "hidden"
        attrs["name"] = self.name
        if self.value is not None:
            attrs["value"] = self.value
        return attrs


class FormGroup(Node):
    """「标签 + 控件 + 帮助文本」的组合。"""

    label: str | None = None
    control: NodeLike | None = None
    help: str | None = None
    required: bool = False

    def css_classes(self) -> list[str]:
        return ["mb-3"]

    def _label_for(self) -> str | None:
        control = self.control
        if isinstance(control, _Control):
            return control.control_id()
        if isinstance(control, Checkbox):
            return control.id or field_id(control.name)
        return None

    def render_content(self) -> str:
        parts: list[str] = []
        if self.label:
            parts.append(Label(text=self.label, for_=self._label_for(), required=self.required).render())
        parts.append(render_children(self.control))
        if self.help:
            parts.append(f'<div class="form-text">{escape(self.help)}</div>')
        return "".join(parts)


def field(label: str, control: Node | str, help: str | None = None, required: bool = False) -> FormGroup:
    """``FormGroup(label=..., control=...)`` 的简写。"""
    return FormGroup(label=label, control=control, help=help, required=required)
