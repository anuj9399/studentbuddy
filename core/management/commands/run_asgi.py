from django.core.management.base import BaseCommand
from django.core.asgi import get_asgi_application
from daphne.server import Server
import os

class Command(BaseCommand):
    help = 'Run ASGI server with daphne for WebSocket support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port to run the server on'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='Host to bind the server to'
        )

    def handle(self, *args, **options):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        
        application = get_asgi_application()
        
        server = Server(
            application=application,
            host=options['host'],
            port=options['port'],
            verbosity=2,
            access_log=None,
        )
        
        self.stdout.write(f"Running ASGI server on {options['host']}:{options['port']}")
        server.run()
