import json
import sys
from pathlib import Path

# Добавляем корень проекта в путь импорта, чтобы находить 'src'
sys.path.append(str(Path(__file__).parent.parent))

from src.db.session import Base


def export_metadata_to_mermaid():
    """
    Экспортирует метаданные моделей SQLAlchemy в формат Mermaid.js с поддержкой комментариев.
    Исключает ассоциативные таблицы из визуализации, превращая их в прямые связи M:N.
    """
    mermaid_lines = ["erDiagram"]
    tooltips = {}

    tables = Base.metadata.tables
    assoc_tables = {}
    regular_tables = {}

    print(f"Обнаружено таблиц: {list(tables.keys())}")

    # Разделяем таблицы на обычные и ассоциативные
    for table_name, table in tables.items():
        # Ассоциативная таблица: все колонки либо PK, либо FK, и нет одиночного PK 'id'
        is_assoc = (
            all(c.primary_key or c.foreign_keys for c in table.columns) and len(table.columns) >= 2
        )

        # Если в таблице есть колонка 'id', которая является единственным PK, это не ассоциативная таблица в нашем смысле
        if "id" in [c.name.lower() for c in table.columns]:
            is_assoc = False

        if is_assoc:
            print(f"Таблица {table_name} определена как ассоциативная")
            assoc_tables[table_name] = table
        else:
            regular_tables[table_name] = table

    # Сначала генерируем блоки для обычных таблиц
    for table_name, table in regular_tables.items():
        entity_name = table_name.upper()
        mermaid_lines.append(f"    {entity_name} {{")

        table_comment = getattr(table, "comment", None) or ""
        tooltips[entity_name] = f"<strong>{entity_name}</strong>{table_comment}"

        for column in table.columns:
            col_type = str(column.type).split("(")[0]
            col_name = column.name

            pk_fk = ""
            if column.primary_key:
                pk_fk = "PK"
            elif column.foreign_keys:
                pk_fk = "FK"

            mermaid_lines.append(f"        {col_type} {col_name} {pk_fk}")

            col_comment = column.comment or ""
            tooltips[f"{entity_name}-{col_name.upper()}"] = (
                f"<strong>{col_name} ({col_type})</strong>{col_comment}"
            )

        mermaid_lines.append("    }")

    # Обрабатываем прямые связи (1:N) из обычных таблиц
    for table_name, table in regular_tables.items():
        entity_name = table_name.upper()
        for fk in table.foreign_keys:
            target_table_name = fk.column.table.name
            if target_table_name in regular_tables:
                target_entity = target_table_name.upper()
                source_col = fk.parent.name
                target_col = fk.column.name
                # One-to-Many
                mermaid_lines.append(
                    f'    {target_entity} ||--o{{ {entity_name} : "{source_col}_to_{target_col}"'
                )

    # Обрабатываем ассоциативные таблицы (M:N)
    for table_name, table in assoc_tables.items():
        fks = list(table.foreign_keys)
        if len(fks) >= 2:
            # Берем уникальные таблицы, в которые ведут FK
            target_entities = sorted(list(set(fk.column.table.name.upper() for fk in fks)))
            if len(target_entities) >= 2:
                t1, t2 = target_entities[0], target_entities[1]
                # Many-to-Many link
                mermaid_lines.append(f'    {t1} }}|--|{{ {t2} : "{table_name.lower()}"')

    mermaid_code = "\n".join(mermaid_lines)

    data = {"mermaidSchema": mermaid_code, "dbTooltips": tooltips}

    output_path = Path(__file__).parent.parent / "schema_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Метаданные успешно экспортированы в {output_path.name}")


if __name__ == "__main__":
    export_metadata_to_mermaid()
