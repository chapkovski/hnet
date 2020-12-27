from django.conf.urls import url, include
from .models import Raw, StructuredPost, Category, Institution, Position
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class RawSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Raw
        fields = ['url', 'body', 'external_id']


class CatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['description']


class InstSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Institution
        fields = ['description']


class PositionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Position
        fields = ['description']


class PostSerializer(serializers.HyperlinkedModelSerializer):
    primary_categories = CatSerializer(read_only=True, many=True)
    secondary_categories = CatSerializer(read_only=True, many=True)
    institution_type = InstSerializer(read_only=True)
    positions = PositionSerializer(read_only=True, many=True)

    class Meta:
        model = StructuredPost
        fields = ['primary_categories',
                  'secondary_categories',
                  'institution_type',
                  'location',
                  'positions',
                  'posting_date',
                  'closing_date',
                  'website',
                  'contact',
                  ]

    """primary_categories = models.ManyToManyField(Category, blank=True, related_name='primary_posts')
    secondary_categories = models.ManyToManyField(Category, blank=True, related_name='secondary_posts')
    body = models.TextField(blank=True, null=True)
    institution_type = models.ForeignKey(to=Institution, blank=True, null=True, on_delete=models.CASCADE)
    location = models.CharField(max_length=1000, blank=True, null=True)
    positions = models.ManyToManyField(Position, blank=True)
    posting_date = models.DateTimeField(blank=True, null=True)
    closing_date = models.DateTimeField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact = models.CharField(blank=True, null=True, max_length=10000, )"""


# ViewSets define the view behavior.
class RawViewSet(viewsets.ModelViewSet):
    queryset = Raw.objects.all()
    serializer_class = RawSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = StructuredPost.objects.all()
    serializer_class = PostSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'rawitems', RawViewSet)
router.register(r'posts', PostViewSet)
