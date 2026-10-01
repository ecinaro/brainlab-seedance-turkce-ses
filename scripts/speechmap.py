"""speechmap — Türkçe konuşma kaydını Seedance diyalog prompt'una hazırlar.

Ses (ya da video) dosyasını alır:
  1. Whisper (Groq, yoksa OpenAI) ile kelime zamanlı Türkçe döküm
  2. librosa ile prozodi: perde, enerji, konuşma hızı, duraklamalar, uzatılan kelimeler
  3. Türkçe telaffuz işaretleri: yumuşak ğ, "şey", konuşma dili kısaltmaları, ı/i, soru eki
  4. Olası konuşmacı değişimleri (perde sıçraması + uzun boşluk)

Çıktı: <out>/report.md ve <out>/analysis.json

Kullanım:
  python speechmap.py "<dosya>" --out "<dizin>" [--start 0:05 --end 0:35]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

CONFIG_FILE = Path.home() / ".config" / "brainwatch" / ".env"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_MODEL = "whisper-large-v3"
OPENAI_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"
OPENAI_MODEL = "whisper-1"

VOWELS = set("aeıioöuüâîûAEIİOÖUÜÂÎÛ")

# konuşma dili biçimi -> yazı dili karşılığı (döküm bunları yakalarsa işaretlenir)
COLLOQUIAL = {
    "napıyosun": "ne yapıyorsun", "napıyon": "ne yapıyorsun", "napcan": "ne yapacaksın",
    "naber": "ne haber", "nolur": "ne olur", "noldu": "ne oldu", "nası": "nasıl",
    "bi": "bir", "bişey": "bir şey", "bişi": "bir şey", "hiçbişey": "hiçbir şey",
    "geliyom": "geliyorum", "gidiyom": "gidiyorum", "biliyom": "biliyorum",
    "bilmiyom": "bilmiyorum", "diyom": "diyorum", "yapıcam": "yapacağım",
    "gelcem": "geleceğim", "gidicem": "gideceğim", "edicem": "edeceğim",
    "yani": "yani", "işte": "işte", "abi": "ağabey", "valla": "vallahi",
    "tamam mı": "tamam mı", "di mi": "değil mi", "dimi": "değil mi",
    "mıyım": "miyim", "şimdi": "şimdi", "şeyy": "şey",
}
FILLERS = {"şey", "yani", "işte", "hani", "ee", "eee", "ıı", "ııı", "hmm", "aa", "valla", "ya"}
Q_PARTICLES = re.compile(r"^(mı|mi|mu|mü)(yım|yim|yum|yüm|sın|sin|sun|sün|yız|yiz|yuz|yüz|sınız|siniz|sunuz|sünüz|dır|dir|dur|dür)?$")


def log(msg: str) -> None:
    print(f"[speechmap] {msg}", file=sys.stderr, flush=True)


def read_env_key(name: str) -> str | None:
    if not CONFIG_FILE.is_file():
        return None
    for line in CONFIG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith(f"{name}="):
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            return v or None
    return None


def parse_time(t: str | None) -> float | None:
    if not t:
        return None
    parts = [float(p) for p in t.split(":")]
    s = 0.0
    for p in parts:
        s = s * 60 + p
    return s


def fmt(t: float) -> str:
    m, s = divmod(max(t, 0.0), 60)
    return f"{int(m)}:{s:05.2f}"


# ---------------------------------------------------------------- ses hazırlığı
def prepare_audio(src: Path, work: Path, start: float | None, end: float | None) -> tuple[Path, Path]:
    """16 kHz mono wav (analiz) + mp3 (Whisper) üretir."""
    wav = work / "speech.wav"
    mp3 = work / "speech.mp3"
    if not shutil.which("ffmpeg"):
        log("ffmpeg yok — librosa ile okunuyor (mp3/m4a/video başarısız olabilir)")
        import librosa
        import soundfile as sf
        y, sr = librosa.load(str(src), sr=16000, mono=True, offset=start or 0.0,
                             duration=(end - (start or 0.0)) if end else None)
        sf.write(str(wav), y, sr)
        return wav, wav
    cut = []
    if start is not None:
        cut += ["-ss", str(start)]
    if end is not None:
        cut += ["-to", str(end)]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *cut, "-i", str(src),
                    "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                    "-b:a", "96k", str(mp3)], check=True)
    return wav, mp3


# ---------------------------------------------------------------- döküm
def transcribe(audio: Path) -> dict | None:
    backends = [
        ("groq", GROQ_ENDPOINT, GROQ_MODEL, read_env_key("GROQ_API_KEY")),
        ("openai", OPENAI_ENDPOINT, OPENAI_MODEL, read_env_key("OPENAI_API_KEY")),
    ]
    backends = [b for b in backends if b[3]]
    if not backends:
        log("Whisper anahtarı yok — döküm atlandı")
        return None
    for backend, endpoint, model, key in backends:
        data = _whisper_call(audio, backend, endpoint, model, key)
        if data:
            return data
    return None


def _whisper_call(audio: Path, backend: str, endpoint: str, model: str, key: str) -> dict | None:
    log(f"döküm ({backend})…")
    boundary = "----speechmap"
    parts: list[bytes] = []

    def field(n: str, v: str) -> None:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n".encode())

    field("model", model)
    field("language", "tr")
    field("response_format", "verbose_json")
    # konuşma dilini düzeltmeden yazması için ipucu
    field("prompt", "Şey... napıyosun ya, bi dakka. Geliyom işte, di mi? Değil mi abi?")
    field("timestamp_granularities[]", "word")
    field("timestamp_granularities[]", "segment")
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{audio.name}\"\r\n"
        f"Content-Type: application/octet-stream\r\n\r\n".encode()
    )
    parts.append(audio.read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(endpoint, data=b"".join(parts), headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "User-Agent": "speechmap/1.0 (+brainlab)",
    })
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        log(f"döküm başarısız: HTTP {e.code} {e.read()[:300]!r}")
        return None
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        log(f"döküm başarısız: {e}")
        return None
    data["_backend"] = backend
    return data


# ---------------------------------------------------------------- prozodi
def prosody(wav: Path):
    import librosa
    import numpy as np

    y, sr = librosa.load(str(wav), sr=16000, mono=True)
    hop = 160  # 10 ms
    f0 = librosa.yin(y, fmin=65, fmax=500, sr=sr, frame_length=1024, hop_length=hop)
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0]
    n = min(len(f0), len(rms))
    f0, rms = f0[:n], rms[:n]
    db = 20 * np.log10(rms + 1e-9)
    voiced_gate = db > (np.percentile(db, 95) - 30)
    f0 = np.where(voiced_gate, f0, np.nan)
    times = np.arange(n) * hop / sr
    return {"y": y, "sr": sr, "f0": f0, "db": db, "t": times, "dur": len(y) / sr}


def window_stats(p: dict, a: float, b: float) -> dict:
    import numpy as np

    m = (p["t"] >= a) & (p["t"] < b)
    f0 = p["f0"][m]
    db = p["db"][m]
    f0v = f0[~np.isnan(f0)]
    out = {"pitch_hz": None, "pitch_range_st": None, "loud_db": None, "end_contour": None}
    if len(db):
        out["loud_db"] = round(float(np.percentile(db, 90)), 1)
    if len(f0v) >= 5:
        med = float(np.median(f0v))
        lo, hi = np.percentile(f0v, [10, 90])
        out["pitch_hz"] = round(med)
        out["pitch_range_st"] = round(float(12 * np.log2(hi / lo)), 1)
        # son %25 ile önceki kısmın karşılaştırması -> cümle sonu ezgisi
        k = max(3, len(f0v) // 4)
        tail, body = np.median(f0v[-k:]), np.median(f0v[:-k]) if len(f0v) > k else med
        st = 12 * np.log2(tail / body)
        out["end_contour"] = "yükselen ↗" if st > 1.5 else ("düşen ↘" if st < -1.5 else "düz →")
    return out


# ---------------------------------------------------------------- yardımcılar
def syllables(word: str) -> int:
    return max(1, sum(1 for c in word if c in VOWELS))


def clean(word: str) -> str:
    return re.sub(r"[^\wçğıöşüâîûÇĞİÖŞÜ']", "", word.lower().replace("İ", "i").replace("I", "ı"))


def register(hz: float | None) -> str:
    if not hz:
        return "?"
    if hz < 120:
        return "kalın / pes"
    if hz < 170:
        return "orta-kalın"
    if hz < 220:
        return "orta-ince"
    return "ince / tiz"


def rate_label(sps: float) -> str:
    if sps < 3.5:
        return "yavaş"
    if sps < 5.0:
        return "sakin"
    if sps < 6.5:
        return "doğal"
    return "hızlı"


def loud_label(db: float | None, ref: float) -> str:
    if db is None:
        return "?"
    d = db - ref
    if d > 2:
        return "yüksek / vurgulu"
    if d < -8:
        return "alçak / fısıltıya yakın"
    if d < -4:
        return "yumuşak"
    return "normal"


# ---------------------------------------------------------------- ana analiz
def analyse(src: Path, out: Path, start: float | None, end: float | None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    wav, mp3 = prepare_audio(src, out, start, end)
    log("prozodi ölçülüyor…")
    p = prosody(wav)
    tr = transcribe(mp3)

    import numpy as np

    all_db = p["db"][p["db"] > np.percentile(p["db"], 95) - 30]
    ref_db = float(np.percentile(all_db, 90)) if len(all_db) else -20.0  # window_stats ile aynı ölçü
    f0v = p["f0"][~np.isnan(p["f0"])]
    overall = {
        "duration_s": round(p["dur"], 2),
        "pitch_hz": round(float(np.median(f0v))) if len(f0v) else None,
        "pitch_range_st": round(float(12 * np.log2(np.percentile(f0v, 90) / np.percentile(f0v, 10))), 1) if len(f0v) > 10 else None,
    }
    overall["register"] = register(overall["pitch_hz"])

    words = []
    if tr:
        for w in tr.get("words") or []:
            words.append({"w": w.get("word", "").strip(), "s": float(w.get("start", 0)), "e": float(w.get("end", 0))})

    # kelime düzeyi: uzatma + duraklama
    stretched, pauses = [], []
    for i, w in enumerate(words):
        d = w["e"] - w["s"]
        syl = syllables(clean(w["w"]))
        if d / syl > 0.38 and d > 0.45:
            stretched.append({"word": w["w"], "t": round(w["s"], 2), "dur": round(d, 2)})
        if i and w["s"] - words[i - 1]["e"] >= 0.35:
            pauses.append({"after": words[i - 1]["w"], "t": round(words[i - 1]["e"], 2),
                           "len": round(w["s"] - words[i - 1]["e"], 2)})

    # segment düzeyi
    segs = []
    src_segs = (tr or {}).get("segments") or []
    if not src_segs and words:
        src_segs = [{"start": words[0]["s"], "end": words[-1]["e"], "text": " ".join(w["w"] for w in words)}]
    if not src_segs:
        # döküm yok: sessizliğe göre böl
        import librosa
        iv = librosa.effects.split(p["y"], top_db=32, frame_length=1024, hop_length=160)
        for a, b in iv:
            a, b = a / p["sr"], b / p["sr"]
            if src_segs and a - src_segs[-1]["end"] < 0.35:
                src_segs[-1]["end"] = b
            elif b - a > 0.15:
                src_segs.append({"start": a, "end": b, "text": ""})
        src_segs = src_segs or [{"start": 0.0, "end": p["dur"], "text": ""}]
    prev_hz = None
    for sg in src_segs:
        a, b = float(sg["start"]), float(sg["end"])
        text = (sg.get("text") or "").strip()
        st = window_stats(p, a, b)
        seg_words = [w for w in words if a - 0.05 <= w["s"] < b]
        syl = sum(syllables(clean(w["w"])) for w in seg_words) or sum(syllables(clean(t)) for t in text.split())
        speak = sum(w["e"] - w["s"] for w in seg_words) or max(b - a, 0.1)
        sps = syl / speak if speak else 0
        change = bool(prev_hz and st["pitch_hz"] and abs(12 * np.log2(st["pitch_hz"] / prev_hz)) > 4)
        segs.append({
            "start": round(a, 2), "end": round(b, 2), "text": text,
            "syl_per_s": round(sps, 1), "rate": rate_label(sps),
            "pitch_hz": st["pitch_hz"], "register": register(st["pitch_hz"]),
            "pitch_range_st": st["pitch_range_st"], "end_contour": st["end_contour"],
            "loudness": loud_label(st["loud_db"], ref_db),
            "possible_speaker_change": change,
        })
        if st["pitch_hz"]:
            prev_hz = st["pitch_hz"]

    # Türkçe işaretler
    tokens = [clean(w["w"]) for w in words] or [clean(t) for s in segs for t in s["text"].split()]
    full_text = " ".join(s["text"] for s in segs)
    marks = {
        "soft_g": sorted({t for t in tokens if "ğ" in t}),
        "fillers": sorted({t for t in tokens if t in FILLERS or re.fullmatch(r"(e+|ı+|a+|ş+e+y+)", t or "")}),
        "colloquial": sorted({f"{t} (= {COLLOQUIAL[t]})" for t in tokens if t in COLLOQUIAL and COLLOQUIAL[t] != t}),
        "dotless_i": sorted({t for t in tokens if "ı" in t})[:25],
        "question_particles": sorted({t for t in tokens if Q_PARTICLES.match(t or "")}),
        "circumflex": sorted({t for t in tokens if re.search("[âîû]", t)}),
        "many_a": sorted({t for t in tokens if t.count("a") >= 2 or ("a" in t and len(t) >= 6)}),
        "letter_j": sorted({t for t in tokens if "j" in t}),
        "letter_ç_ş": sorted({t for t in tokens if re.search("[çş]", t)}),
        "letter_ö_ü": sorted({t for t in tokens if re.search("[öü]", t)}),
        "double_consonant": sorted({t for t in tokens if re.search(r"([bcçdfghjklmnprsştvyz])\1", t)}),
    }

    result = {
        "source": str(src), "clip": [start, end], "overall": overall,
        "transcript_backend": (tr or {}).get("_backend"),
        "text": full_text, "segments": segs, "pauses": pauses,
        "stretched_words": stretched, "turkish_marks": marks,
        "words": [{"w": w["w"], "s": round(w["s"], 2), "e": round(w["e"], 2)} for w in words][:600],
    }
    (out / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "report.md").write_text(render_report(result), encoding="utf-8")
    return result


def render_report(r: dict) -> str:
    o = r["overall"]
    L = ["# speechmap raporu", "",
         f"- Kaynak: `{r['source']}`",
         f"- Süre: {o['duration_s']} sn · Medyan perde: {o['pitch_hz']} Hz ({o['register']}) · Perde aralığı: {o['pitch_range_st']} yarım ton",
         f"- Döküm: {r['transcript_backend'] or 'YOK (Whisper anahtarı yok ya da hata)'}",
         "", "## Döküm", "", r["text"] or "_(döküm yok)_", "",
         "## Segmentler", "",
         "| # | Zaman | Metin | Hız (hece/sn) | Perde | Ses | Cümle sonu | Konuşmacı? |",
         "|---|---|---|---|---|---|---|---|"]
    for i, s in enumerate(r["segments"], 1):
        L.append(f"| {i} | {fmt(s['start'])}–{fmt(s['end'])} | {s['text']} | {s['syl_per_s']} ({s['rate']}) | "
                 f"{s['pitch_hz'] or '?'} Hz {s['register']} · aralık {s['pitch_range_st'] or '?'} st | {s['loudness']} | "
                 f"{s['end_contour'] or '?'} | {'⚠ değişim olabilir' if s['possible_speaker_change'] else ''} |")
    L += ["", "## Duraklamalar (≥0.35 sn)", ""]
    L += [f"- {fmt(x['t'])} — \"{x['after']}\" sonrası {x['len']} sn" for x in r["pauses"]] or ["- yok"]
    L += ["", "## Uzatılan kelimeler", ""]
    L += [f"- {fmt(x['t'])} — \"{x['word']}\" ({x['dur']} sn)" for x in r["stretched_words"]] or ["- yok"]
    m = r["turkish_marks"]
    L += ["", "## Türkçe telaffuz işaretleri", "",
          f"- a riski olan kelimeler (a = kısa açık \"a\", İngilizce æ/ey değil): {', '.join(m['many_a']) or '—'}",
          f"- j (= \"zh\", her zaman not): {', '.join(m['letter_j']) or '—'}",
          f"- ç / ş: {', '.join(m['letter_ç_ş']) or '—'}",
          f"- ö / ü: {', '.join(m['letter_ö_ü']) or '—'}",
          f"- Çift ünsüz: {', '.join(m['double_consonant']) or '—'}",
          f"- Yumuşak ğ (asla \"g\", her zaman not): {', '.join(m['soft_g']) or '—'}",
          f"- Dolgu / tereddüt: {', '.join(m['fillers']) or '—'}",
          f"- Konuşma dili biçimleri: {', '.join(m['colloquial']) or '—'}",
          f"- Soru ekleri: {', '.join(m['question_particles']) or '—'}",
          f"- Şapkalı ünlü: {', '.join(m['circumflex']) or '—'}",
          f"- ı içeren kelimeler (ilk 25): {', '.join(m['dotless_i']) or '—'}",
          "", "_Not: Ölçümler sinyal tabanlıdır. Konuşmacı ayrımı tahmindir; perde sıçraması + boşluk birlikte değerlendirilmeli._"]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("--out", default="speechmap-out")
    ap.add_argument("--start")
    ap.add_argument("--end")
    a = ap.parse_args()
    src = Path(a.source)
    if not src.is_file():
        sys.exit(f"[speechmap] dosya bulunamadı: {src}")
    r = analyse(src, Path(a.out), parse_time(a.start), parse_time(a.end))
    log(f"bitti → {Path(a.out) / 'report.md'}")
    print(Path(a.out, "report.md").read_text(encoding="utf-8"))
    if not r["transcript_backend"]:
        print("\nUYARI: döküm alınamadı — sadece prozodi ölçüldü.")


if __name__ == "__main__":
    main()
