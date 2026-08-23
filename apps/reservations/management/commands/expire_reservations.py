from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.reservations.models import Reservation


class Command(BaseCommand):
    help = 'Marca como vencidas las reservas activas cuyo tiempo (24h) ya pasó.'

    def handle(self, *args, **options):
        expired = Reservation.objects.filter(
            status=Reservation.STATUS_ACTIVE, expires_at__lte=timezone.now(),
        )
        count = expired.update(status=Reservation.STATUS_EXPIRED)
        self.stdout.write(self.style.SUCCESS(f'{count} reserva(s) marcada(s) como vencidas.'))
