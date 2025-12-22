# GitHub Personal Access Token Guide

## ⚠️ Важливо: Токен показується тільки один раз!

GitHub показує токен **тільки під час створення**. Якщо ви його не скопіювали, потрібно створити новий.

## 📝 Як створити/знайти токен:

### Крок 1: Перейдіть на сторінку токенів
1. Відкрийте: https://github.com/settings/tokens
2. Або: GitHub → Settings (правый верхній кут) → Developer settings → Personal access tokens → Tokens (classic)

### Крок 2: Створіть новий токен
1. Натисніть **"Generate new token"** → **"Generate new token (classic)"**
2. Заповніть форму:
   - **Note**: `DocBot Deployment` (будь-яка назва)
   - **Expiration**: оберіть термін (рекомендую 90 days або No expiration)
   - **Scopes**: обов'язково відмітьте **`repo`** (повний доступ до репозиторіїв)
     - Це дасть доступ до: repo:status, repo_deployment, public_repo, repo:invite, security_events

### Крок 3: Скопіюйте токен
1. Після натискання **"Generate token"**
2. **ВАЖЛИВО**: Токен з'явиться на екрані **тільки один раз**
3. Він буде виглядати приблизно так: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
4. **НЕМЕДЛЕННО скопіюйте його** (Ctrl+C або Cmd+C)

### Крок 4: Збережіть токен безпечно
- Збережіть токен в безпечному місці (якщо втратите - доведеться створювати новий)
- Або використайте менеджер паролів

## 🚀 Використання токена для push:

```bash
cd /Users/maximdoroshenko/Documents/DocBot
git push -u origin main --force
```

Коли з'явиться запит:
- **Username**: введіть ваш GitHub username
- **Password**: **вставте токен** (не ваш пароль!)

## 🔄 Якщо токен вже створений, але ви його не скопіювали:

1. Перейдіть на: https://github.com/settings/tokens
2. Знайдіть ваш токен в списку
3. **Проблема**: GitHub не показує значення токена після створення
4. **Рішення**: Видаліть старий токен і створіть новий

## ✅ Альтернатива: Використайте GitHub CLI

Якщо у вас встановлений GitHub CLI:

```bash
gh auth login
cd /Users/maximdoroshenko/Documents/DocBot
git push -u origin main --force
```

Це автоматично налаштує автентифікацію.

## 🔐 Безпека:

- Ніколи не публікуйте токен в коді або на GitHub
- Якщо токен потрапив в публічний доступ - негайно видаліть його
- Використовуйте мінімальні необхідні права (scope: `repo`)

