"""
Comando para migrar nombres de huéspedes adicionales desde notes a additional_guest_names
en reservas antiguas.
"""

import re
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.locations.models import HotelReservation


class Command(BaseCommand):
    help = "Migra nombres de huéspedes adicionales desde notes a additional_guest_names en reservas antiguas"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Solo muestra lo que se migraría sin hacer cambios",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limitar el número de reservas a procesar (útil para pruebas)",
        )

    def extract_guest_names_from_notes(self, notes_text):
        """
        Extrae nombres de huéspedes desde el campo notes.
        Retorna una tupla (additional_guest_names, clean_notes)
        """
        if not notes_text:
            return "", ""

        guest_names_list = []
        clean_notes = notes_text

        # Verificar si contiene el formato esperado
        has_guest_info = (
            "Selected players/children:" in notes_text
            or "Additional adults:" in notes_text
            or "Additional children:" in notes_text
        )

        if not has_guest_info:
            return "", notes_text

        # Extraer nombres de "Selected players/children:"
        players_match = re.search(r"Selected players/children:\s*([^|]+)", notes_text)
        if players_match:
            players_str = players_match.group(1).strip()
            # El texto puede tener múltiples nombres separados por | o estar en un solo bloque
            # Primero intentar dividir por |
            if '|' in players_str:
                player_entries = [p.strip() for p in players_str.split('|') if p.strip()]
            else:
                player_entries = [players_str]

            for entry in player_entries:
                # Extraer el nombre antes de cualquier paréntesis
                # Buscar el primer nombre completo (hasta el primer paréntesis o fin de línea)
                name_part = re.match(r'^([^(|]+)', entry.strip())
                if name_part:
                    clean_name = name_part.group(1).strip()
                    # Limpiar: remover emails, fechas, comas
                    clean_name = re.sub(r'\s*,\s*[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\s*', '', clean_name, flags=re.IGNORECASE).strip()
                    clean_name = re.sub(r'\s*\([^)]*@[^)]+\)\s*', '', clean_name).strip()
                    clean_name = re.sub(r'\s*\(\d{4}-\d{2}-\d{2}[^)]*\)\s*', '', clean_name).strip()
                    clean_name = re.sub(r'\s*\([^)]+\)\s*', '', clean_name).strip()
                    clean_name = clean_name.strip()
                    if clean_name and len(clean_name) > 1 and not clean_name.startswith('('):
                        guest_names_list.append(clean_name)

        # Extraer nombres de "Additional adults:"
        adults_match = re.search(r"Additional adults:\s*([^|]+)", notes_text)
        if adults_match:
            adults_str = adults_match.group(1).strip()
            # El texto puede terminar con | o al final de la línea
            # Remover el | final si existe
            adults_str = re.sub(r'\s*\|\s*$', '', adults_str).strip()

            # Extraer nombres: buscar patrones como "Nombre (fecha)" o solo "Nombre"
            # Puede haber múltiples separados por |
            adult_entries = [e.strip() for e in adults_str.split('|') if e.strip()]
            if not adult_entries:
                adult_entries = [adults_str]

            for entry in adult_entries:
                entry = entry.strip()
                if not entry:
                    continue
                # Extraer el nombre antes del primer paréntesis
                name_match = re.match(r'^([^(|]+)', entry)
                if name_match:
                    clean_name = name_match.group(1).strip()
                    # Remover espacios extra y caracteres residuales
                    clean_name = clean_name.strip()
                    if clean_name and len(clean_name) > 1:
                        guest_names_list.append(clean_name)

        # Extraer nombres de "Additional children:"
        children_match = re.search(r"Additional children:\s*([^|]+)", notes_text)
        if children_match:
            children_str = children_match.group(1).strip()
            # El texto puede terminar con | o al final de la línea
            # Remover el | final si existe
            children_str = re.sub(r'\s*\|\s*$', '', children_str).strip()

            # Extraer nombres: buscar patrones como "Nombre (fecha)" o solo "Nombre"
            # Puede haber múltiples separados por |
            child_entries = [e.strip() for e in children_str.split('|') if e.strip()]
            if not child_entries:
                child_entries = [children_str]

            for entry in child_entries:
                entry = entry.strip()
                if not entry:
                    continue
                # Extraer el nombre antes del primer paréntesis
                name_match = re.match(r'^([^(|]+)', entry)
                if name_match:
                    clean_name = name_match.group(1).strip()
                    # Remover espacios extra y caracteres residuales
                    clean_name = clean_name.strip()
                    if clean_name and len(clean_name) > 1:
                        guest_names_list.append(clean_name)

        # Construir additional_guest_names (uno por línea)
        additional_guest_names = "\n".join(guest_names_list) if guest_names_list else ""

        # Limpiar notes: mantener solo información del pago si existe, sino eliminar todo el texto migrado
        # Intentar preservar información de Stripe session si existe
        stripe_match = re.search(r'Reserva pagada vía Stripe session ([a-zA-Z0-9_]+)', notes_text)
        if stripe_match:
            clean_notes = f"Reserva pagada vía Stripe session {stripe_match.group(1)}"
        else:
            # Si no hay información de Stripe, intentar preservar otras notas que no sean de huéspedes
            # Eliminar las secciones que migramos
            clean_notes = re.sub(r'Selected players/children:[^|]*(\||$)', '', notes_text)
            clean_notes = re.sub(r'Additional adults:[^|]*(\||$)', '', clean_notes)
            clean_notes = re.sub(r'Additional children:[^|]*(\||$)', '', clean_notes)
            clean_notes = re.sub(r'\s*\|\s*', ' ', clean_notes)  # Limpiar separadores |
            clean_notes = clean_notes.strip()
            # Si quedó vacío, usar un mensaje por defecto
            if not clean_notes:
                clean_notes = "Reserva migrada desde sistema anterior"

        return additional_guest_names, clean_notes

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options.get("limit")

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("MIGRACION DE NOMBRES DE HUESPEDES ADICIONALES"))
        self.stdout.write(self.style.SUCCESS("=" * 60))

        # Buscar reservas con información de huéspedes en notes
        reservations = HotelReservation.objects.filter(
            notes__icontains="Selected players/children"
        ) | HotelReservation.objects.filter(
            notes__icontains="Additional adults"
        ) | HotelReservation.objects.filter(
            notes__icontains="Additional children"
        )

        # Excluir reservas que ya tienen additional_guest_names
        reservations = reservations.filter(
            additional_guest_names__isnull=True
        ) | reservations.filter(
            additional_guest_names=""
        )

        if limit:
            reservations = reservations[:limit]

        total = reservations.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("No se encontraron reservas para migrar."))
            return

        self.stdout.write(f"\nReservas encontradas: {total}")
        if dry_run:
            self.stdout.write(self.style.WARNING("\nMODO DRY-RUN: No se realizaran cambios\n"))
        else:
            self.stdout.write("\nIniciando migracion...\n")

        migrated = 0
        skipped = 0
        errors = 0

        with transaction.atomic():
            for reservation in reservations:
                try:
                    additional_guest_names, clean_notes = self.extract_guest_names_from_notes(
                        reservation.notes
                    )

                    if not additional_guest_names:
                        skipped += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Reserva #{reservation.id}: No se encontraron nombres para migrar"
                            )
                        )
                        continue

                    if dry_run:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"[OK] Reserva #{reservation.id}:\n"
                                f"  Nombres a migrar: {len(additional_guest_names.splitlines())}\n"
                                f"  {additional_guest_names.replace(chr(10), ', ')}\n"
                                f"  Notes anterior: {reservation.notes[:100]}...\n"
                                f"  Notes nuevo: {clean_notes}"
                            )
                        )
                    else:
                        reservation.additional_guest_names = additional_guest_names
                        reservation.notes = clean_notes
                        reservation.save(update_fields=["additional_guest_names", "notes"])
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"[OK] Reserva #{reservation.id}: Migrados {len(additional_guest_names.splitlines())} nombres"
                            )
                        )

                    migrated += 1

                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f"[ERROR] Error en reserva #{reservation.id}: {str(e)}")
                    )

            if dry_run:
                # En dry-run, no hacer commit
                transaction.set_rollback(True)

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("RESUMEN"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total de reservas procesadas: {total}")
        self.stdout.write(self.style.SUCCESS(f"Migradas exitosamente: {migrated}"))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f"Omitidas (sin nombres): {skipped}"))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f"Errores: {errors}"))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nEsta fue una ejecucion DRY-RUN. Ejecuta sin --dry-run para aplicar los cambios."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\nMigracion completada exitosamente!")
            )

