from rest_framework.pagination import PageNumberPagination

from backend.settings import RECIPE_PAGE_SIZE


class RecipePagination(PageNumberPagination):
    """Кастомный класс пагинации."""
    page_size_query_param = 'limit'
    page_size = RECIPE_PAGE_SIZE
