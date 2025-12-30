# ⚡ Quick Deploy Guide

Швидкий старт для деплою на GCP Cloud Run.

## 🚀 Швидкий деплой (3 кроки)

### 1. Підготовка

```bash
# Встановіть Google Cloud SDK (якщо ще не встановлено)
brew install google-cloud-sdk  # macOS
# або https://cloud.google.com/sdk/docs/install

# Авторизуйтеся
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Створіть Secret для API Key

```bash
echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create google-api-key --data-file=-
```

### 3. Запустіть деплой

```bash
./deploy_gcp.sh YOUR_PROJECT_ID
```

**Готово!** 🎉

---

## 📝 Покрокова інструкція

Детальна інструкція: [`DEPLOYMENT_GCP.md`](DEPLOYMENT_GCP.md)

---

## ✅ Чеклист

- [ ] Встановлено `gcloud` CLI
- [ ] Авторизовано в GCP (`gcloud auth login`)
- [ ] Встановлено проект (`gcloud config set project YOUR_PROJECT_ID`)
- [ ] Створено secret `google-api-key`
- [ ] Запущено `./deploy_gcp.sh YOUR_PROJECT_ID`
- [ ] Перевірено URL сервісів

---

## 🔗 Корисні команди

```bash
# Перевірка статусу сервісів
gcloud run services list

# Перегляд логів
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Отримання URL
gcloud run services describe langgraph-docbot-ui --format 'value(status.url)'
```

---

**Проблеми?** Дивіться [`DEPLOYMENT_GCP.md`](DEPLOYMENT_GCP.md) секцію Troubleshooting.



