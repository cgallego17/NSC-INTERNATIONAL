"""
Comando para verificar la integridad de todos los wallets del sistema.
Este comando calcula el balance esperado a partir de las transacciones
y compara con el balance almacenado para detectar inconsistencias.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Sum, Q

from apps.accounts.models import UserWallet, WalletTransaction


class Command(BaseCommand):
    help = "Verifica la integridad de todos los wallets comparando balances con transacciones"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Intenta corregir wallets con inconsistencias (NO RECOMENDADO sin backup)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Muestra detalles de todas las verificaciones",
        )

    def handle(self, *args, **options):
        fix = options["fix"]
        verbose = options["verbose"]

        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("VERIFICACIÓN DE INTEGRIDAD DE WALLETS"))
        self.stdout.write(self.style.SUCCESS("=" * 70))

        wallets = UserWallet.objects.all().select_related("user")
        total_wallets = wallets.count()
        valid_count = 0
        invalid_count = 0
        fixed_count = 0

        self.stdout.write(f"\nVerificando {total_wallets} wallets...\n")

        for wallet in wallets:
            is_valid, calculated_balance, actual_balance, discrepancy = wallet.verify_integrity()

            if is_valid:
                valid_count += 1
                if verbose:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Wallet {wallet.user.username} (ID: {wallet.id}): OK - Balance: ${actual_balance}"
                        )
                    )
            else:
                invalid_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Wallet {wallet.user.username} (ID: {wallet.id}): INCONSISTENCIA DETECTADA"
                    )
                )
                self.stdout.write(
                    f"  Balance actual: ${actual_balance} | Balance calculado: ${calculated_balance} | Diferencia: ${discrepancy}"
                )

                if fix:
                    # NO RECOMENDADO: Solo usar si estás absolutamente seguro
                    # En producción, mejor investigar manualmente
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠️  CORRIGIENDO: Actualizando balance de ${actual_balance} a ${calculated_balance}"
                        )
                    )
                    wallet.balance = calculated_balance
                    wallet.save(update_fields=["balance", "updated_at"])
                    fixed_count += 1

        # Resumen
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("RESUMEN"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"Total wallets verificados: {total_wallets}")
        self.stdout.write(self.style.SUCCESS(f"Wallets válidos: {valid_count}"))
        if invalid_count > 0:
            self.stdout.write(self.style.ERROR(f"Wallets con inconsistencias: {invalid_count}"))
            if fix:
                self.stdout.write(self.style.WARNING(f"Wallets corregidos: {fixed_count}"))
        else:
            self.stdout.write(self.style.SUCCESS("✓ Todos los wallets están consistentes"))

        if invalid_count > 0 and not fix:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  ADVERTENCIA: Se detectaron inconsistencias. "
                    "Revisa manualmente antes de usar --fix."
                )
            )
