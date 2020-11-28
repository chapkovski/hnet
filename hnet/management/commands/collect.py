from django.core.management.base import BaseCommand, CommandError
from hnet.models import Raw, UnfoundRecord
import sys
import re
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from bs4 import BeautifulSoup
from django.db.models import Max
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Collect data from hnet'

    def add_arguments(self, parser):
        parser.add_argument('start', nargs='+', type=int)
        parser.add_argument('finish', nargs='+', type=int)

    def handle(self, *args, **options):
        start = options.get('start', [0])[0]
        finish = options.get('finish', [0])[0]
        # Let's get only those which are not already in our db
        initial_list = set(range(start, finish + 1))
        done = Raw.objects.filter(external_id__lte=finish, external_id__gte=start).values_list('external_id', flat=True)
        unfound = UnfoundRecord.objects.filter(external_id__lte=finish, external_id__gte=start).values_list('external_id', flat=True)
        todo = list(initial_list - set(done) - set(unfound))
        if not todo:
            self.stdout.write(self.style.ERROR(f'NOTHGING TO DO!'))
            return
        else:
            self.stdout.write(self.style.SUCCESS(f'Going to scrape {len(todo)} records from H-Net'))

        with FuturesSession() as s:
            idre = '\?id=(?P<external>\d*)$'
            head = 'https://www.h-net.org/jobs/job_display.php?id='
            futures = [s.get(f'{head}{i}') for i in todo]
            for future in as_completed(futures):
                page = future.result()
                m = re.search(idre, page.url)
                external = int(m.group('external'))
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'html.parser')
                    error = soup.find('p', class_='error')
                    if error:
                        UnfoundRecord.objects.create(external_id=external)
                        self.stdout.write(self.style.WARNING(f'NOT FOUND:  {external}. I added it to UNFOUND records'))
                    else:
                        Raw.objects.create(external_id=external, url=page.url, body=page.text)
                        self.stdout.write(self.style.SUCCESS(f'Created {external}'))
                else:
                    raise Exception(f'WRONG CODE for {page.url}:{page.status_code}')
