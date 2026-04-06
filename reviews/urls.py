from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Создание, редактирование, удаление отзыва
    path('product/<int:product_pk>/create/', views.ReviewCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='delete'),

    # Модерация отзывов (только для модератора и админа)
    path('moderation/', views.ReviewModerationListView.as_view(), name='moderation_list'),
    path('<int:pk>/approve/', views.ReviewApproveView.as_view(), name='approve'),
    path('<int:pk>/reject/', views.ReviewRejectView.as_view(), name='reject'),

    # Лайки на отзывы
    path('<int:pk>/like/', views.ReviewLikeView.as_view(), name='like'),

    # Список отзывов пользователя
    path('my-reviews/', views.UserReviewsView.as_view(), name='my_reviews'),

    # Отзывы на товар
    path('product/<int:product_pk>/all/', views.ProductReviewsView.as_view(), name='product_reviews'),
]