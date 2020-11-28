from django.core.management.base import BaseCommand
import logging
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from hnet.models import Raw

logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Process collected data from hnet'

    def add_arguments(self, parser):
        parser.add_argument('start', nargs='+', type=int)
        parser.add_argument('finish', nargs='+', type=int)

    def handle(self, *args, **options):
        start = options.get('start', [0])[0]
        finish = options.get('finish', [0])[0]
        initial_list = set(range(start, finish + 1))
        done = Raw.objects.filter(external_id__lte=finish, external_id__gte=start).values_list('external_id', flat=True)
        todo = list(initial_list - set(done))

        # rendering first and prepare everything to store in db
        r = Raw.objects.all().order_by('?')[:102]
        # print("R",r.id)
        # q = [r] # replace later with queryset
        q = r
        resq = []
        # Candidates for mapping of the first table:
        # {'Location:', 'Position:', 'Institution Type:'}

        # Candidates for mapping of the second table:
        # {'Secondary Categories:', 'Website:', 'Primary Category:', 'Contact:', 'Closing Date', 'Posting Date:'}

        for i in q:
            try:
                page = i.body
                soup = BeautifulSoup(page, 'html.parser')
                tables = soup.find_all('table', class_='table_border')
                table1 = tables[0]
                table2 = tables[-1]

                # first = pd.read_html(str(table1))[0]
                # first.columns = ['fieldname', 'fieldvalue']
                # first.set_index('fieldname', inplace=True)
                # vals = first.to_dict()['fieldvalue']
                # positions = vals.get('Position:').split(',')
                # institution_type = vals.get('Location:')
                # location = vals.get('Institution Type:')
                # inst_obj,_ = Institution.objects.get_or_create(description=institution_type)
                # pos_to_insert = []
                # for p in positions:
                #     i, _ = Position.objects.get_or_create(description=p)
                #     pos_to_insert.append(i)

                last = pd.read_html(str(table2))[0]
                last.columns = ['fieldname', 'fieldvalue']
                last.set_index('fieldname', inplace=True)
                vals = last.to_dict()['fieldvalue']
                website = vals.get('Website:')
                contact = vals.get('Contact:')
                posting_date_str = vals.get('Posting Date:')

                closing_date_str = vals.get('Closing Date')
                posting_date_obj = datetime.strptime(posting_date_str, '%m/%d/%Y')
                closing_date_obj = datetime.strptime(closing_date_str, '%m/%d/%Y')
                # print(posting_date_obj)
                # print(closing_date_obj)
                print((closing_date_obj - posting_date_obj).days)
                # primary_cats = vals.get('Primary Category:')
                # td1 = table2.find(lambda t: t.text.strip() == 'Primary Category:')
                # if td1:
                #     td2 = td1.find_next('td')
                #     primhrefs = td2.find_all('a')
                #     primrefs_to_add = []
                #     if primhrefs:
                #         for p in primhrefs:
                #             primcat, _ = Category.objects.get_or_create(description=p.text)
                #             primrefs_to_add.append(primcat)
                #
                #
                # td1 = table2.find(lambda t: t.text.strip() == 'Secondary Categories:')
                # if td1:
                #     td2 = td1.find_next('td')
                #     sechrefs = td2.find_all('a')
                #     secrefs_to_add = []
                #     if sechrefs:
                #         for s in sechrefs:
                #             seccat, _ = Category.objects.get_or_create(description=s.text)
                #             secrefs_to_add.append(seccat)
                #
                # print('TO ADD SECCAT', secrefs_to_add)
            except Exception as e:
                print(e)
                print('problem!', i.id, i.url, )
