"""
Database models for the application
"""
from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class userManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
      """Create and save a user with the given email and password"""
      if not email:
            raise ValueError("Users must have an email address")
      user = self.model(email=self.normalize_email(email), **extra_fields) # <--- GOOD
      user.set_password(password)
      user.save(using=self.db)

      return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user



class user(AbstractBaseUser, PermissionsMixin):
       """This is the user in the system"""
       email = models.EmailField(max_length=255, unique=True)
       name = models.CharField(max_length=255)
       is_active = models.BooleanField(default=True)
       is_staff = models.BooleanField(default=False)

       objects = userManager()

       USERNAME_FIELD = "email"
