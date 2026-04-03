import json
import re
import sys
from pathlib import Path

# Добавляем корень проекта в путь импорта, чтобы находить 'src'
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.db.mariadb.session import MariaDBBase, discover_and_register_mariadb_models  # noqa: E402
from src.db.postgres.session import (  # noqa: E402
    PostgresBase,
    discover_and_register_postgres_models,
)


def get_doc_comments_from_file(file_path):
    """
    Извлекает комментарии вида # @doc: из файла.
    Возвращает словарь {переменная/связь: комментарий}.
    """
    comments = {}
    if not file_path.exists():
        return comments

    try:
        content = file_path.read_text(encoding="utf-8")
        # Ищем паттерн: # @doc: текст \n переменная = relationship(...)
        pattern = r"#\s*@doc:\s*(.*?)\n\s*(\w+)\s*=\s*relationship"
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            comment_text = match.group(1).strip()
            var_name = match.group(2).strip()
            comments[var_name] = comment_text
    except Exception as e:
        print(f"Ошибка при парсинге {file_path}: {e}")

    return comments


def generate_mermaid_for_metadata(metadata, prefix=""):
    """Генерирует Mermaid-код и тултипы для переданного объекта MetaData."""
    mermaid_lines = []
    tooltips = {}
    edge_tooltips = {}

    tables = metadata.tables
    assoc_tables = {}
    regular_tables = {}

    # Разделяем таблицы на обычные и ассоциативные
    for table_name, table in tables.items():
        is_assoc = (
            all(c.primary_key or c.foreign_keys for c in table.columns) and len(table.columns) >= 2
        )
        if "id" in [c.name.lower() for c in table.columns]:
            is_assoc = False

        if is_assoc:
            assoc_tables[table_name] = table
        else:
            regular_tables[table_name] = table

    # Блоки для обычных таблиц
    for table_name, table in regular_tables.items():
        entity_name = table_name.upper()
        mermaid_lines.append(f"    {entity_name} {{")

        table_comment = getattr(table, "comment", None) or ""
        tooltips[entity_name] = f"<strong>{entity_name}</strong>{table_comment}"

        for column in table.columns:
            col_type = str(column.type).split("(")[0]
            col_name = column.name
            pk_fk = "PK" if column.primary_key else ("FK" if column.foreign_keys else "")
            mermaid_lines.append(f"        {col_type} {col_name} {pk_fk}")
            col_comment = column.comment or ""
            tooltips[f"{entity_name}-{col_name.upper()}"] = (
                f"<strong>{col_name} ({col_type})</strong>{col_comment}"
            )
        mermaid_lines.append("    }")

    # Прямые связи (1:N)
    for table_name, table in regular_tables.items():
        entity_name = table_name.upper()
        for fk in table.foreign_keys:
            target_table_name = fk.column.table.name
            if target_table_name in regular_tables:
                target_entity = target_table_name.upper()
                label = f"{fk.parent.name}_to_{fk.column.name}"
                mermaid_lines.append(f'    {target_entity} ||--o{{ {entity_name} : "{label}"')

    # Ассоциативные таблицы (M:N)
    for table_name, table in assoc_tables.items():
        fks = list(table.foreign_keys)
        if len(fks) >= 2:
            target_entities = sorted(list(set(fk.column.table.name.upper() for fk in fks)))
            if len(target_entities) >= 2:
                t1, t2 = target_entities[0], target_entities[1]
                mermaid_lines.append(f'    {t1} }}|--|{{ {t2} : "{table_name.lower()}"')

    return "\n".join(mermaid_lines), tooltips, edge_tooltips


def export_metadata_to_mermaid():
    """
    Экспортирует метаданные моделей PostgreSQL и MariaDB раздельно в формат Mermaid.js.
    """
    project_root = Path(__file__).parent.parent

    # 1. Регистрация моделей PostgreSQL
    discover_and_register_postgres_models()

    # 2. Регистрация моделей MariaDB
    discover_and_register_mariadb_models()

    # Генерируем схему для Postgres
    pg_mermaid, pg_tooltips, pg_edges = generate_mermaid_for_metadata(PostgresBase.metadata)
    pg_schema = "erDiagram\n" + pg_mermaid

    # Генерируем схему для MariaDB
    ma_mermaid, ma_tooltips, ma_edges = generate_mermaid_for_metadata(MariaDBBase.metadata)
    ma_schema = "erDiagram\n" + ma_mermaid

    data = {
        "postgres": {"mermaidSchema": pg_schema, "tooltips": pg_tooltips, "edgeTooltips": pg_edges},
        "mariadb": {"mermaidSchema": ma_schema, "tooltips": ma_tooltips, "edgeTooltips": ma_edges},
    }

    output_path = project_root / "schema_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Метаданные успешно разделены и экспортированы в {output_path.name}")


if __name__ == "__main__":
    export_metadata_to_mermaid()
