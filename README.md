# Arçelik Connect / COSA — Home Assistant özel entegrasyonu (0.1.0)

Arçelik Connect uygulamasının özel COSA bulut API'siyle hazırlanan **deneysel**, resmi olmayan entegrasyon.

## Kurulum
1. `custom_components/cosa_arcelik` klasörünü Home Assistant yapılandırma klasörüne kopyalayın.
2. Home Assistant'ı yeniden başlatın.
3. Ayarlar → Cihazlar ve Hizmetler → Entegrasyon Ekle → **Arçelik Connect (COSA)**.
4. Hesabınızla giriş yapın ve klimayı seçin.

## Özellikler
- Klima aç/kapat; soğutma, ısıtma, nem alma ve fan modu.
- Ortam/hedef sıcaklığı; nem alma ve fan modunda hedef 25 °C, değiştirilemez.
- Fan hızı 1–5.
- İki bağımsız kanat seçici: dikey ve yatay.
- Bulut durumu 30 saniyede bir yenilenir.

## API ve eşleştirmeler
- Doğrulanan komutlar: `acPower`, `acMode`, `targetTemperature`.
- APK'dan bulunan fan kodları: gösterilen hız 1–5 → API kodu 2–6.
- Dikey kanat: kullanıcı 1–6 → API 6–1; otomatik = 100.
- Yatay kanat: 13 tam sol, 35 tam sağ, 1–5 ara konum, 100 otomatik. Ara konumların fiziksel yönleri henüz test edilmedi.
- Kanat ve fan komutları fiziksel cihazda henüz ayrı ayrı doğrulanmadı.
- Sıcaklık sınırları 16–30 °C ilk sürüm varsayımıdır.

## Güvenlik ve durum
- COSA tarafından yayımlanan resmî bir API olmadığı için haber verilmeksizin değişebilir.
- Kullanıcı bilgileri Home Assistant yapılandırma girişinde tutulur. `.storage` dosyalarını ve token/şifreleri GitHub'a yüklemeyin.
- Home Assistant içinde henüz çalıştırılıp test edilmedi. Ev sisteminde kullanmadan önce gözlemleyerek doğrulayın.
- Resmî Home Assistant veya Arçelik entegrasyonu değildir.
