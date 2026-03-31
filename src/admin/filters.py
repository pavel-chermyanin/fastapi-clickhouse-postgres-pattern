from sqladmin import ModelView

from src.modules.filters.models import Filter


class FilterAdmin(ModelView, model=Filter):
    """
    Администрирование фильтров.
    """

    column_list = [
        Filter.id,
        Filter.report_id,
        Filter.name,
    ]
    column_details_list = [
        Filter.id,
        Filter.report_id,
        Filter.name,
        Filter.config,
    ]
    column_searchable_list = [Filter.name]
    column_sortable_list = [Filter.id, Filter.report_id]
    icon = "fa-solid fa-filter"
    name = "Фильтр"
    plural_name = "Фильтры"
    category = "Контент"
