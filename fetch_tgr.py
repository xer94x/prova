#!/usr/bin/env python3
"""
Recupera l'ultima puntata TGR Sicilia da RaiPlay e genera un file M3U.
Viene eseguito automaticamente da GitHub Actions ogni giorno.
"""

import json
import urllib.request
import urllib.error
import sys
import os
from datetime import datetime

# URL API RaiPlay per TGR Sicilia
# Il ContentSet è l'identificatore della serie TGR Sicilia
API_URL = (
    "https://www.raiplay.it/atomium/v2/page/programmi/informazione-e-approfondimento/"
    "tgr-sicilia.json"
)

# Fallback: ricerca diretta
SEARCH_URL = "https://www.raiplay.it/atomium/v2/search?q=tgr+sicilia&type=Video&limit=5"

M3U_OUTPUT = "tgr_sicilia.m3u"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; TGR-Fetcher/1.0)"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_stream_url(video_url_path: str) -> str | None:
    """Dato il path RaiPlay di un video, restituisce l'URL dello stream .m3u8."""
    api = f"https://www.raiplay.it{video_url_path.replace('.html', '.json')}"
    try:
        data = fetch_json(api)
        # Il campo video contiene i content_url
        video = data.get("video", {})
        stream = (
            video.get("content_url")
            or video.get("url")
            or (video.get("streams") or [{}])[0].get("url")
        )
        return stream
    except Exception as e:
        print(f"  Errore nel recupero stream: {e}", file=sys.stderr)
        return None


def get_latest_episode() -> dict | None:
    """Restituisce info sull'ultima puntata: titolo, data, stream_url."""

    # Strategia 1: pagina programma TGR Sicilia
    try:
        print("Tentativo 1: pagina programma RaiPlay...")
        data = fetch_json(API_URL)

        # Naviga la struttura JSON di RaiPlay
        blocks = data.get("blocks", [])
        for block in blocks:
            sets = block.get("sets", [])
            for s in sets:
                items = s.get("items", [])
                if items:
                    item = items[0]  # primo = più recente
                    title = item.get("name") or item.get("tit_eventbrand_string", "TGR Sicilia")
                    date_str = item.get("date") or item.get("ora_pubblicazione", "")
                    path = item.get("weblink") or item.get("path_id", "")
                    if path:
                        stream = find_stream_url(path)
                        if stream:
                            return {
                                "title": title,
                                "date": date_str,
                                "stream_url": stream,
                                "info_url": f"https://www.raiplay.it{path}",
                            }
    except Exception as e:
        print(f"  Strategia 1 fallita: {e}", file=sys.stderr)

    # Strategia 2: ricerca full-text
    try:
        print("Tentativo 2: ricerca RaiPlay...")
        data = fetch_json(SEARCH_URL)
        results = data.get("items") or data.get("results") or []
        for item in results:
            path = item.get("weblink") or item.get("path_id", "")
            if "tgr" in path.lower() and "sicilia" in (
                item.get("name", "") + path
            ).lower():
                stream = find_stream_url(path)
                if stream:
                    return {
                        "title": item.get("name", "TGR Sicilia"),
                        "date": item.get("date", ""),
                        "stream_url": stream,
                        "info_url": f"https://www.raiplay.it{path}",
                    }
    except Exception as e:
        print(f"  Strategia 2 fallita: {e}", file=sys.stderr)

    return None


def write_m3u(episode: dict) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    title = episode["title"]
    if episode.get("date"):
        title += f" ({episode['date']})"

    content = (
        "#EXTM3U\n"
        f"# Aggiornato: {now}\n"
        "#EXTINF:-1"
        f' tvg-id="TGR-Sicilia"'
        f' tvg-name="TGR Sicilia"'
        f' tvg-logo="https://www.raiplay.it/contentset/TgrSicilia-TGRSicilia.png"'
        f' group-title="RAI",'
        f"{title}\n"
        f"{episode['stream_url']}\n"
    )

    with open(M3U_OUTPUT, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n✅ {M3U_OUTPUT} aggiornato:")
    print(f"   Titolo : {title}")
    print(f"   Stream : {episode['stream_url']}")
    print(f"   Pagina : {episode.get('info_url', '')}")


def main():
    print("=== TGR Sicilia fetcher ===")
    episode = get_latest_episode()

    if not episode:
        print("\n❌ Impossibile trovare l'ultima puntata.", file=sys.stderr)
        # Mantieni il file precedente se esiste, altrimenti esci con errore
        if not os.path.exists(M3U_OUTPUT):
            sys.exit(1)
        print("   Mantengo il file M3U precedente.")
        return

    write_m3u(episode)


if __name__ == "__main__":
    main()
