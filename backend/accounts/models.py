from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser, PermissionsMixin
# Create your models here.


class CustomUserManager(BaseUserManager):
    def create(self,email,password=None,**extra_field):
        if not email:
            raise ValueError('User must have an email addresss')
        email = self.normalize_email(email)

        user = self.model(email=email,**extra_field)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self,email,password):
        user = self.create(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'


    def __str__(self):
        return self.email


