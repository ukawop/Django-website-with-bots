from django.contrib.auth.models import User
from django.db import models

from django.utils.text import slugify



class Room(models.Model):
    user = models.ForeignKey(User, related_name='room', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    bot_token = models.CharField(max_length=255, unique=True)
    is_group = models.BooleanField(default=False)

    class Meta:
        db_table = 'room'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            index = 1
            while Room.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{index}"
                index += 1
            self.slug = slug
        super().save(*args, **kwargs)


class CloneRoom(models.Model):
    room = models.ForeignKey(Room, related_name='cloneroom', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='cloneroom', on_delete=models.CASCADE)



class Message(models.Model):
    room = models.ForeignKey(Room, related_name='messages', on_delete=models.CASCADE)
    clone_room = models.ForeignKey(CloneRoom, related_name='messages', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    is_bot = models.BooleanField(default=False)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/', null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
        db_table = 'messages'






