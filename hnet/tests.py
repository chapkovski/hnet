from hnet.models import StructuredPost
import pandas as pd
from django.db.models import Count, DateTimeField, F, Func, Value, CharField, ExpressionWrapper,Avg
from django.db.models.functions import Trunc
import csv
import sys
import pprint
from django.core import serializers
import json
pp = pprint.PrettyPrinter(indent=4)
# s=StructuredPost.objects.filter(original__external_id=60864).values()
# print(StructuredPost.objects.filter(original__external_id=60864).count())
# s2 = StructuredPost.objects.filter(original__external_id=60864).only('institution_type')
# qs_json = serializers.serialize('json', s2, fields=('institution_type__description'))
# # print(s)
# pp.pprint(qs_json)

t=StructuredPost.objects.annotate(c=Count('primary_categories')).values('c','original__external_id')
filtered=[i for i in t if i.get('c')>1]
# TODO - redo to one to one structured post to Raw
# TODO - redo primary category to Foreign key instead of M2M. redo Antropology&Archaeology to one category
print(StructuredPost.objects.filter(secondary_categories__description='Anthropology').count())
print(StructuredPost.objects.filter(secondary_categories__description='Archaeology').count())
l=[]
for i in filtered:
    qid=i.get('original__external_id')
    print(qid)
    p=StructuredPost.objects.filter(original__external_id=qid).first()
    l.extend(p.primary_categories.all())
    print(p.primary_categories.all(),
                   p.original.external_id)
print(set(l))
# df = pd.DataFrame(list(StructuredPost.objects.annotate(c=Count('primary_categories')).values('c')))
# d=df[df.c.eq(2)]
# d.index.name = 'newhead'
# cands=list(d.index)
# for i in cands:
#     print(StructuredPost.objects.get(id=i).primary_categories.all(),
#           StructuredPost.objects.get(id=i).original.external_id)
# print(StructuredPost.objects.filter(id__in=cands).values("primary_categories__description").distinct())
# print(StructuredPost.objects.get(id).values("primary_categories__description").distinct())
sys.exit()

weekly_data = StructuredPost.objects.annotate(week=Trunc('posting_date', 'week', output_field=DateTimeField())).values(
    'week'
).annotate(posts=Count('id'))

weekly_data = [{**i, **{'week': i.get('week').strftime("%m/%d/%Y")}} for i in weekly_data]

with open('eggs.csv', 'w', newline='') as csvfile:
    fieldnames = ['week', 'posts']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for j, i in enumerate(weekly_data):
        if j % 100 == 0:
            print(f"{j // 100} hundred")
        writer.writerow(i)
