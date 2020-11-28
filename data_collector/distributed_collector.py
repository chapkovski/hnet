import os, django, re
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
from bs4 import BeautifulSoup
from django.db.models import Max

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hnetproj.settings")
django.setup()

from hnet.models import Raw
print(Raw.objects.count())
# CONSTANTS
bunch = 100
# idre = '\?id=(?P<external>\d*)$'
# head = 'https://www.h-net.org/jobs/job_display.php?id='
#
# # max_id = Raw.objects.all().aggregate(mid=Max('external_id'))['mid']
# max_id=1
# requests_list = range(max_id, max_id + bunch)
# not_found = []
with FuturesSession() as s:
    futures = [s]
    futures = s.get(head)

# with FuturesSession() as s:
#     # print('JOPA', session)
#     # session.get(f'{head}1')
#     # print(requests_list)
#     futures = [s.get(f'{head}{i}') for i in [25000,25001]]
#     #
#     for future in as_completed(futures):
#         page = future.result()
#         print(page)
#     #     m = re.search(idre, page.url)
#     #     external = int(m.group('external'))
#     #     if page.status_code == 200:
#     #         soup = BeautifulSoup(page.text, 'html.parser')
#     #         error = soup.find('p', class_='error')
#     #         if error:
#     #             print('NOT FOUND', external)
#     #             not_found.append(external)
#     #         else:
#     #             try:
#     #                 Raw.objects.get(external_id=external)
#     #                 print(f'{external} already exists')
#     #             except Raw.DoesNotExist:
#     #                 Raw.objects.create(
#     #                     external_id=external, url=page.url, body=page.text)
#     #
#     #     else:
#     #         raise Exception(f'WRONG CODE for {page.url}:{page.status_code}')
#
# print(f'TOT NOT FOUND: {len(not_found)} or {(len(not_found)/bunch):.0%}')