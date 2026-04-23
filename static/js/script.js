document.addEventListener('DOMContentLoaded', function () {
    // ========== Переключение темы ==========
    const themeToggle = document.getElementById('themeToggle');

    if (themeToggle) {
        const themeIcon = themeToggle.querySelector('i');

        // Проверяем сохраненную тему в localStorage
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            if (themeIcon) {
                themeIcon.classList.remove('bi-moon');
                themeIcon.classList.add('bi-sun');
            }
        }

        // Обработчик кнопки
        themeToggle.addEventListener('click', function () {
            document.body.classList.toggle('dark-theme');

            if (themeIcon) {
                if (document.body.classList.contains('dark-theme')) {
                    themeIcon.classList.remove('bi-moon');
                    themeIcon.classList.add('bi-sun');
                    localStorage.setItem('theme', 'dark');
                } else {
                    themeIcon.classList.remove('bi-sun');
                    themeIcon.classList.add('bi-moon');
                    localStorage.setItem('theme', 'light');
                }
            }
        });
    }

    // ========== Кнопка "Наверх" ==========
    const backToTopButton = document.getElementById('backToTop');

    if (backToTopButton) {
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 60) {
                backToTopButton.classList.add('visible');
            } else {
                backToTopButton.classList.remove('visible');
            }
        });

        backToTopButton.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});

function addToCart(productId, buttonElement, quantity = 1) {
    const originalText = buttonElement.innerHTML;
    const originalClass = buttonElement.className;

    buttonElement.innerHTML = '<i class="bi bi-check-lg"></i> Добавлено!';
    buttonElement.classList.add('btn-success');
    buttonElement.disabled = true;

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({quantity: quantity})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Находим бейдж корзины
                let cartBadge = document.querySelector('.cart-badge-absolute');

                // Если бейджа нет, создаем его
                if (!cartBadge) {
                    const cartLink = document.querySelector('.cart-item .nav-link');
                    if (cartLink) {
                        cartBadge = document.createElement('span');
                        cartBadge.className = 'cart-badge-absolute';
                        cartLink.appendChild(cartBadge);
                    }
                }

                // Обновляем количество
                if (cartBadge) {
                    cartBadge.textContent = data.cart_total;
                    cartBadge.style.display = 'inline-flex';
                    cartBadge.style.animation = 'none';
                    cartBadge.offsetHeight;
                    cartBadge.style.animation = 'bounce 0.3s ease';
                }

                // Если количество стало 0, скрываем бейдж
                if (data.cart_total === 0 && cartBadge) {
                    cartBadge.style.display = 'none';
                }

                showNotification('Товар добавлен в корзину!', 'success');

                setTimeout(() => {
                    buttonElement.innerHTML = originalText;
                    buttonElement.className = originalClass;
                    buttonElement.disabled = false;
                }, 1500);
            } else {
                buttonElement.innerHTML = originalText;
                buttonElement.className = originalClass;
                buttonElement.disabled = false;
                showNotification(data.error || 'Ошибка при добавлении', 'error');
            }
        })
        .catch(error => {
            buttonElement.innerHTML = originalText;
            buttonElement.className = originalClass;
            buttonElement.disabled = false;
            showNotification('Ошибка при добавлении товара', 'error');
        });
}

function showNotification(message, type = 'success') {
    // Создаем контейнер если его нет
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        container.style.cssText = `
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    z-index: 1050;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                `;
        document.body.appendChild(container);
    }

    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
                background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#dc3545' : type === 'warning' ? '#f39c12' : '#17a2b8'};
                color: white;
                padding: 12px 20px;
                border-radius: 12px;
                min-width: 280px;
                max-width: 350px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                gap: 12px;
                animation: slideInRight 0.3s ease;
                cursor: pointer;
                font-size: 14px;
            `;

    // Иконка в зависимости от типа
    let icon = 'check-circle-fill';
    if (type === 'error') icon = 'exclamation-triangle-fill';
    if (type === 'warning') icon = 'exclamation-triangle-fill';
    if (type === 'info') icon = 'info-circle-fill';

    notification.innerHTML = `
                <i class="bi bi-${icon}" style="font-size: 1.2rem;"></i>
                <span style="flex: 1;">${message}</span>
                <button class="btn-close btn-close-white" style="font-size: 0.7rem;"></button>
            `;

    container.appendChild(notification);

    // Автоматическое исчезновение через 3 секунды
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);

    // Закрытие по клику на крестик
    notification.querySelector('.btn-close').addEventListener('click', () => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });

    // Закрытие по клику на само уведомление
    notification.addEventListener('click', (e) => {
        if (!e.target.classList.contains('btn-close')) {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    });
}


// Добавление в избранное
function addToFavorite(buttonElement, url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),  // ← Исправлено
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                buttonElement.classList.add('active');
                buttonElement.innerHTML = '<i class="bi bi-heart-fill"></i>';
                showNotification(data.message, 'success');
            } else {
                showNotification(data.message, 'warning');
            }
        })
        .catch(error => {
            showNotification('Ошибка при добавлении в избранное', 'error');
        });
}

// Удаление из избранного
function removeFromFavorite(buttonElement, url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),  // ← Исправлено
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                buttonElement.classList.remove('active');
                buttonElement.innerHTML = '<i class="bi bi-heart"></i>';
                showNotification(data.message, 'info');
            } else {
                showNotification(data.message, 'warning');
            }
        })
        .catch(error => {
            showNotification('Ошибка при удалении из избранного', 'error');
        });
}

// Преобразуем Django messages в уведомления
document.addEventListener('DOMContentLoaded', function () {
    // Обрабатываем существующие сообщения от Django
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        const text = message.querySelector('.alert-message')?.innerText || message.innerText;
        const type = message.classList.contains('alert-success') ? 'success' :
            message.classList.contains('alert-danger') ? 'error' :
                message.classList.contains('alert-warning') ? 'warning' : 'info';
        showNotification(text, type);
        message.remove(); // Удаляем оригинальное сообщение
    });
});

// Переключение между модальными окнами
document.addEventListener('DOMContentLoaded', function () {
    // Переключение на регистрацию
    const switchToRegister = document.getElementById('switchToRegister');
    if (switchToRegister) {
        switchToRegister.addEventListener('click', function (e) {
            e.preventDefault();
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            loginModal.hide();
            setTimeout(() => {
                const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
                registerModal.show();
            }, 300);
        });
    }

    // Переключение на вход
    const switchToLogin = document.getElementById('switchToLogin');
    if (switchToLogin) {
        switchToLogin.addEventListener('click', function (e) {
            e.preventDefault();
            const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            registerModal.hide();
            setTimeout(() => {
                const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            }, 300);
        });
    }
});

// ========== ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ CSRF ТОКЕНА ==========
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ========== Вход по коду ==========
let currentCodeEmail = '';

function showCodeAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    const container = document.getElementById('codeAlert');
    if (container) {
        container.innerHTML = '';
        container.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Отправка email для получения кода входа
document.getElementById('loginCodeEmailForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const email = document.getElementById('code_email').value;
    const submitBtn = document.getElementById('sendCodeBtn');
    const originalText = submitBtn.innerHTML;

    if (!email) {
        showCodeAlert('Введите email', 'danger');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Отправка...';

    try {
        const response = await fetch('/users/login/code/ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({email: email})
        });

        const data = await response.json();

        if (data.success) {
            currentCodeEmail = email;
            document.getElementById('verifyEmailInfo').innerHTML = `<i class="bi bi-info-circle"></i> Код отправлен на <strong>${email}</strong>`;
            document.getElementById('stepEmail').style.display = 'none';
            document.getElementById('stepCode').style.display = 'block';
            showCodeAlert('Код отправлен на ваш email', 'success');
        } else {
            if (data.redirect_to) {
                showCodeAlert(data.message, 'warning');
                setTimeout(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('loginCodeModal'));
                    modal.hide();
                    window.location.href = data.redirect_to;
                }, 2000);
            } else {
                showCodeAlert(data.message || 'Ошибка отправки кода', 'danger');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showCodeAlert('Ошибка соединения. Попробуйте позже.', 'danger');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
});

// Подтверждение кода входа
document.getElementById('verifyCodeForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const code = document.getElementById('modal_code').value;
    const verifyBtn = document.getElementById('verifyBtn');
    const originalText = verifyBtn.innerHTML;

    if (!code || code.length !== 6) {
        showCodeAlert('Введите 6-значный код', 'danger');
        return;
    }

    verifyBtn.disabled = true;
    verifyBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Проверка...';

    try {
        const response = await fetch('/users/verify/code/ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({email: currentCodeEmail, code: code, action: 'login'})
        });

        const data = await response.json();

        if (data.success) {
            showCodeAlert('Успешный вход! Перенаправление...', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('loginCodeModal'));
            modal.hide();
            setTimeout(() => {
                window.location.href = data.redirect_url || '/';
            }, 1000);
        } else {
            showCodeAlert(data.message || 'Неверный код', 'danger');
            document.getElementById('modal_code').value = '';
            document.getElementById('modal_code').focus();
        }
    } catch (error) {
        console.error('Error:', error);
        showCodeAlert('Ошибка соединения. Попробуйте позже.', 'danger');
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.innerHTML = originalText;
    }
});

// Повторная отправка кода входа
document.getElementById('resendCodeBtn')?.addEventListener('click', async function () {
    if (!currentCodeEmail) {
        showCodeAlert('Email не найден. Попробуйте снова.', 'danger');
        return;
    }

    this.disabled = true;
    this.innerHTML = '<i class="bi bi-hourglass-split"></i> Отправка...';

    try {
        const response = await fetch('/users/resend/code/ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({email: currentCodeEmail, action: 'login'})
        });

        const data = await response.json();

        if (data.success) {
            showCodeAlert('Новый код отправлен на ваш email', 'success');
        } else {
            showCodeAlert(data.message || 'Ошибка отправки', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showCodeAlert('Ошибка соединения', 'danger');
    } finally {
        this.disabled = false;
        this.innerHTML = '<i class="bi bi-arrow-repeat"></i> Отправить код повторно';
    }
});

// Сброс формы при закрытии модального окна входа по коду
document.getElementById('loginCodeModal')?.addEventListener('hidden.bs.modal', function () {
    document.getElementById('code_email').value = '';
    document.getElementById('modal_code').value = '';
    document.getElementById('codeAlert').innerHTML = '';
    currentCodeEmail = '';
    document.getElementById('stepEmail').style.display = 'block';
    document.getElementById('stepCode').style.display = 'none';
});

// ========== РЕГИСТРАЦИЯ ПО КОДУ ==========
let currentRegEmail = '';
let currentRegFirstName = '';
let currentRegLastName = '';

function showRegCodeAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    const container = document.getElementById('regCodeAlert');
    if (container) {
        container.innerHTML = '';
        container.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Отправка email для регистрации
document.getElementById('registerCodeEmailForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const email = document.getElementById('reg_email').value;
    const firstName = document.getElementById('reg_firstname').value;
    const lastName = document.getElementById('reg_lastname').value;
    const submitBtn = document.getElementById('sendRegCodeBtn');
    const originalText = submitBtn.innerHTML;

    if (!email) {
        showRegCodeAlert('Введите email', 'danger');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Отправка...';

    try {
        const response = await fetch('/users/register/code/ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                email: email,
                first_name: firstName,
                last_name: lastName
            })
        });

        const data = await response.json();

        if (data.success) {
            currentRegEmail = email;
            currentRegFirstName = firstName;
            currentRegLastName = lastName;

            document.getElementById('regVerifyEmailInfo').innerHTML = `<i class="bi bi-info-circle"></i> Код отправлен на <strong>${email}</strong>`;
            document.getElementById('regStepEmail').style.display = 'none';
            document.getElementById('regStepCode').style.display = 'block';
            showRegCodeAlert('Код отправлен на ваш email', 'success');
        } else {
            if (data.redirect_to) {
                showRegCodeAlert(data.message, 'warning');
                setTimeout(() => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('registerCodeModal'));
                    modal.hide();
                    window.location.href = data.redirect_to;
                }, 2000);
            } else {
                showRegCodeAlert(data.message, 'danger');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showRegCodeAlert('Ошибка соединения. Попробуйте позже.', 'danger');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
});

// Подтверждение кода регистрации
document.getElementById('regVerifyCodeForm')?.addEventListener('submit', async function (e) {
    e.preventDefault();

    const code = document.getElementById('reg_modal_code').value;
    const verifyBtn = document.getElementById('regVerifyBtn');
    const originalText = verifyBtn.innerHTML;

    if (!code || code.length !== 6) {
        showRegCodeAlert('Введите 6-значный код', 'danger');
        return;
    }

    verifyBtn.disabled = true;
    verifyBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Проверка...';

    try {
        const response = await fetch('/users/verify/code/ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                email: currentRegEmail,
                code: code,
                action: 'register'
            })
        });

        const data = await response.json();

        if (data.success) {
            showRegCodeAlert('Регистрация успешна! Перенаправление...', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('registerCodeModal'));
            modal.hide();
            setTimeout(() => {
                window.location.href = data.redirect_url || '/';
            }, 1000);
        } else {
            showRegCodeAlert(data.message || 'Неверный код', 'danger');
            document.getElementById('reg_modal_code').value = '';
            document.getElementById('reg_modal_code').focus();
        }
    } catch (error) {
        console.error('Error:', error);
        showRegCodeAlert('Ошибка соединения. Попробуйте позже.', 'danger');
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.innerHTML = originalText;
    }
});

// Повторная отправка кода регистрации
document.getElementById('regResendCodeBtn')?.addEventListener('click', async function () {
    if (!currentRegEmail) {
        showRegCodeAlert('Email не найден. Попробуйте снова.', 'danger');
        return;
    }

    this.disabled = true;
    this.innerHTML = '<i class="bi bi-hourglass-split"></i> Отправка...';

    try {
        const response = await fetch('/users/resend/code/ajax/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({email: currentRegEmail, action: 'register'})
        });

        const data = await response.json();

        if (data.success) {
            showRegCodeAlert('Новый код отправлен на ваш email', 'success');
        } else {
            showRegCodeAlert(data.message || 'Ошибка отправки', 'danger');
        }
    } catch (error) {
        console.error('Error:', error);
        showRegCodeAlert('Ошибка соединения', 'danger');
    } finally {
        this.disabled = false;
        this.innerHTML = '<i class="bi bi-arrow-repeat"></i> Отправить код повторно';
    }
});

// Сброс формы при закрытии модального окна регистрации по коду
document.getElementById('registerCodeModal')?.addEventListener('hidden.bs.modal', function () {
    document.getElementById('reg_email').value = '';
    document.getElementById('reg_firstname').value = '';
    document.getElementById('reg_lastname').value = '';
    document.getElementById('reg_modal_code').value = '';
    document.getElementById('regCodeAlert').innerHTML = '';
    currentRegEmail = '';
    document.getElementById('regStepEmail').style.display = 'block';
    document.getElementById('regStepCode').style.display = 'none';
});

// Переключение на обычный вход из модального окна входа по коду
document.getElementById('switchToLoginFromCode')?.addEventListener('click', function (e) {
    e.preventDefault();
    const codeModal = bootstrap.Modal.getInstance(document.getElementById('loginCodeModal'));
    codeModal.hide();
    setTimeout(() => {
        const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
        loginModal.show();
    }, 300);
});

// Переключение на обычную регистрацию из модального окна регистрации по коду
document.getElementById('switchToRegisterFromCode')?.addEventListener('click', function (e) {
    e.preventDefault();
    const codeModal = bootstrap.Modal.getInstance(document.getElementById('registerCodeModal'));
    codeModal.hide();
    setTimeout(() => {
        const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
        registerModal.show();
    }, 300);
});

// Управление количеством товара в карточках (product_list)
document.addEventListener('DOMContentLoaded', function () {
    // Обработчики для кнопок "-" и "+" в списке товаров
    document.querySelectorAll('.dec-quantity').forEach(btn => {
        btn.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const input = document.querySelector(`.quantity-input[data-product-id="${productId}"]`);
            let value = parseInt(input.value);
            if (value > 1) {
                input.value = value - 1;
            }
        });
    });

    document.querySelectorAll('.inc-quantity').forEach(btn => {
        btn.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const input = document.querySelector(`.quantity-input[data-product-id="${productId}"]`);
            const max = parseInt(input.max);
            let value = parseInt(input.value);
            if (value < max) {
                input.value = value + 1;
            }
        });
    });

    // Обработчики для кнопок "-" и "+" на странице товара
    const decBtn = document.querySelector('.dec-quantity-detail');
    const incBtn = document.querySelector('.inc-quantity-detail');
    const quantityInput = document.querySelector('.quantity-input-detail');

    if (decBtn && incBtn && quantityInput) {
        decBtn.addEventListener('click', function () {
            let value = parseInt(quantityInput.value);
            if (value > 1) {
                quantityInput.value = value - 1;
            }
        });

        incBtn.addEventListener('click', function () {
            let value = parseInt(quantityInput.value);
            let max = parseInt(quantityInput.max);
            if (value < max) {
                quantityInput.value = value + 1;
            }
        });
    }

    // Добавление в корзину с выбранным количеством
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            let quantity = 1;

            // Пытаемся найти input с количеством
            const quantityInput = document.querySelector(`.quantity-input[data-product-id="${productId}"]`);
            if (quantityInput) {
                quantity = parseInt(quantityInput.value);
            }

            // Для страницы товара
            const detailQuantity = document.querySelector('.quantity-input-detail');
            if (detailQuantity) {
                quantity = parseInt(detailQuantity.value);
            }

            addToCart(productId, this, quantity);
        });
    });
});