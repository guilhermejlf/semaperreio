from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import prever_gasto, gastos, gasto_detail, dashboard, receitas, receita_detail, exportar_csv, exportar_xlsx, listar_metas, criar_meta, atualizar_meta, deletar_meta
from .views_auth import RegisterView, LoginView, RefreshView, UserView
from .views_family import FamilyViewSet

router = DefaultRouter()
router.register('family', FamilyViewSet, basename='family')

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="refresh"),
    path("auth/user/", UserView.as_view(), name="user"),
    path("prever/", prever_gasto, name="prever_gasto"),
    path("export/csv/", exportar_csv, name="exportar_csv"),
    path("export/xlsx/", exportar_xlsx, name="exportar_xlsx"),
    path("gastos/", gastos, name="gastos_list"),
    path("gastos/<int:pk>/", gasto_detail, name="gasto_detail"),
    path("dashboard/", dashboard, name="dashboard"),
    path("receitas/", receitas, name="receitas_list"),
    path("receitas/<int:pk>/", receita_detail, name="receita_detail"),
    path("metas/", listar_metas, name="listar_metas"),
    path("metas/criar/", criar_meta, name="criar_meta"),
    path("metas/<int:pk>/", atualizar_meta, name="atualizar_meta"),
    path("metas/<int:pk>/deletar/", deletar_meta, name="deletar_meta"),
    path("", include(router.urls)),
]