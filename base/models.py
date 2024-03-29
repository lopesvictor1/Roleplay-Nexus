#onde ficam armazenados os modelos das tabelas do banco de dados
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    about = models.TextField(max_length=200)
    avatar = models.ImageField(upload_to='media/avatars', default='media/avatars/avatar.svg', blank=True)


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    hostProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)           #o host da sala de conversas é um user
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null = True, blank = True)
    participants = models.ManyToManyField(UserProfile, related_name='participants', blank = True)     #como os participantes da sala são do mesmo tipo já declarado anteriormente, temos que dar um nome para a coluna da tabela relacional, que nesse caso vai ser participants
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    

class Message(models.Model):
    userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        if len(self.body) > 50:
            return self.body[0:50]+"... "
        else:
            return self.body


