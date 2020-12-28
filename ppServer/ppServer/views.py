from django.shortcuts import render


def error_404(request, *args, **argv):
    content = {}
    return render(request, 'base/error_404.html', content)
