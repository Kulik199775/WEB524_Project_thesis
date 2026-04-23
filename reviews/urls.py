from django.urls import path
from . import views
from django.views.decorators.cache import never_cache

app_name = 'reviews'

urlpatterns = [
    # Создание, редактирование, удаление отзыва
    path('product/<int:product_pk>/create/', never_cache(views.ReviewCreateView.as_view()), name='create'),
    path('<int:pk>/edit/', never_cache(views.ReviewUpdateView.as_view()), name='edit'),
    path('<int:pk>/delete/', never_cache(views.ReviewDeleteView.as_view()), name='delete'),

    # Модерация отзывов (только для модератора и админа)
    path('moderation/', never_cache(views.ReviewModerationListView.as_view()), name='moderation_list'),
    path('<int:pk>/approve/', never_cache(views.ReviewApproveView.as_view()), name='approve'),
    path('<int:pk>/reject/', never_cache(views.ReviewRejectView.as_view()), name='reject'),

    # Лайки на отзывы
    path('<int:pk>/like/', never_cache(views.ReviewLikeView.as_view()), name='like'),

    # Список отзывов пользователя
    path('my-reviews/', never_cache(views.UserReviewsView.as_view()), name='my_reviews'),

    # Отзывы на товар
    path('product/<int:product_pk>/all/', views.ProductReviewsView.as_view(),
         name='product_reviews'),
]
