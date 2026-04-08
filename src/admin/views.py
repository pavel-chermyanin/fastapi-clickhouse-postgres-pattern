from sqladmin import ModelView

from src.modules.users import User


class UserAdmin(ModelView, model=User):
    """
    Отображение пользователей в административной панели.
    """

    column_list = [User.id, User.email, User.full_name, User.is_active, User.created_at]
    column_searchable_list = [User.email, User.full_name]
    column_sortable_list = [User.id, User.created_at]
    icon = "fa-solid fa-user"
    name = "Пользователь"
    plural_name = "Пользователи"
    category = "Аккаунты"
