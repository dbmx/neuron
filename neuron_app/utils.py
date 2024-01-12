import re
from datetime import datetime, timedelta
from flask import current_app
from jinja2 import Environment


def calculate_read_time(text):
    words_per_minute = 160  # Prilagodite broj reči po minutu prema vašim potrebama
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return round(minutes)


