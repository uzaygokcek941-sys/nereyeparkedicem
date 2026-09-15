# Giriş sistemini açma — Supabase

## Durum (2026-09-15)

| Adım | Durum |
|---|---|
| Proje `depnhkygxsqsyiomfbad` | **açık** |
| `site/veri/auth.json` (anon anahtar) | **yazıldı, canlıda** — JWT `ref` url ile eşleşiyor, rol `anon` |
| E-posta magic link sağlayıcısı | **açık** (`/auth/v1/settings` → `email: true`) |
| Kayıt açık mı | **evet** (`disable_signup: false`) |
| **`public.favoriler` tablosu** | **YOK** → adım 2, SENDE |
| **Redirect URL listesi** | **doğrulanamadı** → adım 3, SENDE |
| Google sağlayıcısı | **kapalı** (`google: false`) — düğme otomatik gizlendi, adım 4 isteğe bağlı |

**Bu ikisi bitmeden giriş uçtan uca çalışmaz.** Panel adımlarını asistan
yapamaz: bu oturumda tarayıcı aracı yok ve Supabase paneli OAuth girişi
istiyor. SQL ve URL'ler aşağıda, kopyala-yapıştır.

## 2 · Tabloyu ve güvenlik kurallarını kur — **SENDE, ZORUNLU**

Şu an tablo yok, ölçüldü:
`{"code":"PGRST205","message":"Could not find the table 'public.favoriler'"}`.
Bu yüzden giriş yapılsa bile favoriler eşitlenmez — uygulama bunu sessizce
yutmuyor, `/favoriler/` sayfasında hatayı aynen yazıyor.

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

## 2b · Hesap silme fonksiyonu — **SENDE, ZORUNLU (Play şartı)**

Google Play User Data politikası: hesap açılabilen uygulamada kullanıcı hesabını
**hem uygulama içinden hem web üzerinden** silebilmeli. Sayfa hazır
(`/hesap-sil/`), düğme hazır — ama silmeyi sunucu yapmak zorunda: `anon` anahtar
`auth.users` tablosuna yazamaz (yazabilseydi herkes herkesin hesabını silerdi).

SQL Editor'de çalıştır:

```sql
create or replace function public.hesabimi_sil()
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  -- auth.uid() JWT'den gelir: kullanici yalnizca KENDI satirini silebilir.
  delete from auth.users where id = auth.uid();
end;
$$;

revoke all on function public.hesabimi_sil() from public, anon;
grant execute on function public.hesabimi_sil() to authenticated;
```

`public.favoriler` tablosu `on delete cascade` taşıdığı için favori kaydı aynı
işlemde siliniyor; ayrıca silmene gerek yok.

Bunu çalıştırmazsan `/hesap-sil/` düğmesi hata mesajı gösterir (sessizce
başarılı görünmez) — ama **Play incelemesi uygulamayı reddeder**, çünkü silme
yolu fiilen çalışmıyor olur.

## 3 · Dönüş adreslerini tanımla — **SENDE, ZORUNLU**

**Authentication → URL Configuration**:

- **Site URL**: `https://nereyeparkedicem.vercel.app`
- **Redirect URLs** (ikisini de ekle):
  - `https://nereyeparkedicem.vercel.app/favoriler/`
  - `http://127.0.0.1:8744/favoriler/` *(yerel test için, istersen)*

Bu liste eksikse magic link "invalid redirect" hatası verir.

## 4 · Google girişini aç — isteğe bağlı, şu an KAPALI

E-posta bağlantısı (magic link) Supabase'de **varsayılan açıktır**, ek iş yok.
Google istiyorsan: Google Cloud Console → OAuth client ID (Web) oluştur →
Supabase **Authentication → Providers → Google**'a Client ID + Secret gir.
Google tarafındaki "Authorized redirect URI" alanına Supabase'in verdiği
`https://<proje>.supabase.co/auth/v1/callback` adresini yapıştır.

**Açmazsan bir şey yapmana gerek yok:** `hesap.js` açılışta
`/auth/v1/settings` okuyor ve `google: false` görünce düğmeyi **gizliyor**
(canlıda doğrulandı). Panelden açtığın an düğme kendiliğinden geri gelir.

## 5 · Anahtarları dosyaya yaz — ✅ YAPILDI

Supabase panelinde **Project Settings → API**:

```json
{
  "url": "https://<PROJE-REF>.supabase.co",
  "anonKey": "<anon public anahtari>"
}
```

Bu **yazıldı ve canlıda**; tekrar yapmana gerek yok. Kayıtlı değerler:
`url` = `https://depnhkygxsqsyiomfbad.supabase.co`, `anonKey` = anon rolünde
(JWT `ref` alanı proje kimliğiyle eşleştiği doğrulandı).

**`anon` anahtarını kullan, `service_role` anahtarını ASLA.** `anon` tasarım
gereği açık metindir — tarayıcıda çalışır, koruma RLS'ten gelir, o yüzden
depoda durabilir. `service_role` RLS'i **atlar**; sızarsa bütün veri okunur.

`uret.py` bu dosya varsa **üstüne yazmaz**, yani sonraki derlemelerde
girdiğin değerler kalır.

## 6 · Yeniden üret ve doğrula — ✅ YAPILDI (tablo kurulunca tekrarla)

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

**Service worker gecikmesi:** `auth.json` önden önbelleğe alınıyor ve strateji
stale-while-revalidate. Yayına aldıktan sonra **daha önce siteyi açmış** bir
tarayıcı ilk yüklemede hâlâ eski (yer tutucu) dosyayı görebilir, yani giriş bir
yenileme boyunca kapalı görünür. İkinci açılışta kendiliğinden düzelir —
yanlış değil, bir tur gecikmeli.

`test_uret.py` gizlilik testleri artık sabit durum beklemiyor: `auth_acik()`
sonucuyla metnin **tutarlı** olduğunu doğruluyor. Açıkken anahtarın `anon`
rolünde olduğunu ve JWT `ref` alanının url ile eşleştiğini de kontrol ediyor —
`service_role` yapıştırılırsa test kırmızıya döner.

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
