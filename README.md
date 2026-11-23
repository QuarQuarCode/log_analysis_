# 🛡️ Güvenlik Log Analiz ve Takip Paneli (Security Log Analysis & SOC Dashboard)

Bu proje, örnek kimlik doğrulama (login) kayıtlarını analiz ederek şüpheli IP adreslerini ve anormal giriş denemelerini tespit eden, **Python** ve **Streamlit** tabanlı bir güvenlik izleme ve olay müdahale (SOC) prototipidir.

Sistem hem **komut satırı (CLI)** üzerinden hızlı raporlama ve metin tabanlı alarm üretimi hem de **web arayüzü** üzerinden veritabanı destekli alarm yönetimi, risk sınıflandırması ve karantina takibi sunar.

---

## 🚀 Mevcut Özellikler

* **Statik Log Ayrıştırma (`log_analysis.py`):** `login_logs.txt` dosyasındaki ham giriş kayıtlarını tarar; IP bazlı başarılı ve başarısız giriş sayılarını zaman damgalarıyla birlikte analiz eder.
* **Dinamik Eşik ve Risk Derecelendirme:** Belirlenen başarısız giriş eşiğine göre güvenlik alarmları üretir ve deneme sayısına göre olayları **Düşük**, **Orta** veya **Yüksek Risk** olarak sınıflandırır.
* **Etkileşimli Web Paneli (`app.py`):**
  * **Giriş Kontrolü:** Oturum tabanlı yetkilendirme ekranı.
  * **Durum Paneli:** Toplam giriş istatistikleri, grafiksel dağılımlar, IP bazlı yoğunluk analizi ve son güvenlik olayları.
  * **Alarm Merkezi:** IP ve duruma göre filtreleme, alarmlara **Analist Notu** ekleme, olayları **Karantinaya Alma** veya **False Positive (Yoksayıldı)** olarak işaretleme.
  * **Karantina Merkezi:** Karantinaya alınan tehditleri izleme ve gerektiğinde tekrar inceleme kuyruğuna geri alma.
* **Kalıcı Veri Saklama:** Tespit edilen tüm güvenlik olaylarını, durum güncellemelerini ve analist notlarını **SQLite (`security.db`)** veritabanında saklar.
* **CLI Raporlama Desteği (`main.py`):** Terminal üzerinden hızlı özet raporlar sunar, en çok başarısız giriş yapan IP'leri sıralar ve alarmları `security_alerts.txt` dosyasına kaydeder.

---

## 🔮 Yol Haritası ve Planlanan Geliştirmeler (Roadmap)

Şu anki sürüm, manuel hazırlanan statik log dosyaları (`login_logs.txt`) üzerinden IP bazlı toplam başarısız giriş sayılarını analiz etmektedir. Projenin sonraki aşamalarında şu geliştirmeler hedeflenmektedir:

* [ ] **Zaman Pencereli Brute-Force Tespiti:** `log_analysis.py` içerisinde toplanan zaman damgalarını (`failed_times_by_ip`) kullanarak belirli bir zaman aralığında (örneğin *60 saniye içinde 5 başarısız deneme*) gerçekleşen gerçek kaba kuvvet (brute-force) saldırılarını tespit etme.
* [ ] **Canlı Log İzleme (Real-Time Monitoring):** Log dosyasına yeni eklenen satırları anlık olarak takip edip otomatik alarm tetikleme.
* [ ] **Dinamik Dosya Yükleme:** Web arayüzü üzerinden farklı `.log` veya `.txt` dosyalarını yükleyerek analiz edebilme.
* [ ] **Kimlik Doğrulama Güvenliği:** Panel giriş bilgilerini düz metin yerine hash (SHA-256 / bcrypt) ve ortam değişkenleri (`.env`) ile yönetme.

---

## 🛠️ Kullanılan Teknolojiler ve Kütüphaneler

* **Programlama Dili:** Python 3
* **Web Arayüzü:** Streamlit
* **Veritabanı:** SQLite3
* **Standart Kütüphaneler:** `datetime`, Dosya İşlemleri (File I/O)

---

## 📂 Proje Mimarisi

```text
├── app.py                # Streamlit tabanlı web arayüzü ve SOC yönetim paneli
├── main.py               # Komut satırı (CLI) ana çalıştırma dosyası
├── log_analysis.py       # Log kayıtlarını ayrıştıran ve istatistik üreten modül
├── alerts.py             # Eşik değerine göre alarm üreten ve dosyaya yazan modül
├── reports.py            # Terminal çıktısı için özet ve IP sıralama raporları
├── login_logs.txt        # Analiz edilen örnek giriş kayıtları
├── security.db           # Alarm ve karantina kayıtlarının tutulduğu SQLite veritabanı
└── security_alerts.txt   # CLI modunda üretilen güvenlik uyarı kayıtları
```

---

## ⚙️ Kurulum ve Çalıştırma

1. **Depoyu bilgisayarınıza klonlayın:**
   ```bash
   git clone https://github.com
   cd log_analysis_
   ```

2. **Gerekli kütüphaneyi yükleyin:**
   ```bash
   pip install streamlit
   ```

3. **Web Arayüzünü (Dashboard) Başlatın:**
   ```bash
   streamlit run app.py
   ```
   * **Varsayılan Giriş Bilgileri:** Kullanıcı Adı: `admin` | Şifre: `admin123`

4. **Komut Satırı (CLI) Modunu Çalıştırmak İçin:**
   ```bash
   python main.py
   ```
