from hnet.models import StructuredPost, Category
import pandas as pd
from django.db.models import Count, DateTimeField, F, Func, Value, CharField, ExpressionWrapper,Avg
from django.db.models.functions import Trunc
import csv
import sys
import pprint
from django.core import serializers
import json
pp = pprint.PrettyPrinter(indent=4)
print=pp.pprint
doubleC,_=Category.objects.get_or_create(description='Archaelogy/Antrhopology')
print(f'{doubleC}: {_}')
doubles=StructuredPost.objects.annotate(c=Count('primary_categories')).filter(main_category__isnull=True,c=1)
print(f'Before update {doubles.count()}')
to_update=[]
for d in doubles:
    d.main_category=d.primary_categories.first()
    to_update.append(d)
StructuredPost.objects.bulk_update(to_update,fields=['main_category'])
print(f'After update {doubles.count()}')


