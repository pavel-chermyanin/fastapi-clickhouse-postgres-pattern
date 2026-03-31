# ClickHouse Rules

## Usage
1. ClickHouse is used for analytical queries and large-scale data storage.
2. Use `clickhouse-connect` client for interacting with ClickHouse.
3. Keep analytical logic in `src/services/analytics.py` or separate services.
4. Repository layer for ClickHouse should be in `src/repositories/analytics/`.

## Data Management
- ClickHouse models/schemas should be distinct from SQLAlchemy models.
- Always use asynchronous execution when possible for analytics.
- Define table schemas clearly in ClickHouse DDL files if possible.
