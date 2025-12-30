# 🚀 Deployment Guide: LangGraph DocBot on Google Cloud Platform

Покрокова інструкція для деплою проекту на GCP Cloud Run.

---

## 📋 Передумови

1. ✅ Google Cloud Platform аккаунт
2. ✅ Встановлений Google Cloud SDK (`gcloud`)
3. ✅ Google API Key для Gemini
4. ✅ Доступ до проекту в GCP

---

## 🔧 Крок 1: Встановлення та налаштування Google Cloud SDK

### macOS:
```bash
# Встановлення через Homebrew
brew install google-cloud-sdk

# Або завантажте з офіційного сайту
# https://cloud.google.com/sdk/docs/install
```

### Linux:
```bash
# Завантажте та встановіть
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Windows:
Завантажте інсталятор з [офіційного сайту](https://cloud.google.com/sdk/docs/install)

---

## 🔐 Крок 2: Авторизація та налаштування проекту

```bash
# Авторизуйтеся в GCP
gcloud auth login

# Встановіть проект (замініть YOUR_PROJECT_ID на ваш Project ID)
gcloud config set project YOUR_PROJECT_ID

# Перевірте поточний проект
gcloud config get-value project
```

**Як знайти Project ID:**
1. Відкрийте [GCP Console](https://console.cloud.google.com)
2. У верхній панелі ви побачите назву проекту
3. Або перейдіть в Settings → Project Settings

---

## 🔑 Крок 3: Створення Secret для Google API Key

### Варіант A: Через командний рядок

```bash
# Створіть secret (замініть YOUR_GOOGLE_API_KEY на ваш ключ)
echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create google-api-key \
  --data-file=- \
  --replication-policy="automatic"
```

### Варіант B: Через GCP Console

1. Відкрийте [Secret Manager](https://console.cloud.google.com/security/secret-manager)
2. Натисніть **"Create Secret"**
3. Назва: `google-api-key`
4. Значення: вставте ваш Google API Key
5. Натисніть **"Create Secret"**

### Налаштування доступу для Cloud Run:

```bash
# Додайте права для Cloud Run
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")

gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 🛠️ Крок 4: Увімкнення необхідних API

```bash
# Увімкніть необхідні сервіси
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

---

## 🐳 Крок 5: Білд Docker образів

### Варіант A: Локальний білд та push

```bash
cd /Users/maximdoroshenko/Documents/DocBot/langgraph_docbot

# Налаштуйте Docker для GCP
gcloud auth configure-docker

# Білд та push FastAPI образу
docker build -t gcr.io/YOUR_PROJECT_ID/langgraph-docbot-api -f Dockerfile .
docker push gcr.io/YOUR_PROJECT_ID/langgraph-docbot-api

# Білд та push Streamlit образу
docker build -t gcr.io/YOUR_PROJECT_ID/langgraph-docbot-ui -f Dockerfile.streamlit .
docker push gcr.io/YOUR_PROJECT_ID/langgraph-docbot-ui
```

### Варіант B: Cloud Build (рекомендовано)

```bash
# Відправте код на Cloud Build
gcloud builds submit --config cloudbuild.yaml
```

---

## 🚀 Крок 6: Деплой FastAPI на Cloud Run

```bash
gcloud run deploy langgraph-docbot-api \
  --image gcr.io/YOUR_PROJECT_ID/langgraph-docbot-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-secrets="GOOGLE_API_KEY=google-api-key:latest" \
  --set-env-vars="MODEL_NAME=gemini-2.5-flash,DOCS_OUTPUT_DIR=/tmp/generated_docs"
```

**Збережіть URL FastAPI сервісу** (потрібен для Streamlit):
```
https://langgraph-docbot-api-XXXXX-uc.a.run.app
```

---

## 🎨 Крок 7: Деплой Streamlit UI на Cloud Run

```bash
# Замініть YOUR_API_URL на URL з попереднього кроку
gcloud run deploy langgraph-docbot-ui \
  --image gcr.io/YOUR_PROJECT_ID/langgraph-docbot-ui \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars="API_URL=https://langgraph-docbot-api-XXXXX-uc.a.run.app"
```

**Замініть `XXXXX` на реальний URL вашого FastAPI сервісу!**

---

## ✅ Крок 8: Перевірка деплою

### Перевірка FastAPI:
```bash
# Отримайте URL
FASTAPI_URL=$(gcloud run services describe langgraph-docbot-api \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

# Перевірка health endpoint
curl $FASTAPI_URL/health
```

### Перевірка Streamlit:
```bash
# Отримайте URL
STREAMLIT_URL=$(gcloud run services describe langgraph-docbot-ui \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)')

echo "Streamlit UI доступний за адресою: $STREAMLIT_URL"
```

Відкрийте URL у браузері та перевірте роботу!

---

## 🔄 Крок 9: Оновлення деплою

### Оновлення коду:

```bash
# 1. Внесіть зміни в код
# 2. Перебілдіть образи
gcloud builds submit --config cloudbuild.yaml

# Або вручну:
docker build -t gcr.io/YOUR_PROJECT_ID/langgraph-docbot-api -f Dockerfile .
docker push gcr.io/YOUR_PROJECT_ID/langgraph-docbot-api

# 3. Оновіть сервіси
gcloud run deploy langgraph-docbot-api \
  --image gcr.io/YOUR_PROJECT_ID/langgraph-docbot-api \
  --region us-central1
```

---

## 📊 Моніторинг та логи

### Перегляд логів:

```bash
# Логи FastAPI
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=langgraph-docbot-api" --limit 50

# Логи Streamlit
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=langgraph-docbot-ui" --limit 50
```

### В GCP Console:
1. Відкрийте [Cloud Run](https://console.cloud.google.com/run)
2. Виберіть сервіс
3. Перейдіть на вкладку "Logs"

---

## 💰 Оцінка вартості

Cloud Run сплачується за використання:
- **CPU**: $0.00002400 за vCPU-секунду
- **Memory**: $0.00000250 за GiB-секунду
- **Requests**: $0.40 за мільйон запитів

**Приклад для нашого проекту:**
- FastAPI: 2 vCPU, 2Gi RAM, ~1000 запитів/день
- Streamlit: 1 vCPU, 1Gi RAM, ~100 запитів/день
- **Орієнтовна вартість: $5-15/місяць** (залежить від навантаження)

---

## 🔒 Безпека

### Рекомендації:

1. ✅ Використовуйте Secret Manager для API ключів
2. ✅ Обмежте доступ до сервісів (видаліть `--allow-unauthenticated` якщо потрібно)
3. ✅ Налаштуйте VPC connector для приватних сервісів
4. ✅ Увімкніть Cloud Armor для захисту від DDoS

### Обмеження доступу:

```bash
# Видалити публічний доступ
gcloud run services update langgraph-docbot-api \
  --no-allow-unauthenticated \
  --region us-central1
```

---

## 🐛 Troubleshooting

### Проблема: "Permission denied"
```bash
# Перевірте права доступу
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

### Проблема: "Secret not found"
```bash
# Перевірте наявність secret
gcloud secrets list
gcloud secrets describe google-api-key
```

### Проблема: "Image pull failed"
```bash
# Перевірте доступ до Container Registry
gcloud auth configure-docker
```

### Проблема: "Timeout"
```bash
# Збільште timeout
gcloud run services update langgraph-docbot-api \
  --timeout 600 \
  --region us-central1
```

---

## 📚 Додаткові ресурси

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)

---

## ✅ Чеклист деплою

- [ ] Встановлено Google Cloud SDK
- [ ] Авторизовано в GCP
- [ ] Створено проект
- [ ] Створено secret для Google API Key
- [ ] Увімкнено необхідні API
- [ ] Збілджено Docker образи
- [ ] Задеплоєно FastAPI на Cloud Run
- [ ] Задеплоєно Streamlit на Cloud Run
- [ ] Перевірено роботу сервісів
- [ ] Налаштовано моніторинг

---

**Готово! 🎉 Ваш проект тепер працює на GCP Cloud Run!**



