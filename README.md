# DESK APP

App desktop leggera con 5 sezioni.

## Requisiti
```
pip install psutil
```

## Sezioni
- **Pomodoro** – timer 25min/5min con contatore sessioni
- **Note** – testo libero salvato automaticamente in `note.json`
- **AI** – in arrivo
- **Link** – salva e apri link velocemente, persistenti in `links.json`
- **Info** – caratteristiche PC e prestazioni in tempo reale (CPU, RAM, Disco, Batteria)

## Avvio
```
python desk_app.py
```

## File generati
| File | Contenuto |
|------|-----------|
| `note.json` | testo delle note |
| `links.json` | lista dei link salvati |
