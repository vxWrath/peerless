from typing import Any, Dict, Iterable, List, Tuple


class Query:
    @staticmethod
    def insert(table: str, values: Dict[str, Any]) -> Tuple[str, List[Any]]:
        columns = list(values.keys())
        query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(f'${i+1}' for i in range(len(columns)))})
        """
        
        return query.strip(), list(values.values())

    @staticmethod
    def update(table: str, values: Dict[str, Any], where: Dict[str, Any]) -> Tuple[str, List[Any]]:
        set_expr = ', '.join(f"{key}=${i+1}" for i, key in enumerate(values))
        where_expr = ' AND '.join(f"{key}=${i+len(values)+1}" for i, key in enumerate(where))

        query = f"""
            UPDATE {table}
            SET {set_expr}
            WHERE {where_expr}
        """

        return query.strip(), list(values.values()) + list(where.values())

    @staticmethod
    def delete(table: str, where: Dict[str, Any]) -> Tuple[str, List[Any]]:
        where_expr = ' AND '.join(f"{key}=${i+1}" for i, key in enumerate(where))
        query = f"DELETE FROM {table} WHERE {where_expr}"

        return query, list(where.values())

    @staticmethod
    def select(table: str, columns: Iterable[str], where: Dict[str, Any]) -> Tuple[str, List[Any]]:
        where_expr = ' AND '.join(f"{key}=${i+1}" for i, key in enumerate(where))
        query = f"SELECT {', '.join(columns)} FROM {table} WHERE {where_expr}"

        return query, list(where.values())