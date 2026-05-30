"""
Management command: sync_users
Sinkronisasi Django SQLite dengan Supabase.
Menghapus Django user yang tidak ada di tabel 'users' Supabase.

Usage:
    python manage.py sync_users            # dry-run (hanya tampilkan, tidak hapus)
    python manage.py sync_users --delete   # benar-benar hapus dari SQLite
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from api.supabase_client import supabase


class Command(BaseCommand):
    help = "Sync Django SQLite users with Supabase — removes orphan Django users not found in Supabase."

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete orphan users from SQLite (default: dry-run only).',
        )

    def handle(self, *args, **options):
        do_delete = options['delete']
        mode = "DELETE MODE" if do_delete else "DRY-RUN MODE"
        self.stdout.write(self.style.WARNING(f"\n=== sync_users [{mode}] ===\n"))

        # Fetch all Django users (exclude superusers)
        django_users = User.objects.filter(is_superuser=False)
        total = django_users.count()
        self.stdout.write(f"Total Django users (non-superuser): {total}\n")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("Tidak ada user yang perlu dicek.\n"))
            return

        # Fetch all Supabase user ids
        try:
            supabase_rows = supabase.select('users', {})
            supabase_ids = {str(row['id_user']) for row in supabase_rows}
            self.stdout.write(f"Total Supabase users: {len(supabase_ids)}\n\n")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Gagal mengambil data dari Supabase: {e}"))
            return

        orphans = []
        for user in django_users:
            if str(user.id) not in supabase_ids:
                orphans.append(user)

        if not orphans:
            self.stdout.write(self.style.SUCCESS("✅ Semua Django user ditemukan di Supabase. Tidak ada yang perlu dihapus.\n"))
            return

        self.stdout.write(self.style.WARNING(f"⚠️  Ditemukan {len(orphans)} orphan user (ada di SQLite, tidak ada di Supabase):\n"))
        for user in orphans:
            self.stdout.write(f"   - ID={user.id} | username={user.username} | email={user.email}")

        if do_delete:
            self.stdout.write("")
            deleted_count = 0
            for user in orphans:
                try:
                    # Delete token first to avoid FK constraint issues
                    try:
                        user.auth_token.delete()
                    except Exception:
                        pass
                    username = user.username
                    user.delete()
                    deleted_count += 1
                    self.stdout.write(self.style.SUCCESS(f"   🗑️  Dihapus: {username}"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"   ❌ Gagal hapus {user.username}: {e}"))

            self.stdout.write(self.style.SUCCESS(f"\n✅ Selesai. {deleted_count}/{len(orphans)} user dihapus dari SQLite.\n"))
        else:
            self.stdout.write(self.style.WARNING(
                "\nIni adalah DRY-RUN. Jalankan dengan --delete untuk benar-benar menghapus:\n"
                "   python manage.py sync_users --delete\n"
            ))
