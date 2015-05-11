from models import Game, GameComment, Clip, ClipComment

def build_comment(comment_info):
	"""
	builds a comment of the correct type (gamestat or clip) given
	the type of model commented on, the id of that model instance,
	the athlete that commented, and the content.
	"""
	if comment_info['type'] == 'clip':
		clip = Clip.objects.get(id=comment_info['type_id'])
		comment = ClipComment(content=comment_info['content'], 
							  author=comment_info['athlete'], 
							  clip=clip)
	else:
		game = Game.objects.get(id=comment_info['type_id'])
		comment = GameComment(content=comment_info['content'],
							 author=comment_info['athlete'],
							 game=game)
	comment.save()
	return comment