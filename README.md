# HOPS_V1

Etsy dükkanları için toplu ürün hazırlama süreçlerini otomatikleştirmek üzere geliştirilmiş PySide6 tabanlı bir masaüstü uygulaması. Görsel analizinden zip paketlerinin oluşturulmasına kadar uzanan uçtan uca iş akışıyla yüksek hacimli poster/print üretimini standartlaştırır.

## İçindekiler
- [Genel Bakış](#genel-bakış)
- [Temel Özellikler](#temel-özellikler)
- [Sistem Gereksinimleri](#sistem-gereksinimleri)
- [Kurulum](#kurulum)
- [Proje Yapısı](#proje-yapısı)
- [Uygulamayı Çalıştırma](#uygulamayı-çalıştırma)
- [İşlevsel Modüller](#işlevsel-modüller)
- [Veritabanı ve Raporlama](#veritabanı-ve-raporlama)
- [Konfigürasyon](#konfigürasyon)
- [Önerilen İş Akışı](#önerilen-iş-akışı)
- [Sorun Giderme](#sorun-giderme)
- [Geliştirici Notları](#geliştirici-notları)
- [Lisans](#lisans)

## Genel Bakış
Uygulama, çalışma dizini olarak kullanıcının ana klasöründe otomatik oluşturulan `~/HOPS_V1` (Windows'ta `C:\Users\<kullanıcı>\HOPS_V1`) ağacını kullanır. `main.py` içindeki `MainWindow` sınıfı tek pencereli bir yönetim paneli sağlar; sol taraftaki menü ile her adımın ayrı ayrı tetiklenmesine izin verirken üstteki "Settings" butonu trimming yüzdesi ve veritabanı sıfırlama gibi yapılandırmaları içerir.

Arka planda tüm operasyonlar SQLite veritabanı (`99_Logs_Reports/hops_v1.db`) ve belirli klasör yapıları üzerinden gerçekleştirilir. Her modül isteğe bağlı ilerleme geri çağrıları (progress callback) alarak PySide6 progress bar bileşenlerini besler.

## Temel Özellikler
- **Görsel Analizi:** `core/analyzer.py` dosyasındaki `analyze_and_store_images` fonksiyonu `0_Data` klasöründeki görselleri tarayarak oran, yön ve benzersiz SKU numaralarını hesaplar.
- **Design Pack Sınıflandırması:** `core/design_pack.py`, trimming toleransına göre görselleri ön tanımlı oran klasörlerine yerleştirir ve master çerçeve kodları üretir.
- **Akıllı Dosya Taşıma:** `core/split_up.py`, oryantasyon ve `Nearest` etiketi bilgilerini kullanarak görselleri `1_Main`, `2_Design/1_Landscape` veya `2_Design/2_Nearest` klasörlerine taşır.
- **Master Üretimi:** `core/run_master.py`, `3_Master/1_Bulk` içindeki dosyalara boyut bazlı master kodu atar ve uygun `3_Master/0_Sizes/...` alt klasörlerine taşır.
- **Etsy İçin Dışa Aktarım:** `core/exporter.py` dosyası `4_Export/Bulk` içeriğini SKU bazlı klasörlere taşır; `core/etsy_zip.py` her SKU klasörünü zip'e dönüştürür.
- **Kontrol Listeleri:** `core/design_process.py`, `5_Etsy` klasöründe eksik master dosyaları raporlayarak `99_Logs_Reports/missing_files.txt` dosyasını üretir.
- **Kısayollar:** `core/shortcuts.py`, masaüstünde proje klasörü ve paketlenmiş uygulama için kısayol oluşturur.

## Sistem Gereksinimleri
- Python 3.11–3.13
- [Poetry](https://python-poetry.org/) (bağımlılık yönetimi için önerilir)
- Çapraz platform destekli; PyInstaller paketi Windows yürütülebiliri üretmek üzere yapılandırılmıştır.
- Windows ortamında kısayol oluşturmak için `pywin32`; görüntü işlemleri için `Pillow`; arayüz için `PySide6` gereklidir (tümü `pyproject.toml` içinde tanımlıdır).

## Kurulum
1. **Depoyu klonlayın**
   ```bash
   git clone <repo_url>
   cd HOPS_V1
   ```
2. **Bağımlılıkları yükleyin** (Poetry önerilir)
   ```bash
   poetry install
   ```
   Alternatif olarak sanal ortam kurup `pip install -r` yerine aşağıdaki komutu kullanabilirsiniz:
   ```bash
   pip install pyside6 pillow pywin32
   ```
3. **İlk çalıştırma** sırasında `ensure_structure()` fonksiyonu kullanıcı dizininde tüm çalışma klasörlerini oluşturur. Windows'ta `99_Logs_Reports` klasörü gizli olarak işaretlenir.

## Proje Yapısı
Kaynak deposu:
```
HOPS_V1/
├── assets/            # Uygulama simgesi (hop.ico)
├── build/             # PyInstaller geçici çıktıları
├── core/              # İş mantığı modülleri
├── dist/              # Paketlenmiş uygulama çıkışı (oluşturulduğunda)
├── main.py            # PySide6 arayüzü ve giriş noktası
├── pyproject.toml     # Bağımlılıklar ve yapı ayarları
└── HOPS_V1.spec       # PyInstaller yapı betiği
```

Çalışma dizini (`~/HOPS_V1`) ilk açılışta aşağıdaki gibi hazırlanır:
```
~/HOPS_V1/
├── 0_Data/                       # Ham görsellerin bırakıldığı klasör
├── 1_Main/                       # Tasarım öncesi işlenecek görseller
├── 2_Design/
│   ├── 0_Portrait/
│   │   ├── Ratio/Ratio_24x36/{H_36,W_24}/
│   │   ├── Ratio/Ratio_18x24/{H_24,W_18}/
│   │   ├── Ratio/Ratio_24x30/{H_30,W_24}/
│   │   ├── Ratio/Ratio_11x14/{H_14,W_11}/
│   │   ├── Ratio/Ratio_A_Series/{H_33.110,W_23.386}/
│   │   └── Unmatched/
│   ├── 1_Landscape/
│   └── 2_Nearest/
├── 3_Master/{0_Sizes,1_Bulk}/    # Master görsel alanları
├── 4_Export/{Bulk,Unmatched}/
├── 5_Etsy/
├── 6_Etsy_Zip/
└── 99_Logs_Reports/
    ├── config.json               # Trimming ayarları
    └── hops_v1.db                # SQLite veritabanı
```

## Uygulamayı Çalıştırma
### Geliştirme modunda
```bash
poetry run python main.py
```
Uygulama başlarken dizin yapısını ve veritabanını kurar, ardından masaüstünde klasör/EXE kısayolları oluşturmayı dener.

### PyInstaller ile derleme
1. Simgeyi `assets/hop.ico` içine yerleştirin.
2. Aşağıdaki komutla tek dosyalı Windows yürütülebiliri üretin:
   ```bash
   poetry run pyinstaller --noconfirm HOPS_V1.spec
   ```
3. Paketlenmiş uygulama `dist/HOPS_V1/` altında oluşur.

## İşlevsel Modüller
Aşağıdaki başlıklar, sol menüdeki butonların tetiklediği ardıl işlemleri özetler:

### Settings
- `config.json` içindeki `trimming` yüzdesini günceller (varsayılan `%8`).
- Veritabanı sıfırlama butonu, "confirm" kelimesiyle onay aldıktan sonra tüm tabloları temizler.

### Analyzer
1. `0_Data` klasöründeki tüm dosyaları tarar.
2. `Pillow` ile genişlik/yükseklik ve oryantasyon bilgilerini çıkarır.
3. Her görsel için `HOPS_` ile başlayan artan SKU oluşturur ve `raw_data` tablosuna kaydeder.
4. Duplikat `original_name` tespit edilirse kayıt atlanır.

### Design Pack
- `raw_data` içindeki dikey görselleri trimming toleransına göre oran klasörlerine eşler.
- Oran eşleşirse ilgili klasör yolu (`Ratio_24x36\H_36` vb.) ve master çerçeve kodu (`HOPS_xxx_R24x36_300DPI_sRGB`) `design_pack` tablosuna eklenir.
- Hiçbir oran eşleşmezse en yakın oran `Nearest_...` etiketiyle kaydedilir.

### Split-Up
- `0_Data` içindeki dosyaları, `raw_data` tablosundaki SKU bilgisiyle yeniden adlandırır.
- Yatay ve kare görseller `2_Design/1_Landscape` klasörüne; `Nearest` etiketli SKU'lar `2_Design/2_Nearest` klasörüne; kalan dikey görseller `1_Main` klasörüne taşınır.

### Design
- `1_Main` klasöründeki dosyaları alır, `design_pack` tablosunda listelenen oran klasörlerine kopyalar.
- `Nearest` etiketli görseller `2_Design/0_Portrait/Unmatched` klasörüne taşınır.
- İşlem sonunda `design_check` tablosunu güncellemek üzere `check_design_images()` çalıştırılır.

### Master
1. `3_Master/1_Bulk` içindeki görsellerin boyutlarını okuyarak `master_check` tablosunu günceller (`run_master_bulk_check`).
2. Boyutlara göre master kodu (`R18x24`, `R11x14`, `RA1`, `R24x36`, `R24x30`) atar.
3. `perform_master_moves` fonksiyonu dosyaları ilgili `3_Master/0_Sizes/Ratio/...` klasörlerine taşır ve dosya adını master koduyla değiştirir.

### Export
- `4_Export/Bulk` klasöründeki dosyaları SKU bazlı klasörlere (`5_Etsy/<SKU>/`) taşır; mevcut dosyalar üzerine yazılır.

### Etsy Zip
- `5_Etsy` içindeki her SKU klasörünü zipleyerek `6_Etsy_Zip/<SKU>.zip` dosyalarını oluşturur.

### Check List
- `run_design_process_check` fonksiyonu ile `5_Etsy` klasöründe beklenen master dosyalarını doğrular.
- Eksikler `99_Logs_Reports/missing_files.txt` dosyasına yazılır ve arayüzde tablo olarak gösterilir.
- Tablo satırları sağ tık menüsü veya `Ctrl+C` ile panoya kopyalanabilir.

### Dashboard
- Placeholder olarak yer almaktadır; gelecekte metrik ve özet görünümler için kullanılabilir.

## Veritabanı ve Raporlama
- **SQLite Dosyası:** `99_Logs_Reports/hops_v1.db`
  - `raw_data`: Görsel metadata ve SKU eşleşmeleri.
  - `design_pack`: Oran eşleşmeleri ve master çerçeve kodları.
  - `design_check`: Tasarım klasörlerinde dosya varlığını takip eder.
  - `master_check`: Master bulk dosyalarının durumunu kaydeder.
- **Rapor Dosyaları:**
  - `missing_files.txt`: `Check List` çalışması sonrası eksik master kayıtları.
- Veritabanı performansı için `journal_mode=WAL` ve `busy_timeout` ayarları etkinleştirilir.

## Konfigürasyon
- `config.json` içinde saklanan `trimming` yüzdesi, Design Pack aşamasında kabul edilen oran sapmasını belirler.
- Manuel düzenleme durumunda değer aralığı önerilen `0–15` arasındadır; arayüzde hatalı girişler varsayılan `%8` olarak düzeltilir.
- Windows'ta masaüstü kısayolları `Desktop` klasörüne `.lnk` olarak oluşturulur; Linux/macOS ortamında sembolik bağlantı veya `.desktop` dosyası üretilir.

## Önerilen İş Akışı
1. `0_Data` klasörüne yeni görselleri kopyalayın.
2. Uygulamada **Analyzer**'ı çalıştırın.
3. Ardından **Design Pack** otomatik tetiklenir (Analyzer butonu bunu zincir halinde yapar).
4. **Split-Up** ile görselleri oryantasyona göre dağıtın.
5. **Design** aşamasıyla oran klasörlerine kopyalayın ve kalite kontrolünü yapın.
6. Master görsellerinizi `3_Master/1_Bulk` klasörüne ekleyin, **Master** butonu ile boyut bazlı taşımayı yapın.
7. Son tasarımları `4_Export/Bulk` klasörüne yerleştirip **Export** çalıştırın.
8. Etsy yüklemeleri için **Etsy Zip** aşamasını tamamlayın.
9. Gönderim öncesi **Check List** ile eksik dosya kontrolünü yapın.

## Sorun Giderme
- **Veritabanı kilit hataları:** Başka bir süreç `hops_v1.db` dosyasını kullanıyorsa tekrar deneyin; gerekirse Settings ekranından veritabanını sıfırlayın.
- **Analyzer hiçbir dosya bulmuyor:** Görsellerin `~/HOPS_V1/0_Data` klasöründe olduğundan emin olun ve dosya adlarının benzersiz olduğuna dikkat edin.
- **Nearest sonuçları fazlaysa:** `trimming` değerini artırarak toleransı yükseltin; `Nearest` kaydı olan SKU'lar `Design` adımında `Unmatched` klasörüne taşınır.
- **Kısayol oluşturma başarısız:** `pywin32` kurulumunu kontrol edin veya Windows dışındaki sistemlerde manuel kısayol oluşturun.

## Geliştirici Notları
- Tüm uzun süreli işlemler isteğe bağlı `progress_cb(index, total, message)` parametresiyle kullanıcı arayüzüne durum bildirimi yapar. CLI senaryolarında bu parametre atlanabilir.
- `core` modülleri `pyproject.toml` altındaki `packages` alanı sayesinde bağımsız paket olarak kullanılabilir; dış betikler `from core import ...` şeklinde içe aktarabilir.
- Yeni oran tipleri eklemek için `core/design_pack.py` içindeki `RATIOS` ve `MASTER_CODES` sözlükleri güncellenmelidir.
- Master heuristikleri `core/run_master.py` içinde boyut bazlı koşullarla tanımlanmıştır; ihtiyaca göre ek boyutlar eklenebilir.

## Lisans
Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.