from django.db import models
from django.contrib.auth.models import User
from memes.models import Meme

class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name='threads')
    is_accepted = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Thread {self.id} with {', '.join([p.username for p in self.participants.all()])}"

class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(blank=True)
    meme = models.ForeignKey(Meme, on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_in_messages')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        content = self.text[:20] if self.text else "[Shared Meme]"
        return f"{self.sender.username}: {content}"
