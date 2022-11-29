from celery import shared_task

from core.song_serivice import SongService


@shared_task
def create_song_fingerprints(pk):
    SongService.run_main_work(pk)
