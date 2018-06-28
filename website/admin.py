from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Frontpage, HeaderImage

admin.site.register(Frontpage, MarkdownxModelAdmin)
admin.site.register(HeaderImage)
