from django.urls import path

from timers.views import (
    TimerView,
    SessionStateJson,
    ControlView,
    APIResetView,
    APIPauseView,
    APIStartView,
    CreateSessionView,
    UpdateSessionView,
    UpdateSessionTimeView,
    HomeView,
    SelectSessionView,
    InviteAdminView,
    JoinAdminView,
    TableRangesView,
    CreateTableView,
    UpdateTableView,
    DeleteTableView,
    DeleteAllTablesView,
    CreateTableRangeView,
    UpdateTableRangeView,
    DeleteTableRangeView,
    MySessionsView,
    SelectPersonalSessionView,
    SelectPersonalSessionTableView,
    PersonalView,
)

app_name = "timers"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("create/", CreateSessionView.as_view(), name="new_session"),
    path("edit/<slug:slug>/", UpdateSessionView.as_view(), name="edit_session"),
    path("control/", MySessionsView.as_view(), name="my_sessions"),
    path("control/<slug:slug>/", ControlView.as_view(), name="control_session"),
    path(
        "control/<slug:slug>/tables/", TableRangesView.as_view(), name="table_ranges"
    ),
    path(
        "control/<slug:slug>/tables/new/", CreateTableRangeView.as_view(), name="create_table_range"
    ),
    path(
        "control/<slug:slug>/tables/<int:pk>/",
        UpdateTableRangeView.as_view(),
        name="update_table_range",
    ),
    path(
        "control/<slug:slug>/tables/<int:pk>/delete/",
        DeleteTableRangeView.as_view(),
        name="delete_table_range",
    ),
    path(
        "control/<slug:slug>/extension/", CreateTableView.as_view(), name="create_table"
    ),
    path(
        "control/<slug:slug>/extension/<int:pk>/",
        UpdateTableView.as_view(),
        name="update_table",
    ),
    path(
        "control/<slug:slug>/extension/delete-all/",
        DeleteAllTablesView.as_view(),
        name="delete_all_tables",
    ),
    path(
        "control/<slug:slug>/extension/<int:pk>/delete/",
        DeleteTableView.as_view(),
        name="delete_table",
    ),
    path("invite/<slug:slug>/", InviteAdminView.as_view(), name="invite_control"),
    path("join/", JoinAdminView.as_view(), name="join_control"),
    path("time/<slug:slug>/", UpdateSessionTimeView.as_view(), name="edit_time"),
    path("view/", SelectSessionView.as_view(), name="view_session_select"),
    path("personal/", SelectPersonalSessionView.as_view(), name="view_table_select"),
    path("personal/<slug:slug>/", SelectPersonalSessionTableView.as_view(), name="view_table_table"),
    path("personal/<slug:slug>/<int:table>/", PersonalView.as_view(), name="view_table"),
    path("view/<slug:slug>/", TimerView.as_view(), name="view_session"),
    # API endpoints
    path("api/session_state/<slug:slug>", SessionStateJson.as_view()),
    path("api/play/<slug:slug>", APIStartView.as_view()),
    path("api/pause/<slug:slug>", APIPauseView.as_view()),
    path("api/reset/<slug:slug>", APIResetView.as_view()),
]
