import tkinter as tk
import webbrowser
import json
import os
import platform
import psutil

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

# --- INFO PC: logica ---
info_update_id = None

def _colore_percentuale(val):
    if val < 50:
        return "#27ae60"   # verde
    elif val < 80:
        return "#f39c12"   # arancione
    else:
        return "#e74c3c"   # rosso

def _barra(parent, valore, colore):
    """Disegna una barra orizzontale proporzionale al valore (0-100)."""
    canvas = tk.Canvas(parent, height=8, bg="#ecf0f1",
                       highlightthickness=0, relief="flat")
    canvas.pack(fill="x", padx=10, pady=(0, 4))
    # disegna la barra dopo che il widget è visibile
    def _draw(event=None):
        w = canvas.winfo_width()
        canvas.delete("all")
        canvas.create_rectangle(0, 0, int(w * valore / 100), 8,
                                 fill=colore, outline="")
    canvas.bind("<Configure>", _draw)
    return canvas

def _aggiorna_info():
    global info_update_id

    # CPU
    cpu = psutil.cpu_percent(interval=None)
    c_cpu = _colore_percentuale(cpu)
    lbl_cpu_val.config(text=f"{cpu:.1f}%", fg=c_cpu)
    bar_cpu_fill.config(width=int(180 * cpu / 100), bg=c_cpu)

    # RAM
    ram = psutil.virtual_memory()
    ram_pct = ram.percent
    ram_used = ram.used / 1024**3
    ram_tot  = ram.total / 1024**3
    c_ram = _colore_percentuale(ram_pct)
    lbl_ram_val.config(text=f"{ram_used:.1f} / {ram_tot:.1f} GB  ({ram_pct:.0f}%)", fg=c_ram)
    bar_ram_fill.config(width=int(180 * ram_pct / 100), bg=c_ram)

    # DISCO
    disk = psutil.disk_usage("/")
    disk_pct = disk.percent
    disk_used = disk.used / 1024**3
    disk_tot  = disk.total / 1024**3
    c_disk = _colore_percentuale(disk_pct)
    lbl_disk_val.config(text=f"{disk_used:.1f} / {disk_tot:.1f} GB  ({disk_pct:.0f}%)", fg=c_disk)
    bar_disk_fill.config(width=int(180 * disk_pct / 100), bg=c_disk)

    # BATTERIA
    batt = psutil.sensors_battery()
    if batt:
        stato = "🔌" if batt.power_plugged else "🔋"
        lbl_batt_val.config(text=f"{stato}  {batt.percent:.0f}%",
                            fg=_colore_percentuale(100 - batt.percent))
    else:
        lbl_batt_val.config(text="N/D", fg="#7f8c8d")

    info_update_id = root.after(2000, _aggiorna_info)  # aggiorna ogni 2 secondi

def _stop_info_update():
    global info_update_id
    if info_update_id:
        root.after_cancel(info_update_id)
        info_update_id = None

# --- 1. COSA SUCCEDE QUANDO PREMI I TASTI ---
def mostra_pomodoro():
    _stop_info_update()
    frame_link.pack_forget()
    frame_note.pack_forget()
    frame_info.pack_forget()
    label_titolo.pack_forget()
    label_info.pack_forget()
    frame_pomodoro.pack(expand=True, fill="both")

def mostra_note():
    _stop_info_update()
    frame_pomodoro.pack_forget()
    frame_link.pack_forget()
    frame_info.pack_forget()
    label_titolo.pack_forget()
    label_info.pack_forget()
    frame_note.pack(expand=True, fill="both")

def mostra_ai():
    _stop_info_update()
    frame_pomodoro.pack_forget()
    frame_link.pack_forget()
    frame_note.pack_forget()
    frame_info.pack_forget()
    label_titolo.pack(pady=20)
    label_info.pack()
    label_titolo.config(text="Sei nell'ai")
    label_info.config(text="Qui parlerai con l'intelligenza artificiale.")

def mostra_link():
    _stop_info_update()
    frame_pomodoro.pack_forget()
    frame_note.pack_forget()
    frame_info.pack_forget()
    label_titolo.pack_forget()
    label_info.pack_forget()
    frame_link.pack(expand=True, fill="both")
    _aggiorna_lista()

def mostra_info():
    frame_pomodoro.pack_forget()
    frame_link.pack_forget()
    frame_note.pack_forget()
    label_titolo.pack_forget()
    label_info.pack_forget()
    frame_info.pack(expand=True, fill="both")
    _aggiorna_info()

# --- 2. CREAZIONE FINESTRA ---
root = tk.Tk()
root.title("DESK APP")
root.geometry("350x250")
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

entry_link = tk.Entry(frame_input, width=22, font=("Arial", 9),
                      relief="solid", bd=1)
entry_link.pack(side="left", padx=(0, 4))

tk.Button(frame_input, text="+ Aggiungi", command=_aggiungi_link,
          bg="#3498db", fg="white", relief="flat",
          font=("Arial", 9, "bold"), padx=8, pady=3).pack(side="left")

frame_lista = tk.Frame(frame_link, bg="white")
frame_lista.pack(fill="both", expand=True, padx=10, pady=8)

# --- INFO PC: frame grafico ---
frame_info = tk.Frame(contenuto, bg="white")

tk.Label(frame_info, text="🖥  Info PC", font=("Arial", 11, "bold"),
         bg="white", fg="#2c3e50").pack(pady=(8, 2))

# Info statiche (sistema operativo, CPU nome, core)
so   = f"{platform.system()} {platform.release()}"
cpu_name  = platform.processor() or platform.machine()
core_fis  = psutil.cpu_count(logical=False)
core_log  = psutil.cpu_count(logical=True)

tk.Label(frame_info, text=f"OS: {so}", font=("Arial", 8),
         bg="white", fg="#7f8c8d").pack()
tk.Label(frame_info, text=f"CPU: {cpu_name[:38]}",
         font=("Arial", 8), bg="white", fg="#7f8c8d").pack()
tk.Label(frame_info, text=f"Core: {core_fis} fisici  /  {core_log} logici",
         font=("Arial", 8), bg="white", fg="#7f8c8d").pack(pady=(0, 6))

def _riga_metrica(parent, etichetta):
    """Crea una riga con label etichetta, label valore e barra."""
    f = tk.Frame(parent, bg="white")
    f.pack(fill="x", padx=10, pady=1)
    tk.Label(f, text=etichetta, font=("Arial", 8, "bold"),
             bg="white", fg="#2c3e50", width=6, anchor="w").pack(side="left")
    lbl_val = tk.Label(f, text="...", font=("Arial", 8),
                       bg="white", fg="#2c3e50")
    lbl_val.pack(side="left")

    # barra contenitore + barra riempimento
    bar_bg = tk.Frame(parent, bg="#ecf0f1", height=7)
    bar_bg.pack(fill="x", padx=10, pady=(0, 3))
    bar_bg.pack_propagate(False)
    bar_fill = tk.Frame(bar_bg, bg="#27ae60", height=7, width=0)
    bar_fill.place(x=0, y=0, relheight=1)

    return lbl_val, bar_fill

lbl_cpu_val,  bar_cpu_fill  = _riga_metrica(frame_info, "CPU")
lbl_ram_val,  bar_ram_fill  = _riga_metrica(frame_info, "RAM")
lbl_disk_val, bar_disk_fill = _riga_metrica(frame_info, "Disco")

# batteria (solo valore, niente barra)
f_batt = tk.Frame(frame_info, bg="white")
f_batt.pack(fill="x", padx=10, pady=1)
tk.Label(f_batt, text="Batt.", font=("Arial", 8, "bold"),
         bg="white", fg="#2c3e50", width=6, anchor="w").pack(side="left")
lbl_batt_val = tk.Label(f_batt, text="...", font=("Arial", 8),
                         bg="white", fg="#2c3e50")
lbl_batt_val.pack(side="left")

tk.Label(frame_info, text="aggiornato ogni 2 sec", font=("Arial", 7),
         bg="white", fg="#bdc3c7").pack(pady=(4, 0))

# --- 6. BOTTONI NEL MENU ---
tk.Button(menu, text="Pomodoro", command=mostra_pomodoro).pack(pady=10, padx=10, fill="x")
tk.Button(menu, text="Note",     command=mostra_note).pack(pady=10, padx=10, fill="x")
tk.Button(menu, text="AI",       command=mostra_ai).pack(pady=10, padx=10, fill="x")
tk.Button(menu, text="Link",     command=mostra_link).pack(pady=10, padx=10, fill="x")
tk.Button(menu, text="Info",     command=mostra_info).pack(pady=10, padx=10, fill="x")

root.mainloop()