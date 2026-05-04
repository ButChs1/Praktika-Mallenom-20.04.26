def row_matches_query(query, row_data):

    query = query.strip().lower()
    if not query:
        return True

    row_content_lower = [cell.lower() for cell in row_data]

    if "/" in query:
        sub_queries = [q.strip(' "') for q in query.split("/") if q.strip()]
        
        for sq in sub_queries:
            if not any(sq in cell for cell in row_content_lower):
                return False
        return True
        
    else:
        is_exact = query.startswith('"') and query.endswith('"') and len(query) > 1
        search_text = query[1:-1] if is_exact else query
        
        if is_exact:
            return any(search_text == cell for cell in row_content_lower)
        else:
            return any(search_text in cell for cell in row_content_lower)