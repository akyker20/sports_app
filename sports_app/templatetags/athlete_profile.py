from django import template
from django.db.models import get_model

register = template.Library()

@register.filter
def format_view_count(total_views):
	return total_views if total_views < 1000 else "{}k".format(total_views/1000)

@register.filter
def height(total_inches):
	ft = total_inches / 12
	inches = total_inches % 12
	return "{}'{}".format(ft, inches)

@register.filter
def calc_bar_height_width(inches):
	return calc_bar_width(60, 90, inches)

@register.filter
def calc_bar_weight_width(pounds):
	return calc_bar_width(100, 250, pounds)

@register.filter
def calc_bar_vertical_width(vert):
	return calc_bar_width(20, 45, vert)

def calc_bar_width(min_val, max_val, val):
	if val < min_val + (max_val-min_val)*0.25:
		return 25
	elif val >= max_val:
		return 100
	else:
		return (val - min_val)/float(max_val - min_val) * 100