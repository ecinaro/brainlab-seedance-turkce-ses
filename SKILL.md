---
name: brainlab-seedance-turkce-ses
description: Seedance 2.5 videolarında karakterlerin Türkçeyi doğal konuşması için diyalog + telaffuz katmanı kurar. Türkçe diyaloğu yazar ve modelin yanlış okuyacağı yerleri — Türkçe harfler ve saf ünlüler (a İngilizce "æ"/"ey" gibi okunmaz, j = "zh", ç, ş, ö, ü, ı), çift ünsüz, yumuşak ğ ("değil" → "deyil"), dolgu "şey" ("şeeey"), konuşma dili kısaltmaları (napıyosun, bi, geliyom), ı/i farkı, vurgu istisnaları (AN-ka-ra), soru ezgisi — prompt'un içine konuşmacı bazlı İngilizce telaffuz notu olarak gömer. İki girişi var. METİN modu bir fikir/sahne/diyalogdan prompt kurar. SES modu paylaşılan ses ya da video dosyasını analiz eder (döküm + konuşma hızı, perde, duraklama, uzatılan kelimeler, cümle sonu ezgisi) ve o konuşmayı yeniden üreten Seedance prompt'una çevirir. sd25-pe / seedance-prompter ile birlikte çalışır. MUTLAKA tetikle. "seedance türkçe", "türkçe konuşan video", "türkçe diyalog prompt", "karakter türkçe konuşsun", "türkçe telaffuz", "yumuşak g", "şey nasıl okunur", "dudak senkronu türkçe", "bu sesi prompt'a çevir", "bu ses kaydını analiz et", "bu konuşmayı seedance'e aktar", "ses dosyasından prompt" dendiğinde ya da kullanıcı Seedance için Türkçe konuşmalı sahne istediğinde veya bir ses/video kaydı paylaşıp video prompt'u istediğinde.
---

# BR(AI)N Lab — Seedance Türkçe Ses Katmanı

Seedance konuşmayı kendisi seslendirir ama Türkçeyi yabancı birinin okuduğu gibi okur: "değil"i "de-ğil", "şey"i kısa ve kesik, "geliyorum"u kimsenin konuşmadığı tam haliyle. Bu skill diyaloğu **yazar ve okunuşunu yönetir.**

**İş bölümü:**
- **Bu skill:** diyalog, söyleyiş (delivery), telaffuz notları, ses referansı bağlama.
- **`sd25-pe`:** görsel kurgu, çoklu referans, keyframe, edit/extend görevleri. Sahne karmaşıksa (referans görseller, çok aşamalı kurgu, video düzenleme) `sd25-pe`'nin yapısını izle ve bu skill'in katmanını her aşamaya yerleştir. Basit konuşma sahnesinde prompt'u tek başına kur.

**Kilitli kararlar:**
1. Prompt **İngilizce**, `{}` içindeki diyalog **Türkçe**.
2. **Konuşma dili kısaltmaları** (napıyosun, bi, geliyom, di mi) dudak senkronu birebir eşleşsin diye **doğrudan `{}` içine** yazılır. Yumuşak ğ, "şey" uzatması, vurgu ve ezgi gibi şeyler **doğru yazımda kalır**, konuşmacının altına telaffuz notu olarak verilir.
3. Kullanıcı resmî / spiker dili isterse kısaltma yapılmaz.

Telaffuz kurallarının tamamı: `references/turkce-telaffuz.md`. **Her çalıştırmada oku.**

---

## MOD SEÇİMİ

| Kullanıcı ne verdi | Mod |
|---|---|
| Fikir, sahne tarifi, hazır diyalog | **METİN** |
| Ses dosyası (.mp3 .wav .m4a .ogg) ya da konuşmalı video dosyası | **SES** |
| Hazır bir Seedance prompt'u + "Türkçe konuşsun" | **KATMAN** — mevcut prompt'u koru, sadece diyalog dilini, telaffuz notlarını ve dinleyici kurallarını ekle |

---

## METİN MODU

1. **Brief:** Eksik olanı tek mesajda sor, gerisini varsay. Kim konuşuyor (kaç kişi, yaş, ses), nerede, ne kadar sürecek, resmî mi gündelik mi, ağız/bölge var mı? Varsayılan: gündelik İstanbul Türkçesi, 1–2 konuşmacı, tek üretim (~10 sn).
2. **Diyaloğu yaz:** Kısa replikler. Seedance'te ağız ancak **saniyede yaklaşık 2–3 kelime** ile senkron kalır; replikleri aşamanın süresine sığdır. Gündelik konuşmada kısaltmaları doğrudan yaz.
3. **Telaffuz taraması:** Her replikte `references/turkce-telaffuz.md`'deki tuzakları ara: Türkçe harfler (**j** = "zh" ve **ğ** = asla "g" değil, her zaman; **a** = kısa açık "a", İngilizce "æ"/"ey" değil — çok a'lı ya da İngilizceye benzeyen kelimelerde; ç, ş, ö, ü, ı, â gerektiğinde; **c'ye not düşme**; kelimeyi başka harflerle yeniden heceleme), çift ünsüz, ğ, şey ve diğer dolgular, kısaltmalar, vurgu istisnaları, soru eki, şapka, sayılar. Diyalogda Türkçe harfleri asla ASCII'ye çevirme. Sadece modelin **yanlış okuyabileceği** kelimelere not düş, replik başına **en fazla 3–4 not**.
4. **Prompt'u kur** (aşağıdaki şablon).

## SES MODU

### Adım 1 — Analiz

```
python <skill_dir>/scripts/speechmap.py "<dosya>" --out "<çıktı dizini>" [--start 0:05 --end 0:20]
```

- Video dosyası da olur; ses otomatik ayrılır.
- Döküm için `~/.config/brainwatch/.env` içindeki `GROQ_API_KEY` kullanılır (yoksa `OPENAI_API_KEY`). Bu anahtar `watch-brainlab` ile ortaktır.
- YouTube / Instagram linki gelirse önce `watch-brainlab` ile indir, sonra yerel dosyayla çalıştır.
- Çıktı: `report.md` (okunur) + `analysis.json` (kelime zamanları).

### Adım 2 — Raporu oku ve yorumla

Rapordaki ölçümleri **söyleyiş diline** çevir:

| Ölçüm | Prompt'a giden karşılık |
|---|---|
| Hız: yavaş / sakin / doğal / hızlı (hece/sn) | `slow and deliberate` / `calm, unhurried` / `natural conversational pace` / `fast, energetic` |
| Perde: kalın / orta / ince + aralık (st) | `low, deep voice` … ; aralık <8 st → `flat, restrained`; >14 st → `animated, expressive` |
| Ses: yüksek / normal / yumuşak / fısıltıya yakın | `raised, emphatic` / — / `soft` / `almost whispering` |
| Cümle sonu: yükselen / düşen / düz | soru ya da bitmemiş cümle / kesin bitiş / sıralama |
| Duraklamalar | dialogue içinde `...` + delivery'de `pauses briefly after "<kelime>"` |
| Uzatılan kelimeler | telaffuz notu: `stretch "<kelime>"` (dolgu "şey", "yani" ise bu doğrudan duygu bilgisidir) |
| Türkçe işaretler | telaffuz notları için hazır liste |
| ⚠ konuşmacı değişimi olabilir | Perde sıçraması + boşluk varsa ikinci konuşmacı ihtimalini kullanıcıya **sor**; tahmin etme |

**Whisper uyarısı:** Döküm konuşma dilini bazen düzeltir (napıyosun → ne yapıyorsun) ya da yanlış duyar. Raporda bariz bozulma varsa bağlamdan düzelt ve kullanıcıya bir satırla söyle. Gerekirse dökümü kullanıcıya onaylat.

### Adım 3 — Ses dosyası nasıl kullanılacak?

İki yol var. Kullanıcı belirtmediyse **tek soruyla** sor; bağlamdan belliyse sorma:

- **A · Ses referansı (aynı ses):** Dosya Seedance'e `@Audio1` olarak yüklenir. Ses tınısı, aksan, hız ve duygu oradan gelir; söylenecek söz `{}` içindeki metinden gelir. Seedance'in sınırı en fazla **10 ses klibi, toplam 30 sn**. Daha uzunsa `--start/--end` ile en temiz parçayı seç ve kesim komutunu ver.
- **B · Sadece yeniden yorum:** Dosya yüklenmez. Ölçülen söyleyiş, hız, ezgi ve telaffuz yazıyla tarif edilir, Seedance kendi sesiyle üretir.

---

## PROMPT ŞABLONU

```
<Sahne: yer, zaman, ışık, ortam sesi kaynağı — 1-2 cümle>

[A yolu varsa] @Audio1 is used for <Konuşmacı>'s voice timbre, accent, speaking rate and emotion only; the spoken words come from the dialogue below.

Stage 1: <görünür eylem / ifade>.
<Konuşmacı> speaks natural, conversational Istanbul Turkish, <delivery: hız, perde, duygu>: {<Türkçe replik>}
Pronunciation for <Konuşmacı>:
- "<kelime>": <kural>, say it "<okunuş>".
<Diğer karakter> listens with mouth naturally closed.

Stage 2: ...

<Ses efekti>   (Music in parentheses only if wanted.)
Use Turkish for all dialogue. No subtitles appear on screen.
```

Sembol kuralları `sd25-pe` ile aynı: diyalog `{}`, ses efekti `<>`, müzik `()`, altyazı `【】`. `<>` efekt için kullanılıyorsa karakter adlarını köşeli parantez içine **koyma**. Dil etiketi her konuşmacıya **ayrı ayrı** yazılır, başta tek seferlik genel bir beyan yetmez.

---

## ÇIKTI

````
## Prompt
```
<yapıştırılabilir Seedance prompt'u>
```

## Telaffuz özeti
| Kelime | Tuzak | Notta istenen okunuş |
|---|---|---|

## (SES modunda) Kayıttan çıkanlar
- Döküm: ...
- Söyleyiş: <hız, perde, ezgi tek satır>
- Ses referansı: A / B — <gerekiyorsa kesim komutu>
````

---

## KONTROL LİSTESİ

- [ ] Her konuşmacının kendi dil satırı var: `speaks natural, conversational Istanbul Turkish`
- [ ] Gündelik dilde kısaltmalar `{}` içinde, resmî dilde değil
- [ ] Her replikte a / j / ç / ş / ö / ü / ı / ğ / şey / vurgu tuzakları tarandı, en fazla 3–4 not; c'ye not yok
- [ ] `{}` içinde Türkçe harfler eksiksiz (çok, şey, güzel — ASCII yok)
- [ ] Replik uzunluğu aşama süresine sığıyor (~2–3 kelime/sn)
- [ ] Dinleyen karakter: `mouth naturally closed`
- [ ] Sayılar yazıyla
- [ ] `Use Turkish for all dialogue. No subtitles appear on screen.`
- [ ] SES modu: döküm kullanıcının kaydıyla tutarlı, @Audio1 rolü (sadece tını / aksan / hız / duygu) açıkça yazılı
- [ ] Kullanıcı istemedikçe ağız / bölge eklenmedi
