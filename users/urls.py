from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Аутентификация
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),

    # Профиль
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),

    # Управление пользователями (только админ)
    path('admin/users/', views.UserListView.as_view(), name='user_list'),
    path('admin/user/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('admin/user/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('admin/user/<int:pk>/toggle-active/', views.UserToggleActiveView.as_view(), name='user_toggle_active'),
    path('admin/user/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    # AJAX endpoints для входа/регистрации по коду
    path('login/code/ajax/', views.LoginCodeAjaxView.as_view(), name='login_code_ajax'),
    path('register/code/ajax/', views.RegisterCodeAjaxView.as_view(), name='register_code_ajax'),
    path('verify/code/ajax/', views.VerifyCodeAjaxView.as_view(), name='verify_code_ajax'),
    path('resend/code/ajax/', views.ResendCodeAjaxView.as_view(), name='resend_code_ajax'),
]
