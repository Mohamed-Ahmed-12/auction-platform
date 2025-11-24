from django.db import models

def default_location():
    return {
        "country": "",
        "city": "",
        "state": "",
        "longitude": "",
        "latitude": ""
    }

class LocationField(models.JSONField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', default_location)
        super().__init__(*args, **kwargs)
