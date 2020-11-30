from django.core.management.base import BaseCommand
import logging
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
from datetime import datetime
from hnet.models import (Raw, Institution, Position, StructuredPost, Category, FailedRenderPost)
import pytz
import time

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
    def noner(self, val):
        if pd.isnull(val):
            return None
        return val
    def handle(self, *args, **options):
        start_time = time.time()
        start = options.get('start', [0])[0]
        finish = options.get('finish', [0])[0]
        todo = Raw.objects.filter(external_id__gte=start, external_id__lte=finish, )

        # Candidates for mapping of the first table:
        # {'Location:', 'Position:', 'Institution Type:'}

        # Candidates for mapping of the second table:
        # {'Secondary Categories:', 'Website:', 'Primary Category:', 'Contact:', 'Closing Date', 'Posting Date:'}
        self.info(f'Going to render {len(todo)} items')
        for raw_item in list(todo):
            try:
                page = raw_item.body
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
                    if isinstance(body_child, Tag) and 'table_border' not in body_child.get('class', ''):
                        # print(body_child.get('class'))
                        body_list.append(body_child.text)
                body = '\n'.join(body_list)

                first = pd.read_html(str(first_table))[0]
                first.columns = ['fieldname', 'fieldvalue']
                first.set_index('fieldname', inplace=True)
                vals = first.to_dict()['fieldvalue']

                positions = vals.get('Position:')
                if pd.isnull(positions):
                   positions =[]
                else:
                    positions = positions.split(',')

                location = self.noner(vals.get('Location:'))


                institution_type = self.noner(vals.get('Institution Type:'))

                last = pd.read_html(str(last_table))[0]
                last.columns = ['fieldname', 'fieldvalue']
                last.set_index('fieldname', inplace=True)
                vals = last.to_dict()['fieldvalue']
                website = self.noner(vals.get('Website:'))
                contact = self.noner(vals.get('Contact:'))
                posting_date_str = self.noner(vals.get('Posting Date:'))
                closing_date_str = self.noner(vals.get('Closing Date'))
                if posting_date_str:
                    posting_date_obj = datetime.strptime(posting_date_str, '%m/%d/%Y')
                else:
                    posting_date_obj = None
                if closing_date_str:
                    closing_date_obj = datetime.strptime(closing_date_str, '%m/%d/%Y')
                else:
                    closing_date_obj = None
                primary_categories = self.get_categories_from_table(last_table, 'Primary Category:')
                secondary_categories = self.get_categories_from_table(last_table, 'Secondary Categories:')
                # we collected all the data, now we need to link them to the existing items in the DB
                primary_category_objects = []
                secondary_category_objects = []
                position_objects = []
                for i in primary_categories:
                    c, _ = Category.objects.get_or_create(description=i)
                    primary_category_objects.append(c)
                for i in secondary_categories:
                    c, _ = Category.objects.get_or_create(description=i)
                    secondary_category_objects.append(c)
                for i in positions:
                    c, _ = Position.objects.get_or_create(description=i)
                    position_objects.append(c)
                institution_object, _ = Institution.objects.get_or_create(description=institution_type)
                try:
                    processed = StructuredPost.objects.get(original=raw_item)
                except StructuredPost.DoesNotExist:
                    processed = StructuredPost(original=raw_item)

                processed.body = body
                processed.institution_type = institution_object
                processed.location = location
                processed.posting_date = posting_date_obj.astimezone(pytz.utc)
                processed.closing_date = closing_date_obj.astimezone(pytz.utc)
                processed.website = website
                processed.contact = contact
                processed.save()
                processed.primary_categories.add(*primary_category_objects)
                processed.secondary_categories.add(*secondary_category_objects)
                processed.positions.add(*position_objects)
                self.info(f'Item {raw_item.external_id} has been successfully rendered')



            except Exception as e:
                FailedRenderPost.objects.get_or_create(external_id=raw_item.external_id)
                self.stdout.write(self.style.ERROR(f'Problem with rendering {raw_item.external_id}/ {raw_item.url}: {str(e)}'))

        print("--- %s seconds ---" % (time.time() - start_time))
