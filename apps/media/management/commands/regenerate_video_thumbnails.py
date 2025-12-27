"""
Comando de gestión para regenerar thumbnails de videos existentes
"""
from django.core.management.base import BaseCommand
from apps.media.models import MediaFile
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Regenera thumbnails para videos que no tienen miniatura'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerar thumbnails para todos los videos, incluso si ya tienen uno',
        )

    def handle(self, *args, **options):
        # Obtener videos sin thumbnail o todos si se especifica --all
        if options['all']:
            videos = MediaFile.objects.filter(file_type='video')
            self.stdout.write(self.style.WARNING('Regenerando thumbnails para TODOS los videos...'))
        else:
            videos = MediaFile.objects.filter(file_type='video', thumbnail__isnull=True)
            self.stdout.write(self.style.SUCCESS('Regenerando thumbnails para videos sin miniatura...'))

        total = videos.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No hay videos que procesar.'))
            return

        self.stdout.write(f'Encontrados {total} video(s) para procesar.')

        success_count = 0
        error_count = 0

        for video in videos:
            try:
                if not video.original_file:
                    self.stdout.write(
                        self.style.WARNING(f'  [WARNING] Video {video.id} ({video.title}) no tiene archivo original')
                    )
                    continue

                original_path = video.original_file.path
                self.stdout.write(f'  Procesando: {video.title} (ID: {video.id})...')

                # Generar thumbnail
                video._generate_video_thumbnail(original_path)

                # Guardar si se generó el thumbnail
                if video.thumbnail:
                    video.save(update_fields=['thumbnail'])
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'    [OK] Thumbnail generado exitosamente')
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'    [ERROR] No se pudo generar el thumbnail')
                    )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'    [ERROR] Error: {str(e)}')
                )
                logger.error(f'Error regenerando thumbnail para video {video.id}: {e}', exc_info=True)

        # Resumen
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'[OK] Procesados exitosamente: {success_count}'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'[ERROR] Errores: {error_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total procesado: {total} video(s)'))

