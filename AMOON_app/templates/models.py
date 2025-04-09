import json
from django.db import models
from django.contrib.auth.models import User

class CV(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    summary = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_profile = models.URLField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    _skills = models.TextField(db_column='skills', blank=True)  # تخزين المهارات كـ JSON
    languages = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def skills(self):
        if not self._skills:
            return []
        try:
            return json.loads(self._skills)
        except json.JSONDecodeError:
            return []

    @skills.setter
    def skills(self, value):
        if isinstance(value, str):
            self._skills = value
        else:
            self._skills = json.dumps(value)

    def __str__(self):
        return f"{self.user.username}'s CV" 