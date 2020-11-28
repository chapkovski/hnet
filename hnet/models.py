from django.db import models


# Create your models here.
class TrackerModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Raw(TrackerModel):
    external_id = models.IntegerField()
    body = models.TextField()
    url = models.URLField()

class UnfoundRecord(TrackerModel):
    external_id = models.IntegerField()

class GeneralCategory(TrackerModel):
    description = models.CharField(max_length=1000, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.description


class Category(GeneralCategory):
    pass


class Institution(GeneralCategory):
    pass


class Position(GeneralCategory):
    pass


class StructuredPost(TrackerModel):
    """
    That is the class we we store rendered data. It contains link to the orininal data
    plus some parsed info - text of the ad, categories (primary and secondary) etc.
    """
    original = models.ForeignKey(to=Raw, on_delete=models.CASCADE)
    primary_categories = models.ManyToManyField(Category, blank=True, related_name='primary_posts')
    secondary_categories = models.ManyToManyField(Category, blank=True, related_name='secondary_posts')
    body = models.TextField(blank=True, null=True)
    institution_type = models.ForeignKey(to=Institution, blank=True, null=True, on_delete=models.CASCADE)
    location = models.CharField(max_length=1000, blank=True, null=True)
    positions = models.ManyToManyField(Position, blank=True)
    posting_date = models.DateTimeField(blank=True, null=True)
    closing_date = models.DateTimeField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact = models.CharField(blank=True, null=True, max_length=1000, )
