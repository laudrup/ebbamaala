from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Frontpage

admin.site.register(Frontpage, MarkdownxModelAdmin)
