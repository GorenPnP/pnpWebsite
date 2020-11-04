# posts/forms.py
from django import forms
from .models import Image, File, SpielerQuestion


class ImageForm(forms.Form):
	img = forms.ImageField(required=False, label="Bild")


class FileForm(forms.Form):
	file = forms.FileField(required=False, label="Datei")
