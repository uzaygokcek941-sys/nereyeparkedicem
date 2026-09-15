# Giriş sistemini açma — Supabase

Kod tarafı **bitti ve test edildi**. Giriş özelliği şu an bilerek **kapalı**:
`site/veri/auth.json` yer tutucu değer taşıyor, uygulama da bunu görüp
"Giriş henüz açık değil" diyor. Aşağıdaki adımlar bitince kendiliğinden açılır.

Asistan bu adımları yapamaz: hesap açma OAuth girişi gerektiriyor ve
**API anahtarı girmek asistana yasak** — ikisi de senin adımın.

## 1 · Supabase projesi aç

<https://supabase.com> → GitHub ile giriş → **New project**.
Bölge olarak **Frankfurt (eu-central-1)** seç; Türkiye'ye en yakın olanı,
gecikme düşer.

## 2 · Tabloyu ve güvenlik kurallarını kur

Supabase panelinde **SQL Editor** → aşağıdakini olduğu gibi çalıştır.

```sql
create table public.favoriler (
  kullanici   uuid primary key references auth.users(id) on delete cascade,
  veri        jsonb not null default '[]'::jsonb,
  guncelleme  timestamptz not null default now()
);

alter table public.favoriler enable row level security;

-- Her kullanici YALNIZ kendi satirini gorur ve yazar.
-- Bu politika olmadan anon anahtar butun favori listelerini okuyabilirdi.
create policy "kendi satirini okur" on public.favoriler
  for select using (auth.uid() = kullanici);
create policy "kendi satirini ekler" on public.favoriler
  for insert with check (auth.uid() = kullanici);
create policy "kendi satirini gunceller" on public.favoriler
  for update using (auth.uid() = kullanici) with check (auth.uid() = kullanici);
create policy "kendi satirini siler" on public.favoriler
  for delete using (auth.uid() = kullanici);
```

`on delete cascade` önemli: hesap silinince favori kaydı da silinir — KVKK
m.11 silme talebini tek işlemle karşılar.

## 3 · Dönüş adreslerini tanımla

**Authentication → URL Configuration**:

- **Site URL**: `https://nereyeparkedicem.vercel.app`
- **Redirect URLs** (ikisini de ekle):
  - `https://nereyeparkedicem.vercel.app/favoriler/`
  - `http://127.0.0.1:8744/favoriler/` *(yerel test için, istersen)*

Bu liste eksikse magic link "invalid redirect" hatası verir.

## 4 · Google girişini aç (isteğe bağlı)

E-posta bağlantısı (magic link) Supabase'de **varsayılan açıktır**, ek iş yok.
Google istiyorsan: Google Cloud Console → OAuth client ID (Web) oluştur →
Supabase **Authentication → Providers → Google**'a Client ID + Secret gir.
Google tarafındaki "Authorized redirect URI" alanına Supabase'in verdiği
`https://<proje>.supabase.co/auth/v1/callback` adresini yapıştır.

Google'ı açmazsan: giriş sayfasındaki "Google ile devam et" düğmesi kalır ama
basıldığında Supabase hata döner. İstemiyorsan `uret.py` içindeki `GIRIS`
sabitinden o iki satırı sil.

## 5 · Anahtarları dosyaya yaz

Supabase panelinde **Project Settings → API**:

```json
{
  "url": "https://<PROJE-REF>.supabase.co",
  "anonKey": "<anon public anahtari>"
}
```

Bunu `site/veri/auth.json` dosyasına yaz.

**`anon` anahtarını kullan, `service_role` anahtarını ASLA.** `anon` tasarım
gereği açık metindir — tarayıcıda çalışır, koruma RLS'ten gelir, o yüzden
depoda durabilir. `service_role` RLS'i **atlar**; sızarsa bütün veri okunur.

`uret.py` bu dosya varsa **üstüne yazmaz**, yani sonraki derlemelerde
girdiğin değerler kalır.

## 6 · Yeniden üret ve doğrula

```bash
python uret.py            # gizlilik metni "hesap acik" haline gecer
python test_uret.py       # birim testler
python kontrol.py         # hesaplanan CSS degerleri
python kontrol_favori.py  # favori + giris akisi (auth acikken farkli dallar)
git add -A && git commit -m "feat: Supabase giris acildi" && git push
```

`python uret.py` çalıştırmayı **unutma**: gizlilik sayfası hesap özelliği
açıkken farklı metin üretiyor (e-posta işleniyor, yurt dışına aktarım,
KVKK m.11 hakları). Eski metin "işlenen kişisel veri yoktur" diyor ve
giriş açıldığı anda bu **yanlış** olur.

`test_uret.py` içinde iki test giriş **kapalı** olduğunu varsayar
(`auth varsayilan KAPALI`, `gizlilik supabase demiyor`). Açtığında ikisi
kırmızıya döner — beklenen davranış; o testleri açık duruma çevir.

## Açtıktan sonra değişenler

| | Giriş kapalı | Giriş açık |
|---|---|---|
| Favoriler | localStorage, cihazda kalır | + Supabase'e eşitlenir |
| İşlenen kişisel veri | yok | e-posta + favori listesi |
| Gizlilik metni | "kişisel veri toplamıyoruz" | KVKK aydınlatma + yurt dışı aktarım |
| Play **Data safety** formu | veri toplamıyor | **E-posta adresi** + **Uygulama içi etkinlik** beyan edilmeli |
| supabase.js (218 KB) | hiç inmez | yalnız giriş yapılmış oturumda iner |

Play Console tarafını `PLAY-HAZIRLIK.md` anlatıyor; giriş açılırsa Data
safety formu **yeniden doldurulmalı**.
