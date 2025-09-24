# HOPS_V1

Place your icon at `assets/hop.ico` and build with:

```bash
poetry run pyinstaller --noconfirm HOPS_V1.spec
```
## Çalıştırma İpuçları

* Uygulama ilk açıldığında Dashboard ekranı otomatik olarak yüklenir ve dosya yapısı ile veritabanı kayıt sayısına dair durum mesajı gösterir.
* Uygulamayı başlatmadan önce kullanıcının ana dizini altında `HOPS_V1` klasörünü oluşturmak için yazma izni bulunduğundan emin olun. `core/installer.ensure_structure()` fonksiyonu bu klasörleri oluşturur ve yazma testi yapar; izin hatalarında uygulama başlangıçta uyarı vererek sonlanır.
* Masaüstü kısayolları artık Windows, macOS ve Linux platformlarında desteklenir. Linux için `.desktop`, macOS için `.command` dosyası, Windows için `.lnk` kısayolu oluşturulur. Masaüstü dizini bulunamazsa ev dizini kullanılır ve oluşturma hataları uyarı olarak raporlanır.