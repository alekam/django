from django.db import models
from django.contrib import admin


__all__ = ['RelatedItem', 'AnotherRelatedItem']


class RelatedItem(models.Model):
    title = models.CharField(max_length=25, blank=True, null=True)

    def __unicode__(self):
        return self.title

class AnotherRelatedItem(models.Model):
    title = models.CharField(max_length=15, blank=True, null=True)

    def __unicode__(self):
        return self.title


admin.site.register(RelatedItem, None)
admin.site.register(AnotherRelatedItem, None)
