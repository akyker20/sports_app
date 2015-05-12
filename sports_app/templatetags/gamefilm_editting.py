from django import template
from django.template.loader import get_template
from decimal import Decimal

register = template.Library()


# Important: the constants used should correspond to the constants in clip_creation.js
@register.inclusion_tag('athletes/gamefilm_clipbar.html')
def generate_clipbar(gamefilm_clip):
	gamefilm = gamefilm_clip.game.gamefilm
	BUFFERED_CONTROL_WIDTH = 518
	BUFFERED_CONTROL_RIGHT_OFFSET = 68
	pixels_left = (gamefilm_clip.gamefilm_start_time/Decimal(gamefilm.duration))*BUFFERED_CONTROL_WIDTH + BUFFERED_CONTROL_RIGHT_OFFSET
	pixels_width = ((gamefilm_clip.gamefilm_end_time - gamefilm_clip.gamefilm_start_time)/Decimal(gamefilm.duration))*BUFFERED_CONTROL_WIDTH
	return {"clip":gamefilm_clip, "pixels_left": pixels_left, "pixels_width": pixels_width}