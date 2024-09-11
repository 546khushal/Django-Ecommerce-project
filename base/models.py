from django.db import models
import uuid

class BaseModels(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False,default=uuid.uuid4)
    created_at =models.DateTimeField(auto_now=True)
    updated_at =models.DateTimeField(auto_now_add=True)

    class Meta:           #yha meta banaya taki main model me Basemoldes ko bheje to class nhi banaye
        abstract = True  