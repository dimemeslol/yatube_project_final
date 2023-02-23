from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.core.handlers.wsgi import WSGIRequest


CONST_SHOWED_POST = 10


def pagination(request: WSGIRequest, post_list: QuerySet) -> Page:
    """Функция добавления пагинации на страницу"""
    paginator: Paginator = Paginator(post_list, CONST_SHOWED_POST)
    page_number: str = request.GET.get('page')
    page_obj: Page = paginator.get_page(page_number)
    return page_obj
