# DESK APP

App desktop leggera con 6 sezioni. Richiede Python 3 e psutil.

## Installazione
```
pip install psutil
python desk_app.py
```

## Sezioni

| Sezione | Funzione |
|---------|----------|
| 🍅 **Pomodoro** | Timer 25min lavoro / 5min pausa, contatore sessioni |
| 📝 **Note** | Testo libero, salvato in `note.json` |
| 🤖 **AI** | Chat con Ollama (locale), Groq o Gemini. Config in `ai_config.json` |
| 🔗 **Link** | Salva e apri link, persistenti in `links.json` |
| ✅ **To-Do** | Lista attività con spunta e cancellazione, salvata in `promemoria.json` |
| 🖥 **Info** | OS, CPU, RAM, Disco, Batteria — aggiornati ogni 2 sec |

## AI: provider supportati

| Provider | Costo | Dove prendere la key |
|----------|-------|----------------------|
| **Ollama** | Gratis, locale | [ollama.com](https://ollama.com) → `ollama pull llama3.2` |
| **Groq** | Gratis con key | [console.groq.com](https://console.groq.com) |
| **Gemini** | Gratis con key | [aistudio.google.com](https://aistudio.google.com) |

## File generati
- `note.json` — testo delle note
- `links.json` — link salvati
- `promemoria.json` — to-do list
- `ai_config.json` — provider e API key AI
