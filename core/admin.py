from django.contrib import admin
from core.models import datafile, agent_response

# Register your models here.
admin.site.register(datafile)

class agent_responseAdmin(admin.ModelAdmin):
    list_display = ('file', 'response_text', 'actions_to_take', 'gear_Status')
    list_filter = ('gear_Status', 'created_at')
    search_fields = ('file__name', 'response_text', 'actions_to_take')
    
admin.site.register(agent_response, agent_responseAdmin)

