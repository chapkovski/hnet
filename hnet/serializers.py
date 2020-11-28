from django.conf.urls import url, include
from .models import Raw
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class RawSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Raw
        fields = ['url', 'body', 'external_id']

# ViewSets define the view behavior.
class RawViewSet(viewsets.ModelViewSet):
    queryset = Raw.objects.all()
    serializer_class = RawSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'rawitems', RawViewSet)