from datetime import datetime


def year(request):
    now = datetime.today()
    now_year = now.year
    """Добавляет переменную с текущим годом."""
    return {
        'now_year': now_year
    }
