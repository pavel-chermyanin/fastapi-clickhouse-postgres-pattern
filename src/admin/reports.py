from sqladmin import ModelView

from src.modules.reports import Report


class ReportAdmin(ModelView, model=Report):
    """
    Администрирование отчетов.
    """

    column_list = [
        Report.id,
        Report.title,
        Report.created_at,
    ]
    column_details_list = [
        Report.id,
        Report.title,
        Report.content,
        Report.created_at,
    ]
    column_searchable_list = [Report.title]
    column_sortable_list = [Report.id, Report.created_at]
    icon = "fa-solid fa-file-lines"
    name = "Отчет"
    plural_name = "Отчеты"
    category = "Контент"
