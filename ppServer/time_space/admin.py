from time_space.models.net import Net
from django.contrib import admin

from .models.gates import *
from .models.time_fissures import *

class NetAdmin(admin.ModelAdmin):
	fields = ["text", "startNode"]


class GateAdmin(admin.ModelAdmin):
	pass

class TimeFissureAdmin(admin.ModelAdmin):
	list_display = ["net_id", "stufe", "next_required_input_at"]


# admin.site.register(Net, NetAdmin)

# admin.site.register(Mirror, GateAdmin)
# admin.site.register(Inverter, GateAdmin)
# admin.site.register(Aktivator, GateAdmin)
# admin.site.register(Switch, GateAdmin)
# admin.site.register(Konverter, GateAdmin)
# admin.site.register(Barriere, GateAdmin)
# admin.site.register(Manadegenerator, GateAdmin)
# admin.site.register(Manabombe, GateAdmin)
# admin.site.register(Supportgatter, GateAdmin)
# admin.site.register(Teleportgatter, GateAdmin)
# admin.site.register(Sensorgatter, GateAdmin)
# admin.site.register(Tracinggatter, GateAdmin)

# admin.site.register(Linearriss, TimeFissureAdmin)
# admin.site.register(Liniendeletion, TimeFissureAdmin)
# admin.site.register(Splinter, TimeFissureAdmin)
# admin.site.register(Metasplinter, TimeFissureAdmin)
# admin.site.register(Duplikator, TimeFissureAdmin)
# admin.site.register(Looper, TimeFissureAdmin)
# admin.site.register(Timelagger, TimeFissureAdmin)
# admin.site.register(Timedelayer, TimeFissureAdmin)
# admin.site.register(Runner, TimeFissureAdmin)