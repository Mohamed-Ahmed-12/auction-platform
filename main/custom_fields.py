<<<<<<< HEAD
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
=======
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
>>>>>>> d41bd5c2f71c127f5bc5d5e18d3eed1ed818de8e
