from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import AbstractUser as _AbstractUser
from django.contrib.auth.models import Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractUser(_AbstractUser):

    class Meta:
        abstract = True

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="+",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="+",
        related_query_name="user",
    )


class UserWithUniqueEmail(AbstractUser):
    email = models.EmailField(
        verbose_name=_("email address"),
        unique=True,
        blank=True,
    )


class UserType(models.Model):
    name = models.CharField(max_length=255)


class UserWithUserType(AbstractUser):
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)


class SimpleEmailBasedUser(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(
        verbose_name=_("email address"),
        unique=True,
        blank=True,
    )


class Channel(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)


class UserWithChannel(AbstractUser):
    primary_channel = models.OneToOneField(
        Channel,
        on_delete=models.PROTECT,
        related_name="owner",
    )
