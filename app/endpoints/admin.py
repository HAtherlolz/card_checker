from sqladmin import ModelView

from app.models import Profile


class ProfileAdmin(ModelView, model=Profile):
    name = "Profile"
    name_plural = "Profiles"
    icon = "fa-solid fa-person"
    column_list = [Profile.id, Profile.email]
    column_searchable_list = [Profile.id, Profile.email]


admins_models = [
    ProfileAdmin
]
