"""
Morning notification scheduler.
Every day at the user's configured time, sends "Record your dream!" reminder.
"""
import asyncio
import logging
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import database

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


async def _send_morning_reminder(bot, telegram_id: int) -> None:
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=(
                "🌙 *Доброго ранку!*\n\n"
                "Ти щойно прокинувся. Запиши свій сон поки він ще свіжий!\n\n"
                "Просто надішли голосове повідомлення або текст 🎙"
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning(f"Failed to send morning reminder to {telegram_id}: {e}")


def _schedule_user(scheduler: AsyncIOScheduler, bot, user: dict) -> None:
    telegram_id = user["telegram_id"]
    notification_time = user["notification_time"]  # e.g. "08:00:00"
    timezone = user.get("timezone", "Europe/Kyiv")

    # parse hour/minute from time string
    try:
        t = datetime.strptime(notification_time, "%H:%M:%S")
    except ValueError:
        t = datetime.strptime(notification_time, "%H:%M")

    job_id = f"morning_{telegram_id}"

    # remove old job if exists
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        _send_morning_reminder,
        trigger=CronTrigger(
            hour=t.hour,
            minute=t.minute,
            timezone=pytz.timezone(timezone),
        ),
        args=[bot, telegram_id],
        id=job_id,
        replace_existing=True,
    )
    logger.info(f"Scheduled morning reminder for user {telegram_id} at {t.hour:02d}:{t.minute:02d} {timezone}")


async def setup_scheduler(bot) -> AsyncIOScheduler:
    global _scheduler
    _scheduler = AsyncIOScheduler()

    try:
        users = await database.get_users_with_notifications()
        for user in users:
            _schedule_user(_scheduler, bot, user)
        logger.info(f"Scheduler started with {len(users)} user(s) scheduled")
    except Exception as e:
        logger.warning(f"Scheduler: could not load users from DB at startup: {e}. Starting empty.")

    _scheduler.start()
    return _scheduler


def reschedule_user(bot, user: dict) -> None:
    """Call this after a user updates their notification settings."""
    if _scheduler:
        _schedule_user(_scheduler, bot, user)


def cancel_user(telegram_id: int) -> None:
    """Remove morning reminder for a user."""
    if _scheduler:
        job_id = f"morning_{telegram_id}"
        if _scheduler.get_job(job_id):
            _scheduler.remove_job(job_id)
