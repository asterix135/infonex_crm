from django.contrib import admin
from .models import Person, Event, Contact


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1


class PersonAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Personal Information', {
            'fields': ['name', 'title', 'company']
        }),
        ('Contact Information', {
            'fields': ['phone', 'email']
        }),
        ('Date information', {
            'fields': ['date_modified', 'date_created']
        })
    ]
    inlines = [ContactInline]
    list_display = ('name', 'company',
                    'was_modified_recently')
    list_filter = ['date_modified', 'date_created']
    search_fields = ['company', 'title', 'name']


class EventAdmin(admin.ModelAdmin):
    fields = ['number', 'city', 'title', 'date_begins']


admin.site.register(Person, PersonAdmin)
admin.site.register(Event, EventAdmin)
