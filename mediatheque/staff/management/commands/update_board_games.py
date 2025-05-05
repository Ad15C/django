# staff/management/commands/update_board_games.py
from django.core.management.base import BaseCommand
from staff.models import MediaStaff

class Command(BaseCommand):
    help = 'Met à jour tous les jeux de plateau avec can_borrow=False'

    def handle(self, *args, **kwargs):
        board_games = MediaStaff.objects.filter(media_type='board_game')
        updated_count = board_games.update(can_borrow=False)
        self.stdout.write(self.style.SUCCESS(f'{updated_count} jeux de plateau ont été mis à jour avec can_borrow=False'))
