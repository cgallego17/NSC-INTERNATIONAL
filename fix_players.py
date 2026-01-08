import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsc_admin.settings')
django.setup()

from apps.accounts.models import Player, UserProfile
from datetime import date

players = Player.objects.filter(id__in=[26, 27])
positions = ['pitcher', 'catcher', 'shortstop', 'utility']
divisions = ['10U', '12U', '14U']
grades = ['4th', '6th', '8th']

for i, p in enumerate(players, 1):
    p.division = divisions[i % 3]
    p.position = positions[i % 4]
    p.height = "5'10\""
    p.weight = 150 + i*5
    p.jersey_number = 10+i
    p.grade = grades[i % 3]
    p.batting_hand = 'R'
    p.throwing_hand = 'R'
    p.emergency_contact_name = 'Test Contact'
    p.emergency_contact_phone = '555-1234'
    p.emergency_contact_relation = 'Parent'
    p.medical_conditions = 'None'
    p.save()

    prof = p.user.profile
    prof.phone = f'+1 555-000-{i}'
    prof.birth_date = date(2012, 1, 1)
    prof.save()
    print(f'Successfully updated player {p.id} ({p.user.get_full_name()})')

