from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid



class Guild(models.Model):
    group_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=40)

# brings in 
#
# username
# password
# email
# first_name
# last_name
class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    guilds = models.ManyToManyField(Guild)
