from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Guild(models.Model):
    guild_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=40)

# brings in
#
# username
# password
# email
# first_name
# last_name
# + more


class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    guilds = models.ManyToManyField(Guild)


class Task(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    info = models.TextField()
    completed = models.BooleanField(default=False)


class UserTask(Task):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class GuildTask(Task):
    owner = models.ForeignKey(Guild, on_delete=models.CASCADE)
