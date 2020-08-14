from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Guild(models.Model):
    guild_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=40)
    dictator = models.ForeignKey('User', on_delete=models.CASCADE)


class User(AbstractUser):
    # brings in
    #
    # username
    # password
    # email
    # first_name
    # last_name
    # + more
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    guilds = models.ManyToManyField(Guild)
    invites = models.ManyToManyField(Guild, related_name='invites')
    class_name = models.CharField(
        max_length=50, null=True, blank=True, default=None)


class Task(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    info = models.TextField()
    completed = models.BooleanField(default=False)
    minutes = models.IntegerField(null=True, blank=True, default=None)
    deadline = models.DateTimeField(null=True, blank=True, default=None)


class UserTask(Task):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class GuildTask(Task):
    owner = models.ForeignKey(Guild, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
