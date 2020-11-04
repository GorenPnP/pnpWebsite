from django.shortcuts import render, redirect, get_object_or_404


def error_404(request, *args, **argv):
    content = {}
    return render(request, 'base/error_404.html', content)


def error_500(request, *args, **argv):
    content = {'image': File.objects.filter(file__icontains='404')[0].file}
    return render(request, 'base/error_404.html', content)


def error_418(request, *args, **argv):
    content = {'image': File.objects.filter(file__icontains='418')[0].file}
    return render(request, 'base/error_404.html', content)
