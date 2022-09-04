from django.contrib import admin

from .models import *

class CategoryInlineAdmin(admin.TabularInline):
    model = News.categories.through
    extra = 1
    verbose_name = "Kategorie"
    verbose_name_plural = "Kategorien"

class NewsAdmin(admin.ModelAdmin):
    fields = ["published", "titel", "summary", "text", "importance", "publisher"]

    list_display = ('titel', 'creation', "published", "importance")

    inlines = [CategoryInlineAdmin]

admin.site.register(Category)
admin.site.register(Publisher)
admin.site.register(News, NewsAdmin)