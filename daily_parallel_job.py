#Linux Bash: python daily_parallel_job.py & python launch.py && fg
#Her gün saat 00:00da timed_keys tablosunu denetle ve tarihi geçmiş olanları sil.
from database.connection import connection, cursor

#Saat 00:00ı bekleyen sistem...