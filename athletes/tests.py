from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from models import *
import datetime

class NotificationTestCase(TestCase):
    def setUp(self):

    	Group.objects.create(name='athletes')
    	Group.objects.create(name='coaches')


    	team1 = Team.objects.create(city='Indianapolis', state='Indiana', name='Park Tudor Panthers')
    	team2 = Team.objects.create(city='Carmel', state='Indiana', name='Carmel Greyhounds')
        athlete_user_1 = User.objects.create_user(username='student1@example.com', password='password01')
        athlete_user_2 = User.objects.create_user(username='student2@example.com', password='password02')
        coach_user_1 = User.objects.create_user(username='coach1@example.com', password='password03')
        self.athlete_1 = AthleteProfile.objects.create(athlete=athlete_user_1, date_of_birth=datetime.date.today(), current_team=team1,
        	height=75, weight=180, vertical_leap=34)
       	self.athlete_2 = AthleteProfile.objects.create(athlete=athlete_user_2, date_of_birth=datetime.date.today(), current_team=team2,
        	height=75, weight=180, vertical_leap=34)
       	coach_1 = CoachProfile.objects.create(coach=coach_user_1, date_of_birth=datetime.date.today(), current_team=team1)
       	game = Game.objects.create(home_team=team1, away_team=team2, date=datetime.date.today())
       	self.game_film = GameFilm.objects.create(game=game, coach_uploaded_by=coach_1, duration=100, file_size=100000, video_id=0, encoded_id=0)



    def test_notifications_created(self):
        """Ensure that when gamefilm is created all athletes on home and away team are notified"""
        self.assertEqual(GameFilmPostedNotification.objects.count(), 2)
        self.assertEqual(self.athlete_1.notifications.first().game_film.id, self.game_film.id)
        self.assertEqual(self.athlete_2.notifications.first().game_film.id, self.game_film.id)
        

