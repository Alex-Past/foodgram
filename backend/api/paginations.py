from rest_framework.pagination import PageNumberPagination

from backend.settings import RECIPE_PAGE_SIZE


class RecipePagination(PageNumberPagination):
    """Класс пагинации для рецептов."""
    page_size_query_param = 'limit'
    page_size = RECIPE_PAGE_SIZE
