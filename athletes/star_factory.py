from models import GameStat, GameStatStar, Clip, ClipStar

def build_star(star_info):
	"""
	builds a comment of the correct type (gamestat or clip) given
	the type of model commented on, the id of that model instance,
	the athlete that commented, and the content.
	"""
	if star_info['type'] == 'clip':
		clip = Clip.objects.get(id=star_info['type_id'])
		star = ClipStar(author=star_info['athlete'], 
							  clip=clip)
	else:
		gamestat = GameStat.objects.get(id=star_info['type_id'])
		star = GameStatStar(author=star_info['athlete'],
							   gamestat=gamestat)
	star.save()
	return star