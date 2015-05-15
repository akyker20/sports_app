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
from operator import itemgetter
import random

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
		template = 'athletes/profile/user_profile.html'
		suggestions = get_watch_suggestions(athlete)
	else:
		athlete = AthleteProfile.objects.get(pk=athlete_id)
		template = 'athletes/profile/other_profile.html'
		suggestions = None
	watch_count = athlete.watched_by.count()
	athlete_clips = athlete.clip_set
	total_clip_views = athlete_clips.aggregate(views=Sum('view_count'))['views']
	game_stats = athlete.gamestat_set.all()
	watching_player = athlete in current_athlete.watching.all()
	context = { 'athlete': athlete, 'clips': athlete_clips.all(), 'gamestats': game_stats,
				'watch_count': watch_count, "total_clip_views": total_clip_views,
				'suggestions':suggestions }
	return render(request, template, context)

@group_required('athletes')
def search(request):
	if request.is_ajax() and request.method == 'GET':
		searched_name = request.GET['search']
		athlete_results = AthleteProfile.objects.filter(athlete__first_name__istartswith=searched_name)
		context = { 'athlete_results': athlete_results }
		return render(request, 'athletes/profile/search_results.html', context)

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
		return render(request, 'athletes/cc/comment.html', { 'comment': comment })
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
	top10_clips = cache.get(cache_key)
	if not top10_clips:
		weekly_clips = Clip.objects.filter(created_at__gte=datetime.datetime.now() - datetime.timedelta(weeks=1))
		weekly_clips_tuples = map(compute_popularity, weekly_clips)
		weekly_clips_tuples.sort(key=itemgetter(0), reverse=True)
		top10_clips = [Clip.objects.get(id=tup[1]) for tup in weekly_clips_tuples[0:10]]
		cache.set(cache_key, top10_clips, cache_time)
	return render(request, 'athletes/top10.html', {"clips":top10_clips, "athlete": request.user.athleteprofile })


def compute_popularity(clip):
	return (5*clip.stars.count() + clip.view_count, clip.id)


def get_gamestat(request):
	if request.is_ajax() and request.method == 'GET':
		gamestat = GameStat.objects.get(pk=int(request.GET['stat_id']))
		json = {}
		clip = None
		if gamestat.clips.exists():
			clip = gamestat.clips.first()

		json['html'] = render_to_string('athletes/gamestat/gamestat_modal.html', 
										RequestContext(request, { "stat":gamestat, "clip":clip }))
		if clip:
			json['dash_info'] = { "mpd_url":clip.get_gamefilm().mpd_url, 
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
			json['dash_info'] = { "mpd_url":clip.game.gamefilm.mpd_url, 
								  "start_time":clip.gamefilm_start_time, 
								  "end_time":clip.gamefilm_end_time}
	
		return JsonResponse(json)
	return HttpResponseForbidden()


@group_required('athletes')
def play_gamefilm(request):
	if request.is_ajax() and request.method == "GET":
		athlete = request.user.athleteprofile
		film_id = request.GET["gamefilm-id"]
		gamefilm = GameFilm.objects.get(pk=int(film_id))
		gamefilm_clips = athlete.gamestat_set.get(game=gamefilm.game).clips.all()
		return render(request, 'athletes/gamefilm/gamefilm_display_modal.html', 
							   {"gamefilm_clips":gamefilm_clips, "gamefilm": gamefilm })

@group_required('athletes')
def watching(request):
	athlete = request.user.athleteprofile
	players_watching = athlete.watching.order_by("athlete__first_name")
	return render(request, 'athletes/watching_page.html', { "players_watching": players_watching })


@csrf_exempt
@group_required('athletes')
def create_gamefilmclip(request):
	if request.is_ajax() and request.method == 'POST':
		athlete = request.user.athleteprofile
		gamefilm = GameFilm.objects.get(pk=int(request.POST['gamefilm_id']))
		start_time = Decimal(request.POST['start_time'])
		end_time = Decimal(request.POST['end_time'])

		import pdb; pdb.set_trace();
		if not athlete.gamestat_set.filter(game=gamefilm.game).exists():
			gamestat = athlete.gamestat_set.create(game=gamefilm.game)
		else:
			gamestat = athlete.gamestat_set.first()

		GameFilmClip.objects.create(athlete=athlete, 
									gamefilm_start_time=start_time,
									gamefilm_end_time=end_time, 
									game=gamefilm.game, 
									gamestat=gamestat)

		return render(request, 'athletes/gamefilm/gamefilm_clipbars.html', 
							   { "gamefilm_clips":gamestat.clips.all() })

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
		return render(request, 'athletes/gamefilm/gamefilm_clipbars.html', 
							   { "gamefilm_clips":game_clip.gamefilm.clips })
	return HttpResponseForbidden()

@csrf_exempt
@group_required('athletes')
def delete_gamefilm_clip(request):
	if request.is_ajax() and request.method == 'POST':
		gamefilm_clip = get_object_or_404(GameFilmClip, pk=request.POST['clip_id'])
		gamefilm_clip.delete()
		return HttpResponse('Success')
	return HttpResponseForbidden()


@group_required('athletes')
def show_game(request):
	game = Game.objects.get(pk=int(request.GET['game_id']))
	json = {}
	json['dash_info'] = fetch_dash_game_highlights(game)
	json['html'] = render_to_string('athletes/game/game_display_modal.html', 
									RequestContext(request, { "game": game }))
	return JsonResponse(json)

def fetch_dash_game_highlights(game):
	""" Method to return all dash information needed to play game highlight mix - the most popular clips from
		the game in sequential order """
	gamefilm = game.gamefilm
	json = {}
	json['mpd_url'] = gamefilm.mpd_url
	time_ranges = []
	clips_ordered_by_view_count = game.clips.order_by('-view_count')[0:10]
	min_view_count = clips_ordered_by_view_count[len(clips_ordered_by_view_count)-1].view_count
	most_popular_clips = game.clips.filter(view_count__gte=min_view_count)
	for clip in most_popular_clips.order_by('gamefilm_start_time')[0:10]:
		time_ranges.append({"start_time": clip.gamefilm_start_time, "end_time": clip.gamefilm_end_time })
	json['highlights_time_ranges'] = time_ranges
	return json

