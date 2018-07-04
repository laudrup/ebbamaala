from django.contrib import admin
from imagekit.admin import AdminThumbnail
from markdownx.admin import MarkdownxModelAdmin

from .models import Frontpage, Gallery, HeaderImage, PracticalInfo, GalleryPhoto


class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    image_display = AdminThumbnail(image_field='thumbnail')
    readonly_fields = ['image_display', 'date']


class GalleryAdmin(admin.ModelAdmin):
    inlines = [GalleryPhotoInline]

    def save_model(self, request, obj, form, change):
        obj.save()

        for afile in request.FILES.getlist('photos_multiple'):
            obj.galleryphoto_set.create(photo=afile)


class HeaderImageAdmin(admin.ModelAdmin):
    image_display = AdminThumbnail(image_field='thumbnail')
    list_display = ('__str__', 'image_display')
    readonly_fields = ['image_display']


admin.site.register(Frontpage, MarkdownxModelAdmin)
admin.site.register(PracticalInfo, MarkdownxModelAdmin)
admin.site.register(HeaderImage, HeaderImageAdmin)
admin.site.register(Gallery, GalleryAdmin)
