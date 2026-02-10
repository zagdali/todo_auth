# app/tasks/celery_app.py
import os
from celery import Celery
from celery.schedules import crontab


# Устанавливаем переменную окружения для Django/Flask (не обязательно для FastAPI)
#os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

# Создаём экземпляр Celery
celery_app = Celery(
    'todolist',
    broker='redis://redis:6379/0',  # Redis как брокер сообщений
    backend='redis://redis:6379/0',  # Redis как бэкенд результатов
    include=['app.tasks.email_tasks']  # Импортируем задачи
)

# Настройки по умолчанию
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=10 * 60,  # 10 минут
    broker_connection_retry_on_startup=True,  # Включаем переподключение к брокеру
    broker_connection_max_retries=3, # Максимальное количество попыток переподключения
    broker_transport='redis', # ЯВНО указываем транспорт
    result_backend_transport='redis', # ЯВНО указываем транспорт
)

# Периодические задачи (если понадобятся)
celery_app.conf.beat_schedule = {
    # Пример: очистка старых токенов каждый день в 2:00
    # 'cleanup-expired-tokens': {
    #     'task': 'app.tasks.email_tasks.cleanup_expired_tokens',
    #     'schedule': crontab(hour=2, minute=0),
    # },
}