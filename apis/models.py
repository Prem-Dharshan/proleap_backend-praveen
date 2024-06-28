from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        # Set password using Django's built-in method
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, role=Role.ADMIN, **extra_fields)


class Role(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    USER = "USER", _("User")
    ORGANIZER = "ORGANIZER", _("Organizer")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    name = models.CharField(_('name'), max_length=30, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER)
    gender = models.CharField(max_length=10, blank=True, null=True)
    phoneNumber = models.PositiveBigIntegerField(null=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Batch(models.Model):
    name = models.CharField(null=False, max_length=48, blank=False)
    year = models.PositiveIntegerField(blank=False, null=False)

    start_time = models.DateTimeField(
        null=True, blank=True)    # TODO: Make null = False
    end_time = models.DateTimeField(null=True, blank=True)
    total_activities = models.IntegerField(default=0)

    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="organizing_batch",
        null=True)
    users = models.ManyToManyField(
        User,
        related_name="participating_batch",
        through="UserBatch")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['name', 'year']

    def __str__(self):
        return f"{self.name} {self.year}"


class Status(models.TextChoices):
    NOT_ATTEMPTED = "NOT_ATTEMPTED", "Not Attempted"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"


class UserBatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)

    completed_activities = models.IntegerField(default=0)
    # FIXME: Field Not necessary, redundant
    is_completed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_ATTEMPTED)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ['user', 'batch']

    def __str__(self):
        return f"B = {self.batch.id} U = {self.user.id}"


class Activity(models.Model):
    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=256, blank=True, null=True)

    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    total_cards = models.IntegerField(default=0, null=False)
    total_polling_cards = models.IntegerField(default=0, null=False)
    # TODO: Write a Trigger coz polling cards are created in runtime

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    users = models.ManyToManyField(
        "User",
        related_name="participating_activities",
        through="UserActivity")

    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        related_name="activities",
        null=True)
    sequence_no = models.IntegerField(default=1, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'batch',
                    'name',
                    'sequence_no'],
                name='unique_batch_name_sequence')]

    def __str__(self) -> str:
        return f"{self.batch} {self.name} {self.sequence_no}"


class UserActivity(models.Model):
    activity = models.ForeignKey(
        Activity, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    completed_cards = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_ATTEMPTED)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'activity',
                    'user'],
                name='unique_activity_user')]

    def str(self):
        return f"A = {self.activity.id} U = {self.user.id}"


class CardType(models.TextChoices):
    SURVEY_INPUT = "SURVEY_INPUT", _("Survey Input")
    SURVEY_DISPLAY = "SURVEY_DISPLAY", _("Survey Display")
    POLL = "POLL", _("Poll")


class Card(models.Model):
    name = models.CharField(max_length=128)
    desc = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(max_length=32, default=CardType.SURVEY_INPUT)
    total_questions = models.IntegerField(default=0)

    # Only for Polling
    to_be_shown = models.BooleanField(default=True)
    # Provides provision to schedule polling
    start_time = models.DateTimeField(null=False, blank=True)
    end_time = models.DateTimeField(null=False, blank=True)
    duration = models.DurationField(default=timedelta(minutes=1))

    activity = models.ForeignKey(
        Activity, on_delete=models.SET_NULL, null=True)
    sequence_no = models.IntegerField(null=False, default=0)

    users = models.ManyToManyField(
        User,
        through="UserCard",
        related_name="participating_cards")  # Use settings.AUTH_USER_MODEL

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'activity',
                    'sequence_no'],
                name='unique_activity_sequence_no')]

    def __str__(self) -> str:
        return f"{self.id}. {self.name}"


class UserCard(models.Model):
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    completed_questions = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_ATTEMPTED)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'card',
                    'user'],
                name='unique_card_user')]

    def str(self):
        return f"C = {self.card.id} U = {self.user.id}"


class QuestionType(models.TextChoices):
    SHORT_ANSWER = "SHORT_ANSWER", _("short_answer")
    PARAGRAPH = "PARAGRAPH", _("paragraph")
    NUMBER = "NUMBER", _("number")
    RADIO = "RADIO", _("radio")
    DATE = "DATE", _("date")
    FILE = "FILE", _("file")
    CHECKBOXES = "CHECKBOXES", _("checkboxes")
    URL = "URL", _("url")
    IMAGE = "IMAGE", _("image")
    TIME = "TIME", _("time")
    EMAIL = "EMAIL", _("email")


class Question(models.Model):
    text = models.CharField(max_length=512, null=False, blank=False)
    type = models.CharField(
        max_length=64,
        choices=QuestionType.choices,
        null=False,
        blank=False,
        default=QuestionType.SHORT_ANSWER)
    desc = models.CharField(max_length=256, null=True, blank=True)

    is_required = models.BooleanField(default=True)

    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    sequence_no = models.IntegerField(null=False, default=0)

    users = models.ManyToManyField(
        User,
        through="Answer",
        related_name="user_questions")  # Use settings.AUTH_USER_MODEL

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'card',
                    'sequence_no'],
                name='unique_card_sequence_no')]

    def __str__(self) -> str:
        return f"{self.id}. {self.text}"


class Option(models.Model):
    value = models.CharField(max_length=256, null=False, blank=True)
    sequence_no = models.IntegerField(null=False, default=0)

    question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        related_name="options")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'question',
                    'sequence_no'],
                name='unique_question_sequence_no')]

    def __str__(self) -> str:
        return f"{self.id}. {self.value}"


class Answer(models.Model):
    answer = models.CharField(max_length=500, blank=True, null=True)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="user_answers")
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True)
    option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question', 'option', 'answer'],
                name='unique_user_question_option_answer'
            )
        ]

    def __str__(self) -> str:
        if self.answer:
            return f"{self.id}. U = {self.user.id} Q = {
                self.question.id} A = {self.answer[:3]}.."
        else:
            return f"{
                self.id}. U = {
                self.user.id} Q = {
                self.question.id} O = {
                self.option.id}"
