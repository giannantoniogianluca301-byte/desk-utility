import tkinter as tk
import webbrowser
import json
import os
import platform
import psutil
import threading
import urllib.request

# --- POMODORO: variabili e logica ---
TEMPO_LAVORO  = 25 * 60
TEMPO_PAUSA   =  5 * 60
tempo_rimasto  = TEMPO_LAVORO
pomodoro_on    = False
timer_id       = None
modalita       = "lavoro"
pomodori_fatti = 0

def _fmt(sec):
    return f"{sec // 60:02d}:{sec % 60:02d}"

def _countdown():
    global tempo_rimasto, pomodoro_on, timer_id, modalita, pomodori_fatti
    if not pomodoro_on:
        return
    if tempo_rimasto > 0:
        tempo_rimasto -= 1
        label_timer.config(text=_fmt(tempo_rimasto),
                           fg="#e74c3c" if tempo_rimasto <= 60 else "#2c3e50")
        timer_id = root.after(1000, _countdown)
    else:
        pomodoro_on = False
        btn_start.config(text="▶  Start")
        if modalita == "lavoro":
            pomodori_fatti += 1
            label_pomodori.config(text="🍅 " * pomodori_fatti)
            modalita = "pausa"
            tempo_rimasto = TEMPO_PAUSA
            label_modalita.config(text="☕  Pausa!", fg="#27ae60")
        else:
            modalita = "lavoro"
            tempo_rimasto = TEMPO_LAVORO
            label_modalita.config(text="🍅  Lavoro!", fg="#c0392b")
        label_timer.config(text=_fmt(tempo_rimasto), fg="#2c3e50")

def _start_stop():
    global pomodoro_on, timer_id
    if not pomodoro_on:
        pomodoro_on = True
        btn_start.config(text="⏸  Pausa")
        _countdown()
    else:
        pomodoro_on = False
        btn_start.config(text="▶  Start")
        if timer_id:
            root.after_cancel(timer_id)

def _reset():
    global pomodoro_on, timer_id, tempo_rimasto, modalita
    pomodoro_on = False
    if timer_id:
        root.after_cancel(timer_id)
    modalita = "lavoro"
    tempo_rimasto = TEMPO_LAVORO
    btn_start.config(text="▶  Start")
    label_modalita.config(text="🍅  Lavoro!", fg="#c0392b")
    label_timer.config(text=_fmt(TEMPO_LAVORO), fg="#2c3e50")

# --- LINK: logica ---
FILE_LINK = "links.json"

def _salva_link():
    with open(FILE_LINK, "w") as f:
        json.dump(lista_link, f)

def _carica_link():
    if os.path.exists(FILE_LINK):
        with open(FILE_LINK, "r") as f:
            return json.load(f)
    return []

lista_link = _carica_link()

def _aggiungi_link():
    url = entry_link.get().strip()
    if url:
        lista_link.append(url)
        _salva_link()
        _aggiorna_lista()
        entry_link.delete(0, tk.END)

def _apri_link(url):
    webbrowser.open(url)

def _elimina_link(url):
    lista_link.remove(url)
    _salva_link()
    _aggiorna_lista()

def _aggiorna_lista():
    for widget in frame_lista.winfo_children():
        widget.destroy()
    for url in lista_link:
        riga = tk.Frame(frame_lista, bg="white")
        riga.pack(fill="x", pady=2)
        tk.Label(riga, text=url, bg="white", fg="#2c3e50",
                 font=("Arial", 9), anchor="w", width=22,
                 cursor="hand2").pack(side="left")
        tk.Button(riga, text="Apri", command=lambda u=url: _apri_link(u),
                  bg="#3498db", fg="white", relief="flat",
                  font=("Arial", 8), padx=4).pack(side="left", padx=2)
        tk.Button(riga, text="✕", command=lambda u=url: _elimina_link(u),
                  bg="#e74c3c", fg="white", relief="flat",
                  font=("Arial", 8), padx=4).pack(side="left")

# --- NOTE: logica ---
FILE_NOTE = "note.json"

def _salva_note():
    testo = text_note.get("1.0", tk.END)
    with open(FILE_NOTE, "w") as f:
        json.dump(testo, f)

def _carica_note():
    if os.path.exists(FILE_NOTE):
        with open(FILE_NOTE, "r") as f:
            return json.load(f)
    return ""

# --- TO-DO LIST: logica ---
FILE_PROM = "promemoria.json"

def _salva_promemoria():
    with open(FILE_PROM, "w") as f:
        json.dump(lista_promemoria, f)

def _carica_promemoria():
    if os.path.exists(FILE_PROM):
        with open(FILE_PROM, "r") as f:
            return json.load(f)
    return []

lista_promemoria = _carica_promemoria()

def _aggiungi_promemoria():
    testo = entry_prom.get().strip()
    if testo:
        lista_promemoria.append({"testo": testo, "fatto": False})
        _salva_promemoria()
        _aggiorna_promemoria()
        entry_prom.delete(0, tk.END)

def _toggle_promemoria(i):
    lista_promemoria[i]["fatto"] = not lista_promemoria[i]["fatto"]
    _salva_promemoria()
    _aggiorna_promemoria()

def _elimina_promemoria(i):
    lista_promemoria.pop(i)
    _salva_promemoria()
    _aggiorna_promemoria()

def _elimina_fatti():
    lista_promemoria[:] = [p for p in lista_promemoria if not p["fatto"]]
    _salva_promemoria()
    _aggiorna_promemoria()

def _aggiorna_promemoria():
    for widget in frame_prom_lista.winfo_children():
        widget.destroy()
    fatti  = sum(1 for p in lista_promemoria if p["fatto"])
    totale = len(lista_promemoria)
    lbl_prom_counter.config(text=f"{fatti}/{totale} completati")
    for i, p in enumerate(lista_promemoria):
        fatto = p["fatto"]
        riga  = tk.Frame(frame_prom_lista, bg="white")
        riga.pack(fill="x", pady=1)
        segno = "✅" if fatto else "☐"
        tk.Button(riga, text=segno, command=lambda idx=i: _toggle_promemoria(idx),
                  bg="white", relief="flat", font=("Arial", 11),
                  cursor="hand2", bd=0).pack(side="left")
        stile  = ("Arial", 9, "overstrike") if fatto else ("Arial", 9)
        colore = "#bdc3c7" if fatto else "#2c3e50"
        tk.Label(riga, text=p["testo"], bg="white", fg=colore,
                 font=stile, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Button(riga, text="✕", command=lambda idx=i: _elimina_promemoria(idx),
                  bg="white", fg="#e74c3c", relief="flat",
                  font=("Arial", 9), cursor="hand2", bd=0).pack(side="right")

# --- INFO PC: logica ---
info_update_id = None

def _colore_percentuale(val):
    if val < 50:   return "#27ae60"
    elif val < 80: return "#f39c12"
    else:          return "#e74c3c"

def _aggiorna_info():
    global info_update_id
    cpu = psutil.cpu_percent(interval=None)
    c_cpu = _colore_percentuale(cpu)
    lbl_cpu_val.config(text=f"{cpu:.1f}%", fg=c_cpu)
    bar_cpu_fill.config(width=int(180 * cpu / 100), bg=c_cpu)

    ram = psutil.virtual_memory()
    ram_pct = ram.percent
    c_ram = _colore_percentuale(ram_pct)
    lbl_ram_val.config(text=f"{ram.used/1024**3:.1f} / {ram.total/1024**3:.1f} GB  ({ram_pct:.0f}%)", fg=c_ram)
    bar_ram_fill.config(width=int(180 * ram_pct / 100), bg=c_ram)

    disk = psutil.disk_usage("/")
    disk_pct = disk.percent
    c_disk = _colore_percentuale(disk_pct)
    lbl_disk_val.config(text=f"{disk.used/1024**3:.1f} / {disk.total/1024**3:.1f} GB  ({disk_pct:.0f}%)", fg=c_disk)
    bar_disk_fill.config(width=int(180 * disk_pct / 100), bg=c_disk)

    batt = psutil.sensors_battery()
    if batt:
        stato = "🔌" if batt.power_plugged else "🔋"
        lbl_batt_val.config(text=f"{stato}  {batt.percent:.0f}%",
                            fg=_colore_percentuale(100 - batt.percent))
    else:
        lbl_batt_val.config(text="N/D", fg="#7f8c8d")

    info_update_id = root.after(2000, _aggiorna_info)

def _stop_info_update():
    global info_update_id
    if info_update_id:
        root.after_cancel(info_update_id)
        info_update_id = None

# --- AI: logica ---
FILE_AI = "ai_config.json"
ai_history = []

def _salva_ai_config():
    cfg = {
        "provider": ai_provider.get(),
        "api_key":  entry_api.get().strip(),
        "model":    entry_model.get().strip()
    }
    with open(FILE_AI, "w") as f:
        json.dump(cfg, f)

def _carica_ai_config():
    if os.path.exists(FILE_AI):
        with open(FILE_AI, "r") as f:
            return json.load(f)
    return {"provider": "Ollama", "api_key": "", "model": "llama3"}

def _on_provider_change(*_):
    prov = ai_provider.get()
    if prov == "Ollama":
        entry_api.config(state="disabled")
        lbl_api.config(fg="#bdc3c7")
        entry_model.delete(0, tk.END)
        entry_model.insert(0, "llama3.2")
        lbl_model.config(text="Modello:")
    elif prov == "Groq":
        entry_api.config(state="normal")
        lbl_api.config(fg="#2c3e50")
        entry_model.delete(0, tk.END)
        entry_model.insert(0, "llama3-8b-8192")
        lbl_model.config(text="Modello:")
    elif prov == "Gemini":
        entry_api.config(state="normal")
        lbl_api.config(fg="#2c3e50")
        entry_model.delete(0, tk.END)
        entry_model.insert(0, "gemini-1.5-flash")
        lbl_model.config(text="Modello:")

def _ai_aggiungi_messaggio(ruolo, testo):
    chat_box.config(state="normal")
    prefisso = "Tu: " if ruolo == "user" else "AI: "
    chat_box.insert(tk.END, f"{prefisso}{testo}\n\n", ruolo)
    chat_box.tag_config("user", foreground="#2c3e50")
    chat_box.tag_config("assistant", foreground="#8e44ad")
    chat_box.see(tk.END)
    chat_box.config(state="disabled")

def _chiedi_ai():
    testo = entry_msg.get().strip()
    if not testo:
        return
    entry_msg.delete(0, tk.END)
    btn_invia.config(state="disabled", text="...")
    ai_history.append({"role": "user", "content": testo})
    _ai_aggiungi_messaggio("user", testo)

    def _chiama():
        try:
            risposta = _chiama_api()
        except Exception as e:
            risposta = f"[Errore: {e}]"
        ai_history.append({"role": "assistant", "content": risposta})
        root.after(0, lambda: _ai_aggiungi_messaggio("assistant", risposta))
        root.after(0, lambda: btn_invia.config(state="normal", text="Invia"))

    threading.Thread(target=_chiama, daemon=True).start()

def _chiama_api():
    prov  = ai_provider.get()
    key   = entry_api.get().strip()
    model = entry_model.get().strip()

    if prov == "Ollama":
        url  = "http://localhost:11434/api/chat"
        body = json.dumps({"model": model or "llama3.2", "messages": ai_history, "stream": False}).encode()
        req  = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["message"]["content"]

    elif prov == "Groq":
        url  = "https://api.groq.com/openai/v1/chat/completions"
        body = json.dumps({"model": model or "llama3-8b-8192", "messages": ai_history}).encode()
        req  = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]

    elif prov == "Gemini":
        url  = f"https://generativelanguage.googleapis.com/v1beta/models/{model or 'gemini-1.5-flash'}:generateContent?key={key}"
        parts = [{"text": m["content"]} for m in ai_history]
        body = json.dumps({"contents": [{"parts": parts}]}).encode()
        req  = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]

    return "Provider non riconosciuto."

def _pulisci_chat():
    global ai_history
    ai_history = []
    chat_box.config(state="normal")
    chat_box.delete("1.0", tk.END)
    chat_box.config(state="disabled")

# --- 1. COSA SUCCEDE QUANDO PREMI I TASTI ---
def _nascondi_tutti():
    _stop_info_update()
    for f in [frame_pomodoro, frame_note, frame_link, frame_prom, frame_ai, frame_info]:
        f.pack_forget()
    label_titolo.pack_forget()
    label_info.pack_forget()

def mostra_pomodoro():
    _nascondi_tutti()
    frame_pomodoro.pack(expand=True, fill="both")

def mostra_note():
    _nascondi_tutti()
    frame_note.pack(expand=True, fill="both")

def mostra_ai():
    _nascondi_tutti()
    frame_ai.pack(expand=True, fill="both")

def mostra_link():
    _nascondi_tutti()
    frame_link.pack(expand=True, fill="both")
    _aggiorna_lista()

def mostra_promemoria():
    _nascondi_tutti()
    frame_prom.pack(expand=True, fill="both")
    _aggiorna_promemoria()

def mostra_info():
    _nascondi_tutti()
    frame_info.pack(expand=True, fill="both")
    _aggiorna_info()

# --- 2. CREAZIONE FINESTRA ---
root = tk.Tk()
root.title("DESK APP")
root.geometry("350x280")
root.attributes("-alpha", 0.85)

# --- 3. MENU A SINISTRA (Frame Grigio) ---
menu = tk.Frame(root, bg="lightgrey", width=100)
menu.pack(side="left", fill="y")

# --- 4. AREA CONTENUTO A DESTRA (Frame Bianco) ---
contenuto = tk.Frame(root, bg="white")
contenuto.pack(side="right", expand=True, fill="both")

# --- 5. OGGETTI DENTRO L'AREA CONTENUTO ---
label_titolo = tk.Label(contenuto, text="Benvenuto", font=("Arial", 16), bg="white")
label_titolo.pack(pady=20)
label_info = tk.Label(contenuto, text="Clicca un tasto a sinistra", bg="white")
label_info.pack()

# --- POMODORO: frame grafico ---
frame_pomodoro = tk.Frame(contenuto, bg="white")
label_modalita = tk.Label(frame_pomodoro, text="🍅  Lavoro!",
                           font=("Arial", 11, "bold"), bg="white", fg="#c0392b")
label_modalita.pack(pady=(18, 0))
label_timer = tk.Label(frame_pomodoro, text=_fmt(TEMPO_LAVORO),
                       font=("Courier", 48, "bold"), bg="white", fg="#2c3e50")
label_timer.pack(pady=5)
frame_btn = tk.Frame(frame_pomodoro, bg="white")
frame_btn.pack()
btn_start = tk.Button(frame_btn, text="▶  Start", command=_start_stop,
                      bg="#1abc9c", fg="white", font=("Arial", 10, "bold"),
                      relief="flat", padx=14, pady=5)
btn_start.pack(side="left", padx=6)
tk.Button(frame_btn, text="↺  Reset", command=_reset,
          bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
          relief="flat", padx=14, pady=5).pack(side="left", padx=6)
label_pomodori = tk.Label(frame_pomodoro, text="", font=("Arial", 14), bg="white")
label_pomodori.pack(pady=(8, 0))

# --- NOTE: frame grafico ---
frame_note = tk.Frame(contenuto, bg="white")
tk.Label(frame_note, text="📝  Note", font=("Arial", 11, "bold"),
         bg="white", fg="#2c3e50").pack(pady=(10, 4))
text_note = tk.Text(frame_note, font=("Arial", 10), relief="solid", bd=1,
                    wrap="word", height=8)
text_note.pack(fill="both", expand=True, padx=10)
text_note.insert("1.0", _carica_note())
tk.Button(frame_note, text="💾  Salva", command=_salva_note,
          bg="#1abc9c", fg="white", font=("Arial", 9, "bold"),
          relief="flat", padx=10, pady=3).pack(pady=6)

# --- LINK: frame grafico ---
frame_link = tk.Frame(contenuto, bg="white")
tk.Label(frame_link, text="🔗  I tuoi Link", font=("Arial", 13, "bold"),
         bg="white", fg="#2c3e50").pack(pady=(15, 8))
frame_input = tk.Frame(frame_link, bg="white")
frame_input.pack()
entry_link = tk.Entry(frame_input, width=22, font=("Arial", 9), relief="solid", bd=1)
entry_link.pack(side="left", padx=(0, 4))
tk.Button(frame_input, text="+ Aggiungi", command=_aggiungi_link,
          bg="#3498db", fg="white", relief="flat",
          font=("Arial", 9, "bold"), padx=8, pady=3).pack(side="left")
frame_lista = tk.Frame(frame_link, bg="white")
frame_lista.pack(fill="both", expand=True, padx=10, pady=8)

# --- TO-DO LIST: frame grafico ---
frame_prom = tk.Frame(contenuto, bg="white")

tk.Label(frame_prom, text="✅  To-Do List", font=("Arial", 11, "bold"),
         bg="white", fg="#2c3e50").pack(pady=(10, 2))

lbl_prom_counter = tk.Label(frame_prom, text="0/0 completati",
                             font=("Arial", 8), bg="white", fg="#7f8c8d")
lbl_prom_counter.pack()

frame_prom_input = tk.Frame(frame_prom, bg="white")
frame_prom_input.pack(pady=4)
entry_prom = tk.Entry(frame_prom_input, width=22, font=("Arial", 9), relief="solid", bd=1)
entry_prom.pack(side="left", padx=(0, 4))
entry_prom.bind("<Return>", lambda e: _aggiungi_promemoria())
tk.Button(frame_prom_input, text="+ Aggiungi", command=_aggiungi_promemoria,
          bg="#e67e22", fg="white", relief="flat",
          font=("Arial", 9, "bold"), padx=8, pady=3).pack(side="left")

frame_prom_lista = tk.Frame(frame_prom, bg="white")
frame_prom_lista.pack(fill="both", expand=True, padx=10)

tk.Button(frame_prom, text="🗑  Elimina completati", command=_elimina_fatti,
          bg="#ecf0f1", fg="#7f8c8d", relief="flat",
          font=("Arial", 8), pady=3).pack(pady=4)

# --- AI: frame grafico ---
frame_ai = tk.Frame(contenuto, bg="white")
tk.Label(frame_ai, text="🤖  AI Chat", font=("Arial", 11, "bold"),
         bg="white", fg="#2c3e50").pack(pady=(8, 2))

f_prov = tk.Frame(frame_ai, bg="white")
f_prov.pack(fill="x", padx=10)
tk.Label(f_prov, text="Provider:", font=("Arial", 8, "bold"),
         bg="white", fg="#2c3e50").pack(side="left")
ai_provider = tk.StringVar(value="Ollama")
for p in ["Ollama", "Groq", "Gemini"]:
    tk.Radiobutton(f_prov, text=p, variable=ai_provider, value=p,
                   command=_on_provider_change, bg="white",
                   font=("Arial", 8), activebackground="white").pack(side="left", padx=3)

f_api = tk.Frame(frame_ai, bg="white")
f_api.pack(fill="x", padx=10, pady=(2, 0))
lbl_api = tk.Label(f_api, text="API Key:", font=("Arial", 8),
                   bg="white", fg="#bdc3c7")
lbl_api.pack(side="left")
entry_api = tk.Entry(f_api, width=22, font=("Arial", 8), relief="solid", bd=1, show="*")
entry_api.pack(side="left", padx=4)
entry_api.config(state="disabled")

f_mod = tk.Frame(frame_ai, bg="white")
f_mod.pack(fill="x", padx=10, pady=(2, 4))
lbl_model = tk.Label(f_mod, text="Modello:", font=("Arial", 8),
                      bg="white", fg="#2c3e50")
lbl_model.pack(side="left")
entry_model = tk.Entry(f_mod, width=16, font=("Arial", 8), relief="solid", bd=1)
entry_model.insert(0, "llama3.2")
entry_model.pack(side="left", padx=4)
tk.Button(f_mod, text="💾", command=_salva_ai_config,
          bg="#ecf0f1", relief="flat", font=("Arial", 8), padx=4).pack(side="left")

chat_box = tk.Text(frame_ai, font=("Arial", 9), relief="solid", bd=1,
                   wrap="word", height=6, state="disabled", bg="#fafafa")
chat_box.pack(fill="both", expand=True, padx=10, pady=(0, 4))

f_msg = tk.Frame(frame_ai, bg="white")
f_msg.pack(fill="x", padx=10, pady=(0, 6))
entry_msg = tk.Entry(f_msg, font=("Arial", 9), relief="solid", bd=1)
entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 4))
entry_msg.bind("<Return>", lambda e: _chiedi_ai())
btn_invia = tk.Button(f_msg, text="Invia", command=_chiedi_ai,
                      bg="#8e44ad", fg="white", font=("Arial", 9, "bold"),
                      relief="flat", padx=8)
btn_invia.pack(side="left")
tk.Button(f_msg, text="🗑", command=_pulisci_chat,
          bg="#ecf0f1", relief="flat", font=("Arial", 9), padx=6).pack(side="left", padx=2)

# carica config AI salvata
_cfg = _carica_ai_config()
ai_provider.set(_cfg.get("provider", "Ollama"))
entry_api.config(state="normal")
entry_api.insert(0, _cfg.get("api_key", ""))
entry_model.delete(0, tk.END)
entry_model.insert(0, _cfg.get("model", "llama3.2"))
_on_provider_change()

# --- INFO PC: frame grafico ---
frame_info = tk.Frame(contenuto, bg="white")
tk.Label(frame_info, text="🖥  Info PC", font=("Arial", 11, "bold"),
         bg="white", fg="#2c3e50").pack(pady=(8, 2))
so       = f"{platform.system()} {platform.release()}"
cpu_name = platform.processor() or platform.machine()
core_fis = psutil.cpu_count(logical=False)
core_log = psutil.cpu_count(logical=True)
tk.Label(frame_info, text=f"OS: {so}", font=("Arial", 8), bg="white", fg="#7f8c8d").pack()
tk.Label(frame_info, text=f"CPU: {cpu_name[:38]}", font=("Arial", 8), bg="white", fg="#7f8c8d").pack()
tk.Label(frame_info, text=f"Core: {core_fis} fisici / {core_log} logici",
         font=("Arial", 8), bg="white", fg="#7f8c8d").pack(pady=(0, 6))

def _riga_metrica(parent, etichetta):
    f = tk.Frame(parent, bg="white")
    f.pack(fill="x", padx=10, pady=1)
    tk.Label(f, text=etichetta, font=("Arial", 8, "bold"),
             bg="white", fg="#2c3e50", width=6, anchor="w").pack(side="left")
    lbl_val = tk.Label(f, text="...", font=("Arial", 8), bg="white", fg="#2c3e50")
    lbl_val.pack(side="left")
    bar_bg = tk.Frame(parent, bg="#ecf0f1", height=7)
    bar_bg.pack(fill="x", padx=10, pady=(0, 3))
    bar_bg.pack_propagate(False)
    bar_fill = tk.Frame(bar_bg, bg="#27ae60", height=7, width=0)
    bar_fill.place(x=0, y=0, relheight=1)
    return lbl_val, bar_fill

lbl_cpu_val,  bar_cpu_fill  = _riga_metrica(frame_info, "CPU")
lbl_ram_val,  bar_ram_fill  = _riga_metrica(frame_info, "RAM")
lbl_disk_val, bar_disk_fill = _riga_metrica(frame_info, "Disco")
f_batt = tk.Frame(frame_info, bg="white")
f_batt.pack(fill="x", padx=10, pady=1)
tk.Label(f_batt, text="Batt.", font=("Arial", 8, "bold"),
         bg="white", fg="#2c3e50", width=6, anchor="w").pack(side="left")
lbl_batt_val = tk.Label(f_batt, text="...", font=("Arial", 8), bg="white", fg="#2c3e50")
lbl_batt_val.pack(side="left")
tk.Label(frame_info, text="aggiornato ogni 2 sec", font=("Arial", 7),
         bg="white", fg="#bdc3c7").pack(pady=(4, 0))

# --- 6. BOTTONI NEL MENU ---
tk.Button(menu, text="Pomodoro",   command=mostra_pomodoro).pack(pady=8, padx=8, fill="x")
tk.Button(menu, text="Note",       command=mostra_note).pack(pady=8, padx=8, fill="x")
tk.Button(menu, text="AI",         command=mostra_ai).pack(pady=8, padx=8, fill="x")
tk.Button(menu, text="Link",       command=mostra_link).pack(pady=8, padx=8, fill="x")
tk.Button(menu, text="To do list", command=mostra_promemoria).pack(pady=8, padx=8, fill="x")
tk.Button(menu, text="Info",       command=mostra_info).pack(pady=8, padx=8, fill="x")

root.mainloop()
