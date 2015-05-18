from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from athletes.models import *
from random import randint
from datetime import date


class Command(BaseCommand):
	help = 'Generates test data'

	def handle(self, **options):
		team_names = ["Park Tudor Panthers", "Carmel Greyhounds", "North Central Panthers", "Zionsville Eagles", "Cardinal Ritter Raiders"]
		team_cities = ["Indianapolis", "Carmel", "Indianapolis", "Zionsville", "Indianapolis"]
		coaches = ["Kyle Cox", "Darnell Archey", "Steve Blake", "Peter Craft", "Sam Thompson"]

		with open('/home/amk66/.virtualenvs/env/sports_app/sports_app/management/commands/names.txt', 'r') as f:
			random_names = f.readlines()

		names_index = 0

		for index, name in enumerate(team_names):
			team = Team.objects.create(name=name, city=team_cities[index], state="Indiana")
			coach = CoachProfile.objects.create(coach=User.objects.create_user(username=coaches[index].replace(" ", ""), first_name=coaches[index], password="password"),
								 				date_of_birth=date(1974, 11, 7), 
								 				current_team=team)
			print "generated team {}...".format(team.name)

			for i in range(randint(10, 13)):
				random_name = random_names[names_index].replace("\n", "")

				name_w_o_space = random_name.replace(" ", "").strip()
				email = "{}@gmail.com".format(name_w_o_space)
				team.athletes.create(athlete=User.objects.create_user(username=name_w_o_space, first_name=random_name, email=email, password="password"),
									 date_of_birth=date(randint(1993, 1997), randint(1, 12), randint(1, 28)),
									 number=randint(0, 45), 
									 height=randint(63, 80), 
									 weight=randint(160, 230), 
									 vertical_leap=randint(20, 35))
				names_index += 1

		for team in Team.objects.all():
			for team2 in Team.objects.all():
				if team != team2:
					print "generated game between {} and {}...".format(team.name, team2.name)
					home_team_score = randint(50, 100)
					away_team_score = randint(50, 100)
					while away_team_score == home_team_score:
						away_team_score = randint(50, 100)

					game = Game.objects.create(home_team=team, 
											   home_team_score=home_team_score, 
											   away_team=team2, 
											   away_team_score=away_team_score, 
											   date=date.today())
					GameFilm.objects.create(game=game,
											coach_uploaded_by=team.coach, 
											duration=37, 
											file_size=10000, 
											mpd_url="https://s3.amazonaws.com/kykersports/basketball_512kb_dash.mpd")
					self.createGamestatsAndClipsForPlayers(game)


		all_athletes = AthleteProfile.objects.all()
		for athlete in all_athletes:
			count = 0
			while count < len(all_athletes):
				athlete.watching.add(all_athletes[count])
				count += randint(1, 10)

		print "Data generated including {} athletes...".format(len(all_athletes))


	def createGamestatsAndClipsForPlayers(self, game):
		self.createGamestatsAndClipsForPlayersOnTeam(game.home_team, game)
		self.createGamestatsAndClipsForPlayersOnTeam(game.away_team, game)


	def createGamestatsAndClipsForPlayersOnTeam(self, team, game):
		for athlete in team.athletes.all():
			
			print "generating gamestat for {}...".format(athlete)
			gamestat = GameStat.objects.create(points=randint(0, 30),
											   rebounds=randint(0, 10),
											   assists=randint(0, 10),
											   blocks=randint(0, 5),
											   steals=randint(0, 4),
											   athlete=athlete,
											   game=game)

			time = 0
			interval = 5
			while (time + interval) < game.gamefilm.duration:
				GameFilmClip.objects.create(athlete=athlete,
											view_count=randint(0, 200),
											gamestat=gamestat,
											game=game,
											gamefilm_start_time=time,
											gamefilm_end_time=time+interval)
				time += interval
				interval = randint(5, 20)