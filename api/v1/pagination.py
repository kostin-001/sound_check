from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_query_param = "page"
    max_page_size = 100
    page_size = 25
