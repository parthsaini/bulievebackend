# apps/news/pagination.py
from rest_framework.pagination import PageNumberPagination

class NewsArticlePagination(PageNumberPagination):
    page_size = 20  # Default number of articles per page
    page_size_query_param = 'page_size'
    max_page_size = 100