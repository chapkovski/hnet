import requests
import os, django
from bs4 import BeautifulSoup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hnetproj.settings")
django.setup()
from hnet.models import Raw
from django.db.models import Max

posting_api = 'http://127.0.0.1:8000/rawitems/'
start_id = 1
bunch = 25000
head = 'https://www.h-net.org/jobs/job_display.php?id='
not_found = []
found = []
# max_id = Raw.objects.all().aggregate(mid=Max('external_id'))['mid']
max_id=1
chosen = range(max_id, max_id + bunch)

for j, i in enumerate(chosen):
    try:
        Raw.objects.get(external_id=i)
        print(f'{i} already exists')
    except (Raw.DoesNotExist, Raw.MultipleObjectsReturned):
        url = f'{head}{i}'
        page = requests.get(url)
        print(f'{j}: Retrieving {url}: {page.status_code}')
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            error = soup.find('p', class_='error')
            if error:
                print('NOT FOUND', i)
                not_found.append(i)
            else:
                found.append(i)
                r = requests.post(
                    posting_api,
                    dict(external_id=i, url=url, body=page.text)
                )

        else:
            print(f'BROKEN AT {i}')
            break

print(f'TOT NOT FOUND: {len(not_found)} or {(len(not_found)/bunch):.0%}')