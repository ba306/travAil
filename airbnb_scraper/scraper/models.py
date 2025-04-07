from django.db import models


class Search(models.Model):
    email = models.EmailField()
    start_date = models.DateField()
    end_date = models.DateField()
    num_adults = models.IntegerField()
    max_price = models.IntegerField()
    ne_lat = models.FloatField()
    ne_lng = models.FloatField()
    sw_lat = models.FloatField()
    sw_lng = models.FloatField()
    search_time = models.DateTimeField(auto_now_add=True)
    frequency_interval = models.IntegerField(default=1)
    frequency_unit = models.CharField(max_length=10, default='hours')
    task_id = models.CharField(max_length=255, blank=True, null=True)
    min_rating = models.FloatField(null=True, blank=True)
    min_reviews = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return f"Search {self.id} by {self.email}"


class SearchResult(models.Model):
    search = models.ForeignKey(Search, on_delete=models.CASCADE, related_name='results')
    url = models.URLField()
    normalized_url = models.CharField(max_length=255)

    class Meta:
        unique_together = ('search', 'normalized_url')

    def __str__(self):
        return self.url