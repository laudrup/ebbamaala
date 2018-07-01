from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Frontpage, PracticalInfo, HeaderImage

admin.site.register(Frontpage, MarkdownxModelAdmin)
admin.site.register(PracticalInfo, MarkdownxModelAdmin)
admin.site.register(HeaderImage)
