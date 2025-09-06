from flask import request

def get_pagination_params(default_per_page=20, max_per_page=100):
    """Extract and validate pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', default_per_page, type=int), max_per_page)
    return page, per_page

def format_pagination_response(paginated_query, items_key='items'):
    """Format paginated query results with metadata"""
    return {
        items_key: [item for item in paginated_query.items],
        'pagination': {
            'page': paginated_query.page,
            'per_page': paginated_query.per_page,
            'total': paginated_query.total,
            'pages': paginated_query.pages,
            'has_next': paginated_query.has_next,
            'has_prev': paginated_query.has_prev
        }
    }