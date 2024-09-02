import functools
from importlib import import_module
from typing import Callable, Dict

from django import forms
from django.contrib.admin import helpers
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpRequest

from admin_action_tools.admin.base import BaseMixin
from admin_action_tools.constants import CONFIRM_FORM, ToolAction
from admin_action_tools.toolchain import ToolChain, add_finishing_step
from admin_action_tools.utils import snake_to_title_case


class ActionFormMixin(BaseMixin):

    # Custom templates (designed to be over-ridden in subclasses)
    action_form_template: str = None

    def build_context(
        self,
        request: HttpRequest,
        func: Callable,
        queryset: QuerySet,
        form_instance: Form,
        tool_name: str,
        display_queryset: bool,
    ):
        action_display_name = snake_to_title_case(func.__name__)
        title = f"Configure Action: {action_display_name}"
        opts = self.model._meta  # pylint: disable=W0212

        return {
            **self.admin_site.each_context(request),
            "title": title,
            "action": func.__name__,
            "action_display_name": action_display_name,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "submit_name": "confirm_action",
            "queryset": queryset if display_queryset else [],
            "media": self.media + form_instance.media,
            "opts": opts,
            "form": form_instance,
            "submit_action": tool_name,
            "submit_text": "Continue",
            "back_text": "Back",
        }

    def render_action_form(self, request: HttpRequest, context: Dict):
        return super().render_template(
            request, context, "form_tool/action_form.html", custom_template=self.action_form_template
        )

    @staticmethod
    def __get_metadata(form):
        return {
            "type": "form",
            "module": form.__module__,
            "name": form.__name__,
        }

    @staticmethod
    def load_form(data, metadata):
        # import_module use sys.module as a caching mechanism
        module = import_module(metadata["module"])
        form = getattr(module, metadata["name"])
        form_instance: Form = form(data)
        form_instance.is_valid()
        return form_instance

    def run_form_tool(
        self, func: Callable, request: HttpRequest, queryset_or_object, form: forms, display_queryset: bool
    ):
        tool_chain: ToolChain = ToolChain(request)
        tool_name = f"{CONFIRM_FORM}_{form.__name__}"
        step = tool_chain.get_next_step(tool_name)

        if step == ToolAction.BACK:
            # cancel ask, revert to previous form
            data = tool_chain.rollback()
            form_instance = self.__get_instance(form, data=data, instance=queryset_or_object)
        # First called by `Go` which would not have tool_name in params
        elif step == ToolAction.CONFIRMED:
            # form is filled
            form_instance = self.__get_instance(form, data=request.POST, instance=queryset_or_object)
            if form_instance.is_valid():
                metadata = self.__get_metadata(form)
                tool_chain.set_tool(tool_name, form_instance.data, metadata=metadata)
                return func(self, request, queryset_or_object)
        elif step in {ToolAction.FORWARD, ToolAction.CANCEL}:
            # forward to next
            return func(self, request, queryset_or_object)
        else:
            form_instance = self.__get_instance(form, instance=queryset_or_object)

        queryset: QuerySet = self.to_queryset(request, queryset_or_object)
        context = self.build_context(request, func, queryset, form_instance, tool_name, display_queryset)

        # Display form
        return self.render_action_form(request, context)

    @staticmethod
    def __get_instance(
        form: type[forms.BaseForm], data: dict | None = None, instance: forms.BaseForm | None = None
    ) -> forms.BaseForm:
        if issubclass(form, forms.ModelForm):
            return form(data, instance=instance)
        return form(data)


def add_form_to_action(form: Form, display_queryset=True):
    """
    @add_form_to_action function wrapper for Django ModelAdmin actions
    Will redirect to a form page to ask for more information

    Next, it would call the action with the form data.
    """

    def add_form_to_action_decorator(func):

        # make sure tools chain is setup
        func = add_finishing_step(func)

        @functools.wraps(func)
        def func_wrapper(modeladmin: ActionFormMixin, request, queryset_or_object):
            return modeladmin.run_form_tool(func, request, queryset_or_object, form, display_queryset)

        return func_wrapper

    return add_form_to_action_decorator
