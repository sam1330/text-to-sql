import sqlparse

class SQLSanitizer:
    def __init__(self, forbidden_keywords=None):
        if forbidden_keywords is None:
            self.forbidden_keywords = {"DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"}
        else:
            self.forbidden_keywords = set(forbidden_keywords)

    def is_safe(self, sql_query: str) -> bool:
        """Check if the SQL query contains any forbidden keywords."""
        parsed = sqlparse.parse(sql_query)
        for statement in parsed:
            for token in statement.tokens:
                if token.ttype in sqlparse.tokens.Keyword and token.value.upper() in self.forbidden_keywords:
                    return False
                # Double check for DML in case of nested tokens
                if hasattr(token, 'tokens'):
                    if not self._check_nested(token):
                        return False
        return True

    def _check_nested(self, token_list) -> bool:
        for token in token_list.tokens:
            if token.ttype in sqlparse.tokens.Keyword and token.value.upper() in self.forbidden_keywords:
                return False
            if hasattr(token, 'tokens'):
                if not self._check_nested(token):
                    return False
        return True

    def sanitize(self, sql_query: str) -> str:
        """Add LIMIT 100 if not present."""
        if "LIMIT" not in sql_query.upper():
            sql_query = sql_query.strip().rstrip(';') + " LIMIT 100;"
        return sql_query
