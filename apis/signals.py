from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
import logging

from .models import Answer, Question, Card, Activity, UserCard, UserBatch, UserActivity, Status

logger = logging.getLogger('apis')

@receiver(post_save, sender=Answer)
def update_user_progress(sender, instance, created, **kwargs):
    try:
        question = instance.question
        card = question.card
        user = instance.user

        # Fetch all questions in the card
        questions_in_card = Question.objects.filter(card=card)
        
        # Fetch all required questions in the card
        tot_rqd_questions = questions_in_card.filter(is_required=True)
        required_question_ids = tot_rqd_questions.values_list('id', flat=True)

        # Fetch all unique answers for the user and required questions in the card
        user_answers = Answer.objects.filter(
            user=user, question__in=required_question_ids
        ).values('question').distinct()
        completed_questions_count = user_answers.count()

        logger.info(f"User completed_questions_count: {completed_questions_count}")

        # Update the UserCard instance
        user_card, created = UserCard.objects.get_or_create(user=user, card=card)
        user_card.completed_questions = completed_questions_count

        # Update the status in UserCard
        if completed_questions_count == 0:
            user_card.status = Status.NOT_ATTEMPTED
        elif completed_questions_count < tot_rqd_questions.count():
            user_card.status = Status.IN_PROGRESS
        else:
            user_card.status = Status.COMPLETED

        user_card.save(update_fields=['completed_questions', 'status'])
        logger.info(f"UserCard updated: {user_card.status}, {user_card.completed_questions}")

        # Fetch all cards for the activity of the current card
        cards_in_activity = Card.objects.filter(activity=card.activity)
        card_ids = cards_in_activity.values_list('id', flat=True)
        user_cards_in_activity = UserCard.objects.filter(user=user, card__in=card_ids)
        completed_cards_count = user_cards_in_activity.filter(status=Status.COMPLETED).count()

        # Update the UserActivity instance
        user_activity, created = UserActivity.objects.get_or_create(user=user, activity=card.activity)
        user_activity.completed_cards = completed_cards_count

        if completed_cards_count == 0:
            user_activity.status = Status.NOT_ATTEMPTED
        elif completed_cards_count < card.activity.total_cards:
            user_activity.status = Status.IN_PROGRESS
        else:
            user_activity.status = Status.COMPLETED

        user_activity.save(update_fields=['completed_cards', 'status'])
        logger.info(f"UserActivity updated: {user_activity.status}, {user_activity.completed_cards}")

        # Fetch all activities for the batch of the current activity
        activities_in_batch = Activity.objects.filter(batch=card.activity.batch)
        activity_ids = activities_in_batch.values_list('id', flat=True)
        user_activities_in_batch = UserActivity.objects.filter(user=user, activity__in=activity_ids)
        completed_activities_count = user_activities_in_batch.filter(status=Status.COMPLETED).count()

        # Update the UserBatch instance
        user_batch, created = UserBatch.objects.get_or_create(user=user, batch=card.activity.batch)
        user_batch.completed_activities = completed_activities_count

        if completed_activities_count == 0:
            user_batch.status = Status.NOT_ATTEMPTED
        elif completed_activities_count < card.activity.batch.total_activities:
            user_batch.status = Status.IN_PROGRESS
        else:
            user_batch.status = Status.COMPLETED
            user_batch.is_completed = True

        user_batch.save(update_fields=['completed_activities', 'status', 'is_completed'])
        logger.info(f"UserBatch updated: {user_batch.status}, {user_batch.completed_activities}")

    except UserCard.DoesNotExist:
        logger.error(f"UserCard instance for user {user.id} and card {card.id} does not exist.")
    except UserActivity.DoesNotExist:
        logger.error(f"UserActivity instance for user {user.id} and activity {card.activity.id} does not exist.")
    except UserBatch.DoesNotExist:
        logger.error(f"UserBatch instance for user {user.id} and batch {card.activity.batch.id} does not exist.")
    except IntegrityError as e:
        logger.error(f"IntegrityError occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
