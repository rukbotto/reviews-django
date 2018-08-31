from django.contrib import admin

from api.models import Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'rating', 'company', 'reviewer')
    list_filter = ('rating',)
    search_fields = ['title', 'company', 'reviewer']


admin.site.register(Review, ReviewAdmin)
