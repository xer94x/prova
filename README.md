# 📺 TGR Sicilia → Kodi

Aggiorna automaticamente un file M3U con l'ultima puntata del TGR Sicilia da RaiPlay.

## Come funziona

```
GitHub Actions (3 volte al giorno)
    │
    ▼
fetch_tgr.py interroga l'API RaiPlay
    │
    ▼
Sovrascrive tgr_sicilia.m3u
    │
    ▼
URL fisso → Kodi riproduce sempre l'ultima puntata
```

## Setup (una volta sola)

### 1. Crea il repository su GitHub
- Vai su [github.com/new](https://github.com/new)
- Nome: `tgr` (o quello che vuoi)
- Visibilità: **Public** (necessario per l'URL raw gratuito)
- Clicca "Create repository"

### 2. Carica i file
Carica in questo ordine nella root del repository:
- `fetch_tgr.py`
- `tgr_sicilia.m3u`
- La cartella `.github/workflows/update_tgr.yml`

### 3. Lancia il workflow la prima volta
- Vai su **Actions** → "Aggiorna TGR Sicilia" → **Run workflow**
- Aspetta ~30 secondi: il file M3U verrà aggiornato con lo stream reale

### 4. Configura Kodi
In Kodi, installa **PVR IPTV Simple Client** e imposta:

| Campo | Valore |
|-------|--------|
| Location | Remote path (URL) |
| M3U Play List URL | `https://raw.githubusercontent.com/TUO-UTENTE/tgr/main/tgr_sicilia.m3u` |
| Refresh interval | 60 minuti |

Sostituisci `TUO-UTENTE` con il tuo username GitHub.

---

## Aggiornamenti automatici

Il workflow gira **2 volte al giorno**:
- 14:30 ora italiana  
- 20:05 ora italiana

Puoi anche lanciarlo manualmente da GitHub > Actions in qualsiasi momento.

## Troubleshooting

**Il file M3U mostra ancora il placeholder?**
→ Vai su Actions e lancia manualmente il workflow.

**Kodi non riproduce il video?**
→ L'URL `.m3u8` di RaiPlay richiede a volte un User-Agent compatibile.
   In Kodi, nelle impostazioni del client, prova ad aggiungere:
   `User-Agent=Mozilla/5.0 (compatible; IPTV/1.0)`

**GitHub Actions fallisce?**
→ Controlla il log su Actions. L'API RaiPlay cambia struttura occasionalmente —
   apri una Issue o aggiorna `fetch_tgr.py` con il nuovo path JSON.
