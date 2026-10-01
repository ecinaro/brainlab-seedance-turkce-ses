# Türkçe Telaffuz Rehberi — Seedance diyalog notları için

Video modelleri Türkçeyi çoğu zaman **harf harf** okur. Bu dosya, hangi yazımın gerçekte nasıl duyulduğunu ve prompt'a hangi İngilizce notla geçirileceğini listeler. Notlar İngilizce yazılır, çünkü prompt İngilizcedir; tırnak içindeki örnekler Türkçe kalır.

Not formatı (her konuşmacının altında):
```
Pronunciation for <İsim>:
- "<kelime>": <kural, İngilizce>, say it "<okunuş>".
```

Sadece **o replikte gerçekten geçen ve modelin yanlış okuyabileceği** kelimelere not yaz. Her kelimeye not, hiç not kadar kötüdür. Replik başına en fazla 3–4 not.

**Diyalogda Türkçe harfler asla ASCII'ye çevrilmez.** `{çok}` yazılır, `{cok}` değil; `{şey}`, `{seyy}` değil. Harf kaybolursa telaffuz da kaybolur.

---

## 0. Türkçeye özgü harfler — tek tek

Model bu harfleri İngilizce, Almanca ya da Fransızca alışkanlıkla okuyabilir. Kelimede geçiyorsa ve yanlış okunma riski varsa not düş.

| Harf | Ses (IPA) | Türkçe örnek | Doğru okunuş | Tipik hata | Prompt notu |
|---|---|---|---|---|---|
| **ç** | /tʃ/ | çok, çay, kaç, güç | "ch" as in "church" | "k" ya da "s" | `"ç" is "ch" as in church` |
| **ş** | /ʃ/ | şey, şimdi, iş, beş | "sh" as in "shoe" | "s" | `"ş" is "sh" as in shoe` |
| **a** | /a/ | cesaret, hayat, karakter, ama, yani | kısa, açık, saf "a" ("father"daki a, ama kısa) | **İngilizce okuma: "æ" (cat) ya da "ey" (cake)** — "cesæret", "heyat" | `say "<kelime>" exactly as written in Turkish; every "a" is a short open "a" as in "father", never "æ" as in cat, never "ey" as in cake` |
| **j** | /ʒ/ | jüri, jilet, garaj, bej | "s" as in "measure", soft | "dʒ" (İngilizce j) | `"j" is soft "zh" as in measure, not English j` |
| **ö** | /ø/ | göz, öğle, gönül, söz | German ö, lips rounded, tongue forward | "o" | `"ö" is a rounded front vowel like German ö, not "o"` |
| **ü** | /y/ | güzel, üç, süt, düş | German ü / French "u" | "u" | `"ü" is a rounded front vowel like German ü, not "u"` |
| **ı** | /ɯ/ | kız, ılık, altı | dudaklar yayık, dil geride; "i" ile "u" arası kapalı ses (ayrıntı: bölüm 4) | "i" ya da "u" | `"ı" is a close unrounded back vowel, not "i" and not "u"` |
| **ğ** | sessiz / uzatma / y-kayması | dağ, yağmur, değil, eğer, öğretmen | **hiç "g" duyulmaz.** Kalın ünlüden sonra ünlüyü uzatır ("daa", "yaamur"), e/i yanında yumuşak "y" olur ("deyil", "eyer"), hece sonunda ünlüyü uzatır ("ööretmen") (ayrıntı: bölüm 1) | **sert "g"**: "de-gil", "dag" | `the ğ is never a hard g: it is silent and lengthens the vowel ("daa"), or a soft y-glide next to e/i ("deyil")` |
| **â / î / û** | uzun ünlü + incelme | hâlâ, kâr, rüzgâr, millî | ünlü uzar; k/g/l'den sonra â ise ünsüz incelir: "kyar", "rüzgyar" (ayrıntı: bölüm 7) | şapka yok sayılır | `"â" is a long a, and the k before it is palatalized: "kyar"` |
| **İ / i** | /i/ | İstanbul, iki | "ee" | — | büyük İ'deki noktayı koru |
| **v** | /v/ ~ /w/ | tavuk, havuç | yuvarlak ünlü yanında yumuşar, "tawuk" | sert v | genelde not gerekmez |
| **r** | /ɾ/ | bir, gerek, araba | dil ucu tek vuruş, İngilizce "r" değil | İngilizce kıvrık r | `tapped Turkish r, not English r` |
| **e** | /e/ ~ /æ/ | gel, ben, sen | açık "e"; l, r, m, n öncesinde hafif "æ"ye kayar | "i" | genelde not gerekmez |

**Okunuş örneği yazarken kelimeyi başka harflerle yeniden heceleme.** "jesaret", "dje-sa-ret" gibi uydurma yazımlar Türkçe okuyucuyu da modeli de yanıltır. Kelime kendi yazımıyla kalır; nota "exactly as written in Turkish" yazılır, sorunlu ses (çoğunlukla ünlü) İngilizce örnek kelimeyle tarif edilir.

**c'ye not düşme.** Model Türkçe c'yi doğru okuyor; c notu fayda yerine bozulma getiriyor.

**Ünlüler saftır.** Türkçede a, e, ı, i, o, ö, u, ü kayma yapmaz ve diftong olmaz. İngilizce okuma alışkanlığı en çok **a**'yı bozar ("æ" / "ey"), sonra **e**'yi ("i" ya da "ey") ve **o**'yu ("ou").

**Çift harf** her zaman iki kez, uzatılarak okunur: `anne` → "an-ne", `elli` → "el-li", `dikkat` → "dik-kat". Not: `the double "n" is held, an-ne`.

**Kelimeler harf harf okunur, sessiz harf yoktur** (ğ hariç). `kahve`, "kave" değil "kah-ve"; h duyulur.

Hangi harfe not düşülür? Kural: **j ve ğ her zaman** (en sık bozulanlar), **a** İngilizce bir kelimeye benzeyen ya da çok a'lı kelimede (cesaret, hayat, karakter, davranmak), **ö / ü** anlam ayıran ya da vurgulu kelimede (göz/goz, süt/sut), **ç / ş** sadece kelime yabancı bir kelimeye benziyorsa (örneğin "şık" İngilizce "sick" gibi okunabilir).

---

## 1. Yumuşak ğ

ğ hiçbir zaman sert "g" olarak duyulmaz. Üç davranışı var:

| Durum | Örnek | Okunuş | Prompt notu |
|---|---|---|---|
| Kalın ünlüden sonra, iki ünlü arasında | dağı, ağaç, sağol | "daa-ı", "aaç", "saa-ol" | `the ğ is silent; it just lengthens the vowel before it` |
| e / i yanında | değil, eğer, eğlence, diğer | "deyil", "eyer", "eylence", "diyer" | `the ğ is a soft y-like glide, never a hard g` |
| Hece / sözcük sonunda | dağ, yağmur, doğmaz, öğretmen, çağ | "daa", "yaamur", "doomaz", "ööretmen", "çaa" | `the ğ is silent and lengthens the preceding vowel` |

Kısaltılmış kalıplar: **ağabey → "abi"**, **değil mi → "di mi"** (konuşma dilinde `{}` içine doğrudan `abi`, `di mi` yazılabilir).

## 2. "şey"

| Kullanım | Okunuş | Prompt notu |
|---|---|---|
| Tereddüt / dolgu ("Şey... bilmiyorum") | "şeeey", uzar, sesi düşerek söner | `"Şey" is a hesitation filler: stretch the vowel, "şeeey", trailing off with slightly falling pitch` |
| İsim ("Bir şey aldım") | kısa, düz "şey" | not gerekmez |
| Konuşma dilinde "bir şey" | "bişey" | `{}` içine `bişey` yazılabilir |

Diğer dolgular: **yani** (YA-ni, ilk hece vurgulu, sık sık uzatılır "yaaani"), **hani**, **işte** (İŞ-te), **ııı / eee** (düşünme sesi), cümle sonunda **ya** (yumuşatıcı, alçak ve kısa), **abi / abla** (hitap).

## 3. Konuşma dili kısaltmaları

Bunlar ağız hareketini değiştirdiği için **doğrudan `{}` içine** konuşma dili haliyle yazılır (karar: lip-sync birebir eşleşsin). Altına kısa bir "spoken contraction" notu düşülür.

| Yazı dili | Konuşma dili (`{}` içine) | Not |
|---|---|---|
| ne yapıyorsun | napıyosun | `fast, one word, no r` |
| geliyorum / gidiyorum / biliyorum | geliyom / gidiyom / biliyom | `-yorum is reduced to -yom` |
| bir | bi | `short, no r` |
| bir şey | bişey | — |
| değil mi | di mi | `two tiny syllables, rising` |
| ne oldu / ne olur | noldu / nolur | — |
| yapacağım / geleceğim | yapıcam / gelcem | `-acağım is reduced to -cam/-cem` |
| bir dakika | bi dakka | — |
| vallahi | valla | — |

Kullanıcı resmî / spiker / sunum dili istiyorsa kısaltma **yapma**, yazı dilini koru.

## 4. ı ile i

ı (noktasız) dudaklar yayık, dil geride, kapalı bir ünlüdür (IPA /ɯ/). Model onu "i" ya da "u" gibi okuyabilir.

- Not: `"kız" uses the Turkish ı, a close unrounded back vowel, not "i" and not "u"`
- Anlam farkı olan çiftler kritik: **kır / kir**, **sıcak**, **ılık**, **altı / alti** değil.
- Büyük harfte dikkat: **I** = ı, **İ** = i. İsimlerde (Işık, İrem) doğru harfi koru.

## 5. Vurgu

Türkçede varsayılan vurgu **son hecededir** (ki-TAP, ki-tap-LAR). İstisnalar modelin en çok bozduğu yerdir:

| Kural | Örnek | Okunuş |
|---|---|---|
| Şimdiki zaman -yor vurgusuz, vurgu ondan önceki hecede | geliyor, yapıyorum | ge-Lİ-yor, ya-PI-yo-rum |
| Yer adları çoğunlukla ilk hecelerde | Ankara, Türkiye, Avrupa, İzmir | AN-ka-ra, TÜR-ki-ye, av-RU-pa, İZ-mir |
| İstanbul | İstanbul | is-TAN-bul |
| Bazı zarflar / bağlaçlar ilk hecede | şimdi, yani, belki, sonra, ama | ŞİM-di, YA-ni, BEL-ki, SON-ra, A-ma |
| Olumsuzluk eki -me/-ma vurgusuz, vurgu ondan önce | gelmedi, yapma | GEL-me-di, YAP-ma |
| Soru eki mi/mı/mu/mü vurgusuz | geliyor musun? | ses "musun"dan hemen önce yükselir, "musun" alçak kalır |
| Ek-fiil -dir, -ken, bağlaç "de" vurgusuz | evdeyken, sen de | EV-dey-ken, SEN de |
| Hitap / ünlem ilk hecede | Ahmet!, Anne! | AH-met!, AN-ne! |

Prompt notu: `stress on the first syllable, AN-ka-ra` / `"musun" is unstressed; the pitch rises on the syllable before it`.

## 6. Ezgi (intonation)

| Cümle tipi | Ezgi | Prompt notu |
|---|---|---|
| mi'li soru (evet/hayır) | mi'den önceki hecede yükselir, mi alçak | `rising question intonation peaking on "<hece>"` |
| ne / nasıl / kim soruları | düşen | `falling intonation, it is a wh-question` |
| Sitem / şaşkınlık "Hadi ya!", "Yok artık!" | yüksek başlar, düşer | `exclamation, high start, sharp fall` |
| Cümle sonu "ya" | alçak, kısa, yumuşatıcı | `the final "ya" is short and soft` |
| Liste / devam eden cümle | düz ya da hafif yükselen, bitmemiş | `level intonation, sentence continues` |

## 7. Uzun ünlüler ve şapka

| Örnek | Okunuş | Not |
|---|---|---|
| hâlâ (still) / hala (aunt) | "haalaa" / "hala" | şapka ünlüyü uzatır, anlam değişir |
| kâr, rüzgâr, Kâzım | k ve g incelir: "kyar", "rüzgyar" | `palatalized k, like "kyar"` |
| saat, kanaat, memur, resmen | "saat" uzun a, "meemur" | Arapça kökenli uzun ünlüler |

## 8. Diğer

- **h** her zaman duyulur, sözcük sonunda da hafifçe: sabah, Allah, şah.
- **Sözcük sonu r** gündelik İstanbul konuşmasında hafif hışırtılı ve zayıftır ("var", "bir"). Abartma; sadece kullanıcı "İstanbul ağzı" isterse not düş.
- **Ünsüz benzeşmesi** yazıya yansıtılmaz, model genelde doğru okur; not gerekmez.
- **Sayılar, kısaltmalar, semboller** her zaman yazıyla: `2026` → `iki bin yirmi altı`, `%50` → `yüzde elli`, `AI` → `yapay zekâ`.
- **İngilizce kelimeler** Türkçe cümle içinde (toplantı, "deadline") Türkçe ağızla okunur; not: `"deadline" said the way a Turkish speaker says it, not native English`.

## 9. Ağız / bölge (sadece istenirse)

Kullanıcı açıkça belirtmedikçe varsayılan **"natural, conversational Istanbul Turkish"**dir. Ağız istenirse dil satırına ekle: `natural Turkish with a light Black Sea (Karadeniz) accent`, `Aegean (Ege) Turkish`, `Eastern Anatolian accent`. Ağız ekleyince kalıplaşmış karikatür ifadelerden kaçın.
