from ppServer.decorators import verified_account
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from fileserver.models import Map, File


@login_required
@verified_account
def maps(request):
    map_list = []
    maps = Map.objects.all().order_by('titel')
    if not User.objects.filter(username=request.user.username, groups__name='spielleiter').exists():
        for map in maps:
            if map.sichtbar_für.filter(name=request.user.username).exists():
                map_list.append(map)
    else:
        map_list = maps

    context = {'topic': "Dateien", 'maps': map_list}
    return render(request, 'fileserver/maps.html', context)


@login_required
@verified_account
def show_map(request, mapID):
    map = get_object_or_404(Map, id=mapID)

    if not map.sichtbar_für.filter(name=request.user.username).exists() and not \
            User.objects.filter(username=request.user.username, groups__name='spielleiter').exists():
        return redirect('file:index')

    files = []
    for m in map.files.all():
        # get rid of 'files/' prefix
        name = m.file.name[m.file.name.find("/")+1:]
        files.append({'url': m.file.url, 'name': name})

    context = {'files': files, 'topic': map.titel}
    return render(request, 'fileserver/show_map.html', context)
