from django.shortcuts import render, redirect, get_object_or_404


def error_404(request, *args, **argv):
    content = {}
    return render(request, 'base/error_404.html', content)
