from django.core.management.base import BaseCommand, CommandError
from hnet.models import Raw
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
        start = options.get('start',[0])[0]
        finish = options.get('finish',[0])[0]
        with FuturesSession() as s:
            idre = '\?id=(?P<external>\d*)$'
            head = 'https://www.h-net.org/jobs/job_display.php?id='
            futures = [s.get(f'{head}{i}') for i in range(start, finish+1)]
            for future in as_completed(futures):
                page = future.result()
                m = re.search(idre, page.url)
                external = int(m.group('external'))
                if page.status_code == 200:
                    soup = BeautifulSoup(page.text, 'html.parser')
                    error = soup.find('p', class_='error')
                    if error:
                        logger.warning(f'NOT FOUND:  {external}')
                    else:
                        try:
                            Raw.objects.get(external_id=external)
                            logger.warning(f'{external} already exists')
                        except Raw.DoesNotExist:
                            self.stdout.write(self.style.SUCCESS(f'Creating {external}'))
                            
                            Raw.objects.create(
                                external_id=external, url=page.url, body=page.text)

                else:
                    raise Exception(f'WRONG CODE for {page.url}:{page.status_code}')