from django.urls import path
from . import views
from django.views.decorators.cache import cache_page, never_cache

app_name = 'catalog'

urlpatterns = [
    # Главная страница и каталог
    path('', views.ProductListView.as_view(), name='home'),
    path('catalog/', views.ProductListView.as_view(), name='product_list'),

    # Категории
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),

    # Товары
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/add-to-favorite/', never_cache(views.AddToFavoriteView.as_view()), name='add_to_favorite'),
    path('product/<int:pk>/remove-from-favorite/', never_cache(views.RemoveFromFavoriteView.as_view()),
         name='remove_from_favorite'),

    # CRUD для товаров (только для админа)
    path('product/create/', never_cache(views.ProductCreateView.as_view()), name='product_create'),
    path('product/<int:pk>/update/', never_cache(views.ProductUpdateView.as_view()), name='product_update'),
    path('product/<int:pk>/delete/', never_cache(views.ProductDeleteView.as_view()), name='product_delete'),

    # Избранное
    path('favorites/', never_cache(views.FavoriteListView.as_view()), name='favorites'),

    # Поиск
    path('search/', views.SearchResultsView.as_view(), name='search'),

    # Фильтрация по типу кожи
    path('skin-type/<slug:slug>/', views.SkinTypeProductsView.as_view(),
         name='skin_type_products'),
]
