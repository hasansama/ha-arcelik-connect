# Arçelik Connect (COSA) – Home Assistant

Home Assistant için **resmî olmayan**, deneysel Arçelik Connect / COSA bulut entegrasyonu.

Arçelik 12556 model klima üzerinde geliştirilmiş ve Home Assistant Container **2026.10.1** üzerinde temel işlevleri çalışırken gözlemlenmiştir. Henüz başka modellerde denenmemiştir.

![Arçelik Connect simgesi](custom_components/cosa_arcelik/brand/icon.png)

## Özellikler ve doğrulama

| Özellik | Durum |
| --- | --- |
| COSA hesabıyla giriş ve cihaz keşfi | Doğrulandı |
| Home Assistant içinde klima cihazı oluşturma | Doğrulandı |
| Klima açma / kapama | Fiziksel klimada doğrulandı |
| Soğutma, ısıtma, nem alma | Mod komutları ve HA üzerinden çalışma gözlemlendi |
| Fan modu | Entegrasyonda mevcut, ayrı fiziksel test gerekli |
| Hedef sıcaklık değiştirme | COSA ve cihaz durumunda doğrulandı |
| Ortam sıcaklığını okuma | Doğrulandı |
| Fan hızı 1–5 | APK dönüşümü kodlandı, fiziksel hız testleri tamamlanmadı |
| Dikey/yatay kanat seçimleri | API alanları mevcut; konum kodları ve davranışları bütünüyle test edilmedi |
| Home Assistant üzerinden komut sonrası hızlı panel güncellemesi | Kodlandı, tüm durumlarda doğrulama sürüyor |

Home Assistant içinde `climate` ve `select` varlıkları bulunur. `Çalışma modu` seçicisindeki Türkçe etiketler: **Kapalı, Soğutma, Isıtma, Nem Alma, Fan**. Standart Home Assistant klima kartı, yerleşik `dry` modunu sistem çevirisi nedeniyle hâlâ **Kuru** diye gösterebilir; bu entegrasyonla yerleşik çeviriyi değiştirmiyoruz.

## Kurulum: HACS

1. HACS → sağ üst menü → **Custom repositories / Özel depolar**.
2. `https://github.com/hasansama/ha-arcelik-connect` adresini **Integration** türüyle ekleyin.
3. Entegrasyonu **Download / İndir** ile kurun. Geliştirme sürümünü yenilemek için **Redownload → main** kullanın.
4. Home Assistant'ı yeniden başlatın.
5. **Ayarlar → Cihazlar ve Hizmetler → Entegrasyon ekle → Arçelik Connect (COSA)**.
6. Arçelik Connect giriş bilgilerinizi kullanın ve klimayı seçin.

Alternatif: `custom_components/cosa_arcelik` dizinini Home Assistant'ın `/config/custom_components/` klasörüne kopyalayıp yeniden başlatın.

## Kullanım ve mimari

- `climate` varlığı: açma/kapama, HVAC modu, hedef sıcaklık, fan hızı, **dikey ve yatay kanat konumları** (standart Home Assistant swing kontrolleri).
- `select` varlıkları: **Çalışma modu**, **Dikey kanat**, **Yatay kanat**. Kanat seçicilerinin yanı sıra klima kartının desteklediği salınım kontrolleri de kullanılabilir; görünürlük kullanılan kartın özelliklerine bağlıdır.
- Nem alma ve fan modlarında hedef sıcaklık **25 °C sabit** gösterilir, değiştirilmez.
- COSA API: `https://kiwi.cosa.com.tr/api`; `provider: arcelik`.
- Komutlar `sendACState` üzerinden gönderilir; kabul edilen komut sonrasında panel yerel olarak güncellenir ve `getEndpoint` ile hemen doğrulama denenir.
- Genel durum sorgulama aralığı **30 saniyedir**; uygulama/kumanda kaynaklı değişiklikler bu aralıkta görünür.
- COSA bazen mod değişikliğinin hemen ardından durum sorgusuna `100` hata kodu verebilir. Geçici hatalarda son başarılı durum sınırlı sayıda korunur.

## API kodları ve sınırlar

- Çalışma modları: soğutma `0`, nem alma `1`, fan `2`, ısıtma `4`.
- Fan hızı: kullanıcı 1–5 → COSA `acFanSpeed` 2–6 (APK kodundan).
- Dikey kanat: kullanıcı konumları 1–6 → COSA 6–1; otomatik salınım `100`.
- Yatay kanat: `13` sol, `35` sağ, `1–5` ara konumlar, `100` salınım. Yatay kanat aralıklarının fiziksel karşılıkları bütünüyle doğrulanmadı.
- Sıcaklık aralığı `16–30 °C` şu an entegrasyondaki varsayımsal sınırdır.
- `acPower` ve `acMode` gerçek durumu belirtir; `active` veya `operationMode` alanlarını klima güç/mod bilgisi olarak kullanmayız.

## Güvenlik ve sorumluluk

Bu entegrasyon **Arçelik, COSA veya Home Assistant tarafından desteklenmez**. Özel/belgelenmemiş bulut API'si zaman içinde değişebilir. Bulut ve İnternet bağlantısı gereklidir.

Giriş bilgileri Home Assistant config entry içinde saklanır. Token, şifre veya Home Assistant `.storage` içeriğini GitHub'a yüklemeyin.

Henüz erken geliştirme aşamasındadır. Fiziksel cihaz davranışını gözlemleyerek kullanın. Sorun bildirmek için [GitHub Issues](https://github.com/hasansama/ha-arcelik-connect/issues) kullanabilirsiniz.
