from rest_framework.pagination import PageNumberPagination

class MyPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'p'
    page_size_query_param = 'records'
    max_page_size = 100
    last_page_strings = ['end']  # Assign a list of strings here
    allow_empty_first_page = True

    