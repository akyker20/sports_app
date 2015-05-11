from django.shortcuts import render
from sports_app.forms import AuthenticateForm, AthleteCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from datetime import date
from sports_app.decorators import group_required
from django.views.decorators.csrf import csrf_exempt
from models import *
import json, datetime
from comment_factory import build_comment
from star_factory import build_star
from django.db.models import Count, Sum
from django.core.cache import cache
from decimal import Decimal

def register(request):
	form = AthleteCreationForm()
	if request.method == 'POST':
		form = AthleteCreationForm(request.POST)
		if form.is_valid():
			athletes_dob = date(request.POST['dob_year'], 
				                request.POST['dob_month'], 
				                request.POST['dob_day'])
			new_user = form.save()
			AthleteProfile.create(user=new_user, date_of_birth=athletes_dob)
			return redirect('athlete_profile')
	return render(request, "athletes/form_display.html", {'form': form})

@login_required
def feed(request):
	athlete = request.user.athleteprofile
	gamestats = GameStat.objects.filter(athlete__in=athlete.watching.all())[:5]
	clips = Clip.objects.filter(athlete__in=athlete.watching.all())[:5]
	feed_objects = []
	while gamestats or clips:
		if not gamestats:
			feed_objects += clips
			break
		if not clips:
			feed_objects += gamestats
			break
		if gamestats[0].created_at > clips[0].created_at:
			feed_objects.append(gamestats[0])
			gamestats = gamestats[1:]
		else:
			feed_objects.append(clips[0])
			clips = clips[1:]
	return render(request, 'athletes/feed.html', {"feed_objects": feed_objects, "athlete": athlete })



@csrf_exempt
@login_required
def watch_player(request, athlete_id=None):
	if request.is_ajax() and request.method =='POST':
		athlete = request.user.athleteprofile
		if athlete_id is not None and athlete_id != athlete.id:
			athlete_to_watch = AthleteProfile.objects.get(id=athlete_id)
			if not athlete_to_watch in athlete.watching.all():
				athlete.watching.add(athlete_to_watch)
			return render(request, 'athletes/watching.html', { 'watching_player': True, 'athlete_id': athlete_id })
	return HttpResponseForbidden()

@csrf_exempt
@login_required
def unwatch_player(request, athlete_id=None):
	if request.is_ajax() and request.method =='POST':
		athlete = request.user.athleteprofile
		if athlete_id is not None and athlete_id != athlete.id:
			athete_watching = AthleteProfile.objects.get(id=athlete_id)
			if athete_watching in athlete.watching.all():
				athlete.watching.remove(athete_watching)
			return render(request, 'athletes/watching.html', { 'watching_player': False, 'athlete_id': athlete_id })
	return HttpResponseForbidden()

@group_required('athletes')
def profile(request, athlete_id=None):
	current_athlete = request.user.athleteprofile
	if athlete_id is None or int(athlete_id) == current_athlete.id:
		athlete = current_athlete
		template = 'athletes/user_profile.html'
	else:
		athlete = AthleteProfile.objects.get(pk=athlete_id)
		template = 'athletes/other_profile.html'
	watch_count = athlete.watched_by.count()
	athlete_clips = athlete.clip_set
	total_clip_views = athlete_clips.aggregate(views=Sum('view_count'))['views']
	game_stats = athlete.gamestat_set.all()
	watching_player = athlete in current_athlete.watching.all()
	context = { 'athlete': athlete, 'clips': athlete_clips.all(), 'gamestats': game_stats,
				'watch_count': watch_count, "total_clip_views": total_clip_views }
	return render(request, template, context)

@group_required('athletes')
def search(request):
	if request.is_ajax() and request.method == 'GET':
		searched_name = request.GET['search']
		athlete_results = AthleteProfile.objects.filter(athlete__first_name__istartswith=searched_name)
		context = { 'athlete_results': athlete_results }
		return render(request, 'athletes/search_results.html', context)

def get_type_and_id(request):
	athlete = request.user.athleteprofile
	model_type = request.POST['type']
	type_id = request.POST['id']
	return {"athlete":athlete, "type":model_type, "type_id": type_id}

@group_required('athletes')
@csrf_exempt
def comment(request):
	# import pdb; pdb.set_trace();
	if request.is_ajax() and request.method == 'POST':
		comment_info = get_type_and_id(request)
		comment_info['content'] = request.POST['content']
		comment = build_comment(comment_info)
		return render(request, 'athletes/comment.html', { 'comment': comment })
	return HttpResponseForbidden()

@group_required('athletes')
@csrf_exempt
def star(request):
	if request.is_ajax() and request.method == 'POST':
		star = build_star(get_type_and_id(request))
		return render(request, 'athletes/star_btns.html', {'has_starred': True})
	return HttpResponseForbidden()


@group_required('athletes')
def top10(request):
	cache_key = 'top10_clips'
	cache_time = 300
	clips = cache.get(cache_key)
	if not clips:
		clips = Clip.objects.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(weeks=1)).annotate(star_count=Count('stars')).order_by('-star_count')[:10]
		cache.set(cache_key, clips, cache_time)
	return render(request, 'athletes/top10.html', {"clips":clips})


def get_gamestat(request):
	if request.is_ajax() and request.method == 'GET':
		gamestat = GameStat.objects.get(pk=int(request.GET['stat_id']))
		json = {}
		clip = None
		if gamestat.game.gamefilm.clips.exists():
			clip = gamestat.game.gamefilm.clips.first()

		json['html'] = render_to_string('athletes/gamestat_modal.html', 
										RequestContext(request, { "stat":gamestat, "clip":clip }))
		if clip:
			json['dash_info'] = { "mpd_url":clip.gamefilm.mpd_url, 
								  "start_time":clip.gamefilm_start_time, 
								  "end_time":clip.gamefilm_end_time}

		return JsonResponse(json)

	return HttpResponseForbidden()



# TODO: store id, not encoded_id (Use primary key!!!)
@group_required('athletes')
def play_clip(request):
	if request.is_ajax() and request.method == "GET":
		clip = Clip.objects.get(pk=request.GET['clip_id'])
		clip.view_count += 1
		clip.save()
		json = {}
		json['html'] = render_to_string('athletes/video_display_modal.html', 
			RequestContext(request, { "clip":clip }))
		
		if(clip.__class__.__name__ == "GameFilmClip"):
			json['dash_info'] = { "mpd_url":clip.gamefilm.mpd_url, 
								  "start_time":clip.gamefilm_start_time, 
								  "end_time":clip.gamefilm_end_time}
	
		return JsonResponse(json)
	return HttpResponseForbidden()


@group_required('athletes')
def play_gamefilm(request):
	if request.is_ajax() and request.method == "GET":
		film_id = request.GET["gamefilm-id"]
		gamefilm = GameFilm.objects.get(pk=int(film_id))
		return render(request, 'athletes/gamefilm_display_modal.html', {"gamefilm":gamefilm})


@csrf_exempt
@group_required('athletes')
def create_gamefilmclip(request):
	if request.is_ajax() and request.method == 'POST':
		athlete = request.user.athleteprofile
		gamefilm = GameFilm.objects.get(pk=int(request.POST['gamefilm_id']))
		start_time = Decimal(request.POST['start_time'])
		end_time = Decimal(request.POST['end_time'])
		GameFilmClip.objects.create(athlete=athlete, gamefilm_start_time=start_time,
									gamefilm_end_time=end_time, gamefilm=gamefilm)
		return render(request, 'athletes/gamefilm_clipbars.html', { "gamefilm_clips":gamefilm.clips })

@csrf_exempt
@group_required('athletes')
def update_gamefilm_clip(request):
	if request.is_ajax() and request.method == 'POST':
		game_clip = GameFilmClip.objects.get(pk=int(request.POST['clip_id']))
		start_time = Decimal(request.POST['start_time'])
		end_time = Decimal(request.POST['end_time'])
		game_clip.gamefilm_start_time = start_time
		game_clip.gamefilm_end_time = end_time
		game_clip.save()
		return render(request, 'athletes/gamefilm_clipbars.html', { "gamefilm_clips":game_clip.gamefilm.clips })
	return HttpResponseForbidden()

@csrf_exempt
@group_required('athletes')
def delete_gamefilm_clip(request):
	if request.is_ajax() and request.method == 'POST':
		gamefilm_clip = get_object_or_404(GameFilmClip, pk=request.POST['clip_id'])
		gamefilm_clip.delete()
		return HttpResponse('Success')
	return HttpResponseForbidden()


# @group_required('athletes')
# def get_dash_info(request):
# 	if request.method == 'GET':
# 		clip = get_object_or_404(GameFilmClip, pk=request.GET['clip_id'])
# 		json = {}
# 		json['dash_info'] = { "mpd_url":clip.gamefilm.mpd_url, "start_time":clip.gamefilm_start_time, "end_time":clip.gamefilm_end_time }
# 		return JsonResponse(json)
# 	return HttpResponseForbidden()

@group_required('athletes')
def show_game(request):
	# import pdb; pdb.set_trace();
	game = Game.objects.get(pk=int(request.GET['game_id']))
	json = {}
	json['dash_info'] = fetch_dash_game_highlights(game)
	json['html'] = render_to_string('athletes/game_display_modal.html', RequestContext(request, { "game": game }))
	return JsonResponse(json)

def fetch_dash_game_highlights(game):
	""" Method to return all dash information needed to play game highlight mix - the most popular clips from
		the game in sequential order """
	gamefilm = game.gamefilm
	json = {}
	json['mpd_url'] = gamefilm.mpd_url
	time_ranges = []
	clips_ordered_by_view_count = gamefilm.clips.order_by('-view_count')[0:10]
	min_view_count = clips_ordered_by_view_count[len(clips_ordered_by_view_count)-1].view_count
	most_popular_clips = gamefilm.clips.filter(view_count__gte=min_view_count)
	for clip in most_popular_clips.order_by('gamefilm_start_time')[0:10]:
		time_ranges.append({"start_time": clip.gamefilm_start_time, "end_time": clip.gamefilm_end_time })
	json['highlights_time_ranges'] = time_ranges
	return json

