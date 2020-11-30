from django.core.management.base import BaseCommand
import logging
from bs4 import  BeautifulSoup, NavigableString, Tag
import pandas as pd
from datetime import datetime
from hnet.models import (Raw, Institution, Position, StructuredPost, Category)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process collected data from hnet'

    def info(self, *s):
        i = ' '.join([str(j) for j in s])
        self.stdout.write(self.style.SUCCESS(str(i)))

    def add_arguments(self, parser):
        parser.add_argument('start', nargs='+', type=int)
        parser.add_argument('finish', nargs='+', type=int)
    def get_categories_from_table(self, table, categories_name):
        td = table.find(lambda t: t.text.strip() == categories_name)
        if td:
            td2 = td.find_next('td')
            categories = [i.text for i in td2.find_all('a')]
            return categories

    def handle(self, *args, **options):
        start = options.get('start', [0])[0]
        finish = options.get('finish', [0])[0]

        initial_list = set(range(start, finish + 1))
        todo = Raw.objects.filter(external_id__lte=start, external_id__gte=finish)

        resq = []
        # Candidates for mapping of the first table:
        # {'Location:', 'Position:', 'Institution Type:'}

        # Candidates for mapping of the second table:
        # {'Secondary Categories:', 'Website:', 'Primary Category:', 'Contact:', 'Closing Date', 'Posting Date:'}
        self.info(f'Going to render {len(todo)} items')
        for i in list(todo):
            try:
                page = i.body
                soup = BeautifulSoup(page, 'html.parser')
                tables = soup.find_all('table', class_='table_border')
                first_table = tables[0]
                last_table = tables[-1]
                body_list = []
                """Let's first extract the body"""
                body_container = soup.select_one("div.nav_end > div.text")
                for body_child in body_container.findChildren(recursive=False):
                    if isinstance(body_child, NavigableString):
                        continue
                    if isinstance(body_child, Tag) and 'table_border' not in  body_child.get('class','') :
                        # print(body_child.get('class'))
                        body_list.append(body_child.text)
                body = '\n'.join(body_list)





                first = pd.read_html(str(first_table))[0]
                first.columns = ['fieldname', 'fieldvalue']
                first.set_index('fieldname', inplace=True)
                vals = first.to_dict()['fieldvalue']
                positions = vals.get('Position:').split(',')
                location = vals.get('Location:')
                institution_type = vals.get('Institution Type:')
                inst_obj, _ = Institution.objects.get_or_create(description=institution_type)
                self.info(f'POSITION: {positions} {location} {institution_type}')
                last = pd.read_html(str(last_table))[0]
                last.columns = ['fieldname', 'fieldvalue']
                last.set_index('fieldname', inplace=True)
                vals = last.to_dict()['fieldvalue']
                website = vals.get('Website:')
                contact = vals.get('Contact:')
                posting_date_str = vals.get('Posting Date:')
                closing_date_str = vals.get('Closing Date')
                posting_date_obj = datetime.strptime(posting_date_str, '%m/%d/%Y')
                closing_date_obj = datetime.strptime(closing_date_str, '%m/%d/%Y')
                primary_categories = self.get_categories_from_table(last_table,'Primary Category:' )
                secondary_categories = self.get_categories_from_table(last_table, 'Secondary Categories:' )





            except Exception as e:
                print(type(e).__name__)
                self.stdout.write(self.style.ERROR(f'Problem with rendering {i.id}: {str(e)}'))
