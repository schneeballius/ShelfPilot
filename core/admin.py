from django.contrib import admin
from django.apps import apps

# Name Deiner App (so wie in settings.py hinterlegt)
app_name = 'core'

# Alle Models der App laden
models = apps.get_app_config(app_name).get_models()

# Jedes Model in der Admin-Site registrieren
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass