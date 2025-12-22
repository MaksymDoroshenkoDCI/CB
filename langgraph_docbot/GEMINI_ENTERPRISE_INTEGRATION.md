# 🚀 Інтеграція з Gemini Enterprise Agents

Цей документ описує, як інтегрувати LangGraph DocBot з **Gemini Enterprise Agents** для створення повноцінного conversational агента для генерації IT-документації.

---

## 📋 Зміст

1. [Архітектура інтеграції](#архітектура-інтеграції)
2. [Налаштування Gemini Enterprise Agent](#налаштування-gemini-enterprise-agent)
3. [API Endpoints](#api-endpoints)
4. [Приклади використання](#приклади-використання)
5. [Workflow в Gemini Enterprise](#workflow-в-gemini-enterprise)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ Архітектура інтеграції

```
┌─────────────────────────────────────┐
│   Gemini Enterprise Agent           │
│   (Conversational Agent)            │
│                                     │
│   - Веде діалог з користувачем     │
│   - Керує workflow                  │
│   - Викликає API endpoints          │
└──────────────┬──────────────────────┘
               │
               │ HTTP/HTTPS
               │
               ▼
┌─────────────────────────────────────┐
│   FastAPI Backend                   │
│   (LangGraph DocBot)                │
│                                     │
│   /conversation/start               │
│   /conversation/continue            │
│   /conversation/generate            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   LangGraph Workflow                 │
│                                     │
│   Conversation → Outline → Draft    │
│   → Refine → Persist                │
└─────────────────────────────────────┘
```

---

## ⚙️ Налаштування Gemini Enterprise Agent

### 1. Створення Conversational Agent

У Gemini Enterprise створіть новий **Conversational Agent** з наступними параметрами:

#### Основні налаштування:
- **Name**: `IT Documentation Agent`
- **Type**: `Conversational Agent`
- **Model**: `gemini-2.0-flash-exp` або `gemini-1.5-pro`
- **Temperature**: `0.3`

#### System Prompt:

```
Ти — досвідчений системний аналітик, який допомагає збирати вимоги до IT-систем для створення технічної документації.

Твоя мета:
1. Вести діалог з користувачем
2. Збирати всі необхідні вимоги через структуровані питання
3. Коли всі дані зібрані — викликати API для генерації документації

Процес роботи:
1. Почати діалог через API endpoint /conversation/start
2. Задавати питання користувачу на основі отриманих питань від API
3. Зберігати відповіді та продовжувати діалог через /conversation/continue
4. Коли діалог завершено — викликати /conversation/generate для створення документації

Будь дружнім, професійним та допоміжним. Якщо користувач каже "готово" або "згенеруй документацію" — завершуй діалог та викликай генерацію.
```

### 2. Додавання Tools (API Calls)

Додайте наступні **Tools** до вашого Gemini Enterprise Agent:

#### Tool 1: Start Conversation

```json
{
  "name": "start_conversation",
  "description": "Починає новий діалог для збору вимог до IT-системи. Повертає перше питання.",
  "parameters": {
    "type": "object",
    "properties": {
      "project_name": {
        "type": "string",
        "description": "Назва проекту (опціонально)"
      }
    }
  },
  "http_request": {
    "method": "POST",
    "url": "https://your-domain.com/conversation/start",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "project_name": "{{project_name}}"
    }
  }
}
```

#### Tool 2: Continue Conversation

```json
{
  "name": "continue_conversation",
  "description": "Продовжує діалог з відповіддю користувача. Повертає наступне питання або сигналізує про завершення.",
  "parameters": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "ID сесії діалогу"
      },
      "answer": {
        "type": "string",
        "description": "Відповідь користувача на поточне питання"
      }
    },
    "required": ["session_id", "answer"]
  },
  "http_request": {
    "method": "POST",
    "url": "https://your-domain.com/conversation/continue",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "session_id": "{{session_id}}",
      "answer": "{{answer}}"
    }
  }
}
```

#### Tool 3: Generate Documentation

```json
{
  "name": "generate_documentation",
  "description": "Генерує технічну документацію на основі зібраних вимог з діалогу.",
  "parameters": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "ID сесії діалогу"
      },
      "force": {
        "type": "boolean",
        "description": "Завершити діалог навіть якщо не всі питання зібрані (за замовчуванням false)"
      }
    },
    "required": ["session_id"]
  },
  "http_request": {
    "method": "POST",
    "url": "https://your-domain.com/conversation/generate",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "session_id": "{{session_id}}",
      "force": "{{force}}"
    }
  }
}
```

---

## 🔌 API Endpoints

### 1. POST `/conversation/start`

Починає новий діалог.

**Request:**
```json
{
  "project_name": "fintom8",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "question": "Опиши основну мету системи. Що вона має робити?",
  "message": "Діалог розпочато. Відповідайте на питання для збору вимог.",
  "conversation_started": true
}
```

### 2. POST `/conversation/continue`

Продовжує діалог з відповіддю.

**Request:**
```json
{
  "session_id": "uuid-here",
  "answer": "Система призначена для автоматизації процесів продажів..."
}
```

**Response (продовження діалогу):**
```json
{
  "session_id": "uuid-here",
  "question": "Хто основні користувачі системи?",
  "message": "Відповідь збережено. Продовжуйте діалог.",
  "conversation_complete": false,
  "collected_requirements": null
}
```

**Response (діалог завершено):**
```json
{
  "session_id": "uuid-here",
  "question": null,
  "message": "Всі вимоги зібрано! Тепер можна згенерувати документацію через /conversation/generate",
  "conversation_complete": true,
  "collected_requirements": "# Зібрані вимоги до системи\n\n## Питання 1\nВідповідь 1\n\n..."
}
```

### 3. POST `/conversation/generate`

Генерує документацію на основі зібраних вимог.

**Request:**
```json
{
  "session_id": "uuid-here",
  "force": false
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "outline": "1. Вступ та загальний опис...",
  "documentation": "# Технічна документація...",
  "message": "Документацію згенеровано і збережено в txt."
}
```

---

## 💡 Приклади використання

### Приклад 1: Базовий workflow в Gemini Enterprise

```
Користувач: "Хочу створити документацію для системи fintom8"

Agent:
1. Викликає start_conversation(project_name="fintom8")
2. Отримує перше питання: "Опиши основну мету системи..."
3. Задає питання користувачу
4. Отримує відповідь
5. Викликає continue_conversation(session_id="...", answer="...")
6. Повторює кроки 3-5 до завершення діалогу
7. Викликає generate_documentation(session_id="...")
8. Показує користувачу згенеровану документацію
```

### Приклад 2: Використання Memory в Gemini Enterprise

Gemini Enterprise має вбудовану пам'ять. Ви можете зберігати `session_id` в пам'яті агента:

```
Memory:
- session_id: "abc-123"
- project_name: "fintom8"
- current_question_index: 3
```

Це дозволить агенту продовжувати діалог навіть після перезапуску.

---

## 🔄 Workflow в Gemini Enterprise

### Створення Workflow Agent

Якщо ви хочете використати **Workflow Agent** замість Conversational Agent:

1. Створіть новий Workflow Agent
2. Додайте кроки:
   - **Step 1**: Start Conversation
   - **Step 2**: Loop: Ask Question → Get Answer → Continue Conversation
   - **Step 3**: Check if Complete
   - **Step 4**: Generate Documentation
   - **Step 5**: Return Result

### Умовна логіка:

```python
# Псевдокод для Workflow
if conversation_complete:
    result = generate_documentation(session_id)
    return result
else:
    question = continue_conversation(session_id, answer)
    return question
```

---

## 🔒 Безпека та аутентифікація

### Рекомендації:

1. **API Key Authentication**: Додайте API ключ до заголовків запитів:
   ```json
   "headers": {
     "Content-Type": "application/json",
     "X-API-Key": "your-api-key"
   }
   ```

2. **HTTPS**: Використовуйте HTTPS для всіх API викликів

3. **Rate Limiting**: Налаштуйте обмеження на кількість запитів

4. **Session Validation**: Перевіряйте валідність session_id на бекенді

---

## 🐛 Troubleshooting

### Проблема 1: Session not found

**Причина**: Сесія була видалена або не існує.

**Рішення**: Почніть новий діалог через `/conversation/start`.

### Проблема 2: Conversation not complete

**Причина**: Діалог не завершено, але намагаєтесь згенерувати документацію.

**Рішення**: Використайте `force=true` в `/conversation/generate` або завершіть діалог.

### Проблема 3: API Timeout

**Причина**: Генерація документації займає багато часу.

**Рішення**: 
- Збільште timeout в налаштуваннях Gemini Enterprise
- Використайте асинхронний підхід (webhook callback)

### Проблема 4: Invalid response format

**Причина**: API повертає неочікуваний формат.

**Рішення**: Перевірте формат відповіді в Swagger документації (`/docs`).

---

## 📚 Додаткові ресурси

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Gemini Enterprise Agents Guide](https://ai.google.dev/gemini-api/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## ✅ Checklist для інтеграції

- [ ] Налаштовано Gemini Enterprise Agent
- [ ] Додано всі 3 Tools (start, continue, generate)
- [ ] Налаштовано System Prompt
- [ ] Протестовано API endpoints
- [ ] Налаштовано аутентифікацію (якщо потрібно)
- [ ] Налаштовано HTTPS
- [ ] Протестовано повний workflow
- [ ] Налаштовано error handling
- [ ] Додано логування

---

## 🎯 Приклад повного діалогу

```
Користувач: Привіт, хочу створити документацію для CRM системи

Agent: Привіт! Допоможу тобі створити технічну документацію. 
       Почнемо з першого питання: Опиши основну мету системи. Що вона має робити?

Користувач: Система призначена для автоматизації процесів продажів, 
            управління клієнтською базою та аналітики продажів.

Agent: Чудово! Наступне питання: Хто основні користувачі системи? 
       Для кого вона призначена?

Користувач: Основні користувачі - менеджери з продажів, керівники відділу продажів 
            та аналітики.

Agent: Дякую! Продовжуємо: Які ключові функції повинні бути реалізовані? 
       Опиши основні можливості.

Користувач: Управління контактами, воронка продажів, звітність, інтеграція з email.

Agent: Відмінно! Останнє питання: Які технології плануються?

Користувач: Python, Django, PostgreSQL, React, Docker.

Agent: Чудово! Всі вимоги зібрано. Зараз згенерую технічну документацію...

[Agent викликає generate_documentation]

Agent: ✅ Документацію згенеровано! Ось структура та повний документ:

[Показує outline та documentation]
```

---

**Готово!** Тепер ваш Gemini Enterprise Agent може вести діалог з користувачами та генерувати технічну документацію через LangGraph DocBot. 🚀

