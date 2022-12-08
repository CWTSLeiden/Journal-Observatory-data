from utils.query import get_single_result


def pad_count(db, query="{?pad a ppo:PAD}") -> int:
    query = f"select (count(*) as ?count) where {query}"
    total = get_single_result(db.query(query))
    return int(total or 0)
