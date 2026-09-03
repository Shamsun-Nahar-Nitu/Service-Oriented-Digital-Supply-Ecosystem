from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Default pagination for the whole API. Client can override page size
    with ?page_size=, capped at 100 so nobody can pull the whole DB in one go."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
