# import json
#
# from django import template
# from django.template.context import Context
#
# from django.contrib.admin.templatetags import admin_modify
#
# from django.contrib.admin.templatetags.base import InclusionAdminNode
#
# register = template.Library()
#
# def submit_row(context):
#     ctx = admin_modify.submit_row(context)
#
#
# @register.tag(name='submit_row')
# def submit_row_tag(parser, token):
#     return InclusionAdminNode(parser, token, func=submit_row, template_name='submit_line.html')