# Elektrikli Araç Şarjı ve Hibrit Enerji Optimizasyonu

Bu proje, elektrikli aracın evde şarj edilmesini; güneş, rüzgar, şebeke ve güneş bataryası ile birlikte en düşük maliyetle planlayan bir GAMS optimizasyon modelidir.

Ana model dosyası:

```text
scenario_c_user_behavior.gms
```

Model, yalnızca “talebi en ucuz kaynakla karşıla” yaklaşımıyla sınırlı değildir. EV batarya durumu, aracın evde olup olmaması, ev tüketimi, güneş bataryası, yenilenebilir üretim limitleri ve saatlik şebeke fiyatları birlikte değerlendirilir.

---

## Model Özeti

Model türü:

```text
Mixed Integer Programming (MIP)
```

Çözüm hedefi:

```text
Toplam enerji maliyetini minimize etmek
```

Zaman aralığı:

```text
24 saatlik günlük optimizasyon
```

Kullanılan enerji kaynakları:

| Kaynak | Açıklama |
|---|---|
| Şebeke | Saatlik değişen elektrik fiyatı ile satın alınan enerji |
| Solar PV | Güneş üretiminin doğrudan kullanımı |
| Rüzgar | Saatlik rüzgar kapasitesi kadar kullanılabilen enerji |
| Solar batarya | Güneş enerjisini depolayıp sonraki saatlerde kullanma |

---

## Amaç Fonksiyonu

Modelin amacı toplam maliyeti minimize etmektir:

```text
total_cost =
SUM(t,
    price_grid(t)  * Pgrid(t)
  + price_solar(t) * Ppv(t)
  + price_wind(t)  * Pwind(t)
)
```

Batarya deşarjının doğrudan ayrıca maliyeti yoktur; çünkü bataryadaki enerji daha önce solar üretimden şarj edilmiştir. Bu nedenle model, güneş üretimini doğrudan kullanmak veya bataryaya aktarmak arasında karar verir.

---

## Karar Değişkenleri

| Değişken | Anlamı |
|---|---|
| `Pgrid(t)` | Şebekeden alınan enerji |
| `Ppv(t)` | Solar PV’den doğrudan kullanılan enerji |
| `Pwind(t)` | Rüzgardan kullanılan enerji |
| `P_batt_charge(t)` | Solar bataryaya şarj edilen enerji |
| `P_batt_discharge(t)` | Solar bataryadan çekilen enerji |
| `P_ev(t)` | EV’ye verilen şarj gücü |
| `SoE_ev(t)` | EV batarya doluluk durumu |
| `SoE_batt(t)` | Solar batarya doluluk durumu |
| `b_batt_ch(t)` | Solar batarya şarj modunda mı? |
| `b_batt_dis(t)` | Solar batarya deşarj modunda mı? |

İkili değişkenler sayesinde solar bataryanın aynı saat içinde hem şarj hem de deşarj yapması engellenir.

---

## Temel Parametreler

| Parametre | Değer | Açıklama |
|---|---:|---|
| `daily_ev_need` | 5.68 kWh | Günlük EV enerji ihtiyacı |
| `ev_charge_max` | 2.3 kW | 220V ev tipi şarj limiti |
| `SoE_ini` | 20 kWh | EV başlangıç batarya seviyesi |
| `SoE_min` | 10 kWh | EV minimum batarya seviyesi |
| `SoE_max` | 88.5 kWh | EV batarya kapasitesi |
| `CE_EV` | 0.95 | EV şarj verimi |
| `SoE_batt_ini` | 0 kWh | Solar batarya başlangıç seviyesi |
| `battery_capacity` | 10 kWh | Solar batarya kapasitesi |
| `batt_charge_max` | 2.3 kW | Solar batarya şarj limiti |
| `batt_discharge_max` | 2.3 kW | Solar batarya deşarj limiti |
| `CE_batt` | 0.95 | Solar batarya verimi |

---

## Kısıtlar

### Enerji Dengesi

Her saat için sisteme giren enerji, çıkan enerjiye eşit olmalıdır:

```text
Pgrid(t) + Ppv(t) + Pwind(t) + P_batt_discharge(t)
=
load_house(t) + P_ev(t) + P_batt_charge(t)
```

Bu denklem ev tüketimini, EV şarjını ve batarya şarjını aynı enerji dengesi içinde toplar.

### Solar Üretim Dağılımı

Solar üretim ya doğrudan kullanılır ya da bataryaya şarj edilir:

```text
Ppv(t) + P_batt_charge(t) <= solar_cap(t)
```

### Rüzgar Kapasitesi

```text
Pwind(t) <= wind_cap(t)
```

### EV Sadece Evdeyken Şarj Olur

```text
P_ev(t) <= ev_charge_max * home(t)
```

`home(t) = 1` ise araç evdedir ve şarj olabilir.  
`home(t) = 0` ise araç dışarıdadır ve şarj olamaz.

### Günlük EV Şarj İhtiyacı

```text
SUM(t, P_ev(t) * CE_EV) >= daily_ev_need
```

Model gün sonunda aracın günlük enerji ihtiyacını karşılamak zorundadır.

### EV Batarya Durumu

EV bataryası şarjla artar, araç dışarıdayken sürüş tüketimiyle azalır:

```text
SoE_ev(t) = SoE_ev(t-1) + P_ev(t) * CE_EV - drive_consumption(t)
```

Batarya seviyesi daima minimum ve maksimum sınırlar arasında tutulur:

```text
SoE_min <= SoE_ev(t) <= SoE_max
```

### Solar Batarya Durumu

Solar batarya güneşten şarj olur, ihtiyaç olduğunda deşarj olur:

```text
SoE_batt(t) =
SoE_batt(t-1)
+ P_batt_charge(t) * CE_batt
- P_batt_discharge(t) / CE_batt
```

Batarya kapasite limiti:

```text
SoE_batt(t) <= battery_capacity
```

Aynı anda şarj ve deşarj engeli:

```text
b_batt_ch(t) + b_batt_dis(t) <= 1
```

---

## Kullanılan Veriler

Modelde 24 saatlik gerçekçi örnek veri doğrudan `scenario_c_user_behavior.gms` içine yazılmıştır:

| Veri | GAMS parametresi |
|---|---|
| Saatlik şebeke fiyatı | `price_grid(t)` |
| Solar üretim maliyeti | `price_solar(t)` |
| Rüzgar üretim maliyeti | `price_wind(t)` |
| Solar kapasitesi | `solar_cap(t)` |
| Rüzgar kapasitesi | `wind_cap(t)` |
| Ev tüketimi | `load_house(t)` |
| Araç evde mi? | `home(t)` |

Ek veri hazırlama dosyaları `Veri setleri/` klasöründedir. Bu dosyalar daha uzun zaman aralığı için CSV verilerini GAMS formatına çevirmek amacıyla kullanılır.

---

## Dosya Yapısı

```text
Bitirme_Calismasi/
├── README.md
├── scenario_c_user_behavior.gms       # Senaryo C: kullanıcı davranışlı nihai model
├── scenario_a_full_grid.gms           # Senaryo A: sadece şebeke
├── scenario_b_hybrid_grid.gms         # Senaryo B: şebeke + solar + rüzgar
├── results_summary.txt
├── userInterface/
│   ├── app.py                         # Streamlit arayüzü
│   ├── requirements.txt
│   └── README.md
└── Veri setleri/
    ├── merged_energy_2025.csv
    ├── energy_prices.csv
    ├── user_behavior.csv
    ├── vehicle_specs.csv
    ├── scenario_common_24.gms
    ├── prepare_gams.py
    ├── prepare_scenarios.py
    ├── merge_energy.py
    ├── convert_power.py
    └── check_quality.py
```

---

## Senaryo Karşılaştırması

Nihai çalışmada üç farklı çıktı alınır. Bu üç senaryo aynı 24 saatlik ev tüketimi, fiyat, solar ve rüzgar verisini kullanır.

| Senaryo | Dosya | Model | İçerik | Toplam Maliyet |
|---|---|---|---|---:|
| A - Full Şebeke | `scenario_a_full_grid.gms` | LP | Sadece şebeke kullanılır | 157.6198 TL |
| B - Hibrit Şebeke | `scenario_b_hybrid_grid.gms` | LP | Şebeke + solar + rüzgar kullanılır | 51.3304 TL |
| C - Kullanıcı Davranışlı Hibrit | `scenario_c_user_behavior.gms` | MIP | Şebeke + solar + rüzgar + solar batarya + EV batarya + evde/dışarıda davranışı | 49.5261 TL |

Bu sonuçlara göre, yalnızca şebeke kullanımına kıyasla hibrit sistem maliyeti ciddi biçimde düşürür. Kullanıcı davranışı ve solar batarya eklendiğinde ek iyileşme sağlanır.

Tasarruf özeti:

```text
A -> B: 106.2894 TL
B -> C:   1.8043 TL
A -> C: 108.0937 TL
```

---

## Çalıştırma

### Ana Modeli Çalıştırma

Proje klasöründeyken:

```bash
gams scenario_c_user_behavior.gms
```

Alternatif olarak tam dosya yolu ile:

```bash
gams "d:\Users\tarik\OneDrive\Desktop\Bitirme_Calismasi\scenario_c_user_behavior.gms"
```

GAMS `PATH` değişkeninde yoksa:

```bash
"D:\GAMS\53\gams.exe" "d:\Users\tarik\OneDrive\Desktop\Bitirme_Calismasi\scenario_c_user_behavior.gms"
```

### Üç Senaryoyu Çalıştırma

```bash
gams scenario_a_full_grid.gms
gams scenario_b_hybrid_grid.gms
gams scenario_c_user_behavior.gms
```

GAMS `PATH` değişkeninde yoksa:

```bash
"D:\GAMS\53\gams.exe" "scenario_a_full_grid.gms"
"D:\GAMS\53\gams.exe" "scenario_b_hybrid_grid.gms"
"D:\GAMS\53\gams.exe" "scenario_c_user_behavior.gms"
```

### Streamlit Arayüzünü Çalıştırma

```bash
cd "d:\Users\tarik\OneDrive\Desktop\Bitirme_Calismasi"
python -m streamlit run userInterface\app.py
```

Varsayılan adres:

```text
http://localhost:8501
```

Arayüzde kullanıcı şu bilgileri seçer:

- Araç modeli: şu an yalnızca `TOGG T10F Long Range`
- Şarj tipi: şu an yalnızca `Ev tipi 220V priz - 2.3 kW`
- Ev ile iş arası tek yön mesafe
- Çalışılan günler
- Evden çıkış saati
- Eve giriş saati

Bu bilgilerden günlük EV enerji ihtiyacı hesaplanır ve `scenario_c_user_behavior.gms` içindeki `daily_ev_need`, `ev_charge_max`, `SoE_max` ve `home(t)` değerleri güncellenir. Ardından Scenario C optimizasyonu arayüzden çalıştırılabilir.

---

## Çıktılar

GAMS çözüm sonunda şu değerleri raporlar:

| Çıktı | Açıklama |
|---|---|
| `total_cost.l` | Minimum toplam maliyet |
| `Pgrid.l` | Saatlik şebeke kullanımı |
| `Ppv.l` | Saatlik doğrudan solar kullanım |
| `Pwind.l` | Saatlik rüzgar kullanımı |
| `P_batt_charge.l` | Solar batarya şarj programı |
| `P_batt_discharge.l` | Solar batarya deşarj programı |
| `P_ev.l` | EV şarj programı |
| `SoE_ev.l` | EV batarya seviyesi |
| `SoE_batt.l` | Solar batarya seviyesi |
| `drive_consumption` | Araç dışarıdayken saatlik sürüş tüketimi |
| `cheapest_price` | Her saat için en ucuz kaynak fiyatı |

---

## Modelin Karar Mantığı

Model şu sorulara aynı anda cevap verir:

- EV hangi saatlerde şarj edilmeli?
- Araç evde değilken batarya seviyesi nasıl azalır?
- Güneş enerjisi doğrudan mı kullanılmalı, bataryaya mı aktarılmalı?
- Rüzgar kapasitesi hangi saatlerde kullanılmalı?
- Şebekeden ne kadar enerji alınmalı?
- Pahalı saatlerde solar batarya deşarj edilerek maliyet azaltılabilir mi?

Bu nedenle mevcut model, eski README’de anlatılan basit LP modelinden daha kapsamlıdır. Solar batarya ve ikili değişkenler nedeniyle model MIP olarak çözülmektedir.

---

## Notlar

- `scenario_c_user_behavior.gms` ana ve güncel nihai modeldir.
- `scenario_a_full_grid.gms` ve `scenario_b_hybrid_grid.gms` karşılaştırma senaryolarıdır.
- GAMS demo lisansı satır/sütun sınırı nedeniyle büyük zaman aralıklarında kısıtlayıcı olabilir.

---

## Gelecek İyileştirmeler

- Tüm yıl için 8760 saatlik modelin lisans sınırı aşılmadan parçalı çözülmesi
- Solar batarya kapasitesinin karar değişkeni olarak optimize edilmesi
- Araç kullanım davranışının haftanın günlerine göre ayrıştırılması
- Şebekeye enerji satışı veya mahsuplaşma eklenmesi
- Çoklu EV şarj planlaması

---

**Son Güncelleme:** 17.05.2026
