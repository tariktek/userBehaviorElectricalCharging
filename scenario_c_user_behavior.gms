$TITLE Hybrid Grid + EV Charging Optimization with Real Data

SETS
   t  Saatler / 1*24 /;

PARAMETERS
   price_grid(t)   'Saatlik şebeke fiyatı (TL/kWh)'
   price_solar(t)  'Saatlik solar üretim maliyeti (TL/kWh)'
   price_wind(t)   'Saatlik rüzgar üretim maliyeti (TL/kWh)'
   solar_cap(t)    'Saatlik solar kapasitesi (kW)'
   wind_cap(t)     'Saatlik rüzgar kapasitesi (kW)'
   home(t)         'EV evde mi? 1=evde, 0=dışarıda'
   drive_consumption(t) 'EV dışarıdayken saatlik sürüş tüketimi (kWh)'
   load_house(t)   'Saatlik ev içi talep (kW)';

SCALARS
   daily_ev_need   'Günlük EV şarj ihtiyacı (kWh)' / 7.1000 /
   ev_charge_max   '220V ev şarj aleti limiti (kW)' / 2.3000 /
   SoE_ini         'Başlangıç batarya durumu (kWh)' / 20 /
   SoE_min         'Minimum batarya durumu (kWh)' / 10 /
   SoE_max         'Batarya maksimum kapasitesi (kWh)' / 88.5000 /
   CE_EV           'EV şarj verimi' / 0.95 /
   SoE_batt_ini    'Solar batarya başlangıç durumu (kWh)' / 5 /
   battery_capacity 'Solar batarya kapasitesi (kWh)' / 10 /
   batt_charge_max 'Solar batarya şarj gücü limiti (kW)' / 2.3 /
   batt_discharge_max 'Solar batarya deşarj gücü limiti (kW)' / 2.3 /
   CE_batt         'Solar batarya verimi' / 0.95 /
   away_hours      'EV evde değilken geçen saat sayısı';

* 1. Gerçek veri: Veri setindeki fiyat, solar/ruzgar kapasitesi ve tüketim değerleri.
price_grid('1')  = 2.50;  price_solar('1') = 0.20; price_wind('1') = 0.50; solar_cap('1') = 0.00; wind_cap('1') = 1.49; load_house('1') = 2.55014; home('1') = 1;
price_grid('2')  = 2.50;  price_solar('2') = 0.20; price_wind('2') = 0.50; solar_cap('2') = 0.00; wind_cap('2') = 1.18; load_house('2') = 2.52340; home('2') = 1;
price_grid('3')  = 2.50;  price_solar('3') = 0.20; price_wind('3') = 0.50; solar_cap('3') = 0.00; wind_cap('3') = 0.93; load_house('3') = 2.58233; home('3') = 1;
price_grid('4')  = 2.50;  price_solar('4') = 0.20; price_wind('4') = 0.50; solar_cap('4') = 0.00; wind_cap('4') = 0.72; load_house('4') = 2.54167; home('4') = 1;
price_grid('5')  = 2.50;  price_solar('5') = 0.20; price_wind('5') = 0.50; solar_cap('5') = 0.00; wind_cap('5') = 0.75; load_house('5') = 2.47573; home('5') = 1;
price_grid('6')  = 2.50;  price_solar('6') = 0.20; price_wind('6') = 0.50; solar_cap('6') = 0.0101; wind_cap('6') = 1.02; load_house('6') = 2.47623; home('6') = 1;
price_grid('7')  = 2.50;  price_solar('7') = 0.20; price_wind('7') = 0.50; solar_cap('7') = 0.2018; wind_cap('7') = 1.35; load_house('7') = 2.45580; home('7') = 1;
price_grid('8')  = 3.30;  price_solar('8') = 0.20; price_wind('8') = 0.50; solar_cap('8') = 0.4779; wind_cap('8') = 1.74; load_house('8') = 2.44720; home('8') = 0;
price_grid('9')  = 3.30;  price_solar('9') = 0.20; price_wind('9') = 0.50; solar_cap('9') = 0.7000; wind_cap('9') = 2.15; load_house('9') = 2.44173; home('9') = 0;
price_grid('10') = 3.30;  price_solar('10')= 0.20; price_wind('10')= 0.50; solar_cap('10')= 0.8466; wind_cap('10')= 2.38; load_house('10')= 3.14613; home('10') = 0;
price_grid('11') = 3.30;  price_solar('11')= 0.20; price_wind('11')= 0.50; solar_cap('11')= 0.8558; wind_cap('11')= 2.44; load_house('11')= 2.66173; home('11') = 0;
price_grid('12') = 3.30;  price_solar('12')= 0.20; price_wind('12')= 0.50; solar_cap('12')= 0.7670; wind_cap('12')= 2.33; load_house('12')= 2.57600; home('12') = 0;
price_grid('13') = 3.30;  price_solar('13')= 0.20; price_wind('13')= 0.50; solar_cap('13')= 0.5687; wind_cap('13')= 2.06; load_house('13')= 2.61587; home('13') = 0;
price_grid('14') = 3.30;  price_solar('14')= 0.20; price_wind('14')= 0.50; solar_cap('14')= 0.2649; wind_cap('14')= 1.56; load_house('14')= 2.16240; home('14') = 0;
price_grid('15') = 3.30;  price_solar('15')= 0.20; price_wind('15')= 0.50; solar_cap('15')= 0.0417; wind_cap('15')= 1.19; load_house('15')= 1.29440; home('15') = 0;
price_grid('16') = 3.30;  price_solar('16')= 0.20; price_wind('16')= 0.50; solar_cap('16')= 0.00; wind_cap('16')= 1.00; load_house('16')= 1.90917; home('16') = 0;
price_grid('17') = 3.30;  price_solar('17')= 0.20; price_wind('17')= 0.50; solar_cap('17')= 0.00; wind_cap('17')= 0.94; load_house('17')= 1.39010; home('17') = 0;
price_grid('18') = 3.30;  price_solar('18')= 0.20; price_wind('18')= 0.50; solar_cap('18')= 0.00; wind_cap('18')= 1.14; load_house('18')= 1.63207; home('18') = 0;
price_grid('19') = 5.00;  price_solar('19')= 0.20; price_wind('19')= 0.50; solar_cap('19')= 0.00; wind_cap('19')= 1.56; load_house('19')= 1.46190; home('19') = 1;
price_grid('20') = 5.00;  price_solar('20')= 0.20; price_wind('20')= 0.50; solar_cap('20')= 0.00; wind_cap('20')= 2.13; load_house('20')= 0.73230; home('20') = 1;
price_grid('21') = 5.00;  price_solar('21')= 0.20; price_wind('21')= 0.50; solar_cap('21')= 0.00; wind_cap('21')= 2.66; load_house('21')= 0.41230; home('21') = 1;
price_grid('22') = 5.00;  price_solar('22')= 0.20; price_wind('22')= 0.50; solar_cap('22')= 0.00; wind_cap('22')= 3.03; load_house('22')= 0.43393; home('22') = 1;
price_grid('23') = 5.00;  price_solar('23')= 0.20; price_wind('23')= 0.50; solar_cap('23')= 0.00; wind_cap('23')= 3.32; load_house('23')= 0.44373; home('23') = 1;
price_grid('24') = 2.50;  price_solar('24')= 0.20; price_wind('24')= 0.50; solar_cap('24')= 0.00; wind_cap('24')= 3.54; load_house('24')= 0.44997; home('24') = 1;

drive_consumption(t) = 0;
away_hours = SUM(t$(home(t) = 0), 1);
drive_consumption(t)$(home(t) = 0 AND away_hours > 0) = daily_ev_need / away_hours;

PARAMETERS cheapest_price(t) 'Saatlik en düşük kaynak fiyatı (TL/kWh)';
cheapest_price(t) = min(price_grid(t), min(price_solar(t), price_wind(t)));

VARIABLES
   Pgrid(t)         'Şebekeden alınan enerji (kW)'
   Ppv(t)           'Solar PV doğrudan kullanımı (kW)'
   Pwind(t)         'Rüzgar enerjisi kullanımı (kW)'
   P_batt_charge(t) 'Solar bataryaya şarj gücü (kW)'
   P_batt_charge_solar(t) 'Solar kaynaklı batarya şarj gücü (kW)'
   P_batt_charge_wind(t)  'Rüzgar kaynaklı batarya şarj gücü (kW)'
   P_batt_discharge(t) 'Solar bataryadan deşarj gücü (kW)'
   P_ev(t)          'EV şarj gücü (kW)'
   SoE_ev(t)        'EV batarya durumu (kWh)'
   SoE_batt(t)      'Solar batarya doluluk durumu (kWh)'
   total_cost       'Toplam maliyet (TL)';

POSITIVE VARIABLES Pgrid, Ppv, Pwind, P_batt_charge, P_batt_charge_solar, P_batt_charge_wind, P_batt_discharge, P_ev, SoE_ev, SoE_batt;
BINARY VARIABLES b_batt_ch(t), b_batt_dis(t);

EQUATIONS
   cost_def              'Toplam maliyet'
   power_balance(t)      'Enerji denge denklemi'
   solar_dispatch(t)     'Solar üretim dağılımı: direkt kullanım + depolama'
   wind_limit(t)         'Rüzgar üretim sınırı'
   batt_charge_split(t)  'Batarya şarjının solar ve rüzgar kaynaklarına ayrılması'
   ev_home_limit(t)      'EV sadece evdeyken şarj olur'
   ev_charge_need        'Günlük EV şarj ihtiyacı'
   ev_soe_init           'Başlangıç batarya durumu'
   ev_soe_balance(t)     'EV batarya enerjisi dengesi'
   ev_soe_final          'Günün sonunda gerekli EV batarya durumu'
   ev_soe_min_limit(t)   'EV batarya minimum limiti'
   ev_soe_max_limit(t)   'EV batarya maksimum limiti'
   batt_init             'Solar batarya başlangıç durumu'
   batt_discharge_init   'Solar batarya ilk saat deşarjı'
   batt_balance(t)       'Solar batarya enerji dengesi'
   batt_final            'Solar batarya günlük denge'
   batt_max(t)           'Solar batarya kapasite limiti'
   batt_charge_limit(t)  'Solar batarya şarj gücü limiti'
   batt_discharge_limit(t) 'Solar batarya deşarj gücü limiti'
   batt_ch_dis_excl(t)   'Solar batarya aynı anda şarj ve deşarj olamaz'
   batt_charge_bigM(t)   'Solar batarya şarj ikili değişken bağlantısı'
   batt_discharge_bigM(t) 'Solar batarya deşarj ikili değişken bağlantısı';

cost_def..       total_cost =E= SUM(t, price_grid(t)*Pgrid(t)
                                       + price_solar(t)*(Ppv(t) + P_batt_charge_solar(t))
                                       + price_wind(t)*(Pwind(t) + P_batt_charge_wind(t)));

power_balance(t)..  Pgrid(t) + Ppv(t) + Pwind(t) + P_batt_discharge(t) =E= load_house(t) + P_ev(t) + P_batt_charge(t);

solar_dispatch(t)..  Ppv(t) + P_batt_charge_solar(t) =L= solar_cap(t);

wind_limit(t)..     Pwind(t) + P_batt_charge_wind(t) =L= wind_cap(t);

batt_charge_split(t).. P_batt_charge(t) =E= P_batt_charge_solar(t) + P_batt_charge_wind(t);

ev_home_limit(t)..  P_ev(t) =L= ev_charge_max * home(t);

batt_charge_limit(t)..    P_batt_charge(t) =L= batt_charge_max;

batt_discharge_limit(t).. P_batt_discharge(t) =L= batt_discharge_max;

* Prevent simultaneous battery charge and discharge
batt_ch_dis_excl(t)..    b_batt_ch(t) + b_batt_dis(t) =L= 1;

batt_charge_bigM(t)..     P_batt_charge(t) =L= batt_charge_max * b_batt_ch(t);

batt_discharge_bigM(t)..  P_batt_discharge(t) =L= batt_discharge_max * b_batt_dis(t);

ev_charge_need..   SUM(t, P_ev(t) * CE_EV) =G= daily_ev_need;

ev_soe_init..      SoE_ev('1') =E= SoE_ini + P_ev('1') * CE_EV - drive_consumption('1');

ev_soe_balance(t)$(ord(t) > 1)..  SoE_ev(t) =E= SoE_ev(t-1) + P_ev(t) * CE_EV - drive_consumption(t);

ev_soe_final..     SoE_ev('24') =G= SoE_ini;

ev_soe_min_limit(t).. SoE_ev(t) =G= SoE_min;
ev_soe_max_limit(t).. SoE_ev(t) =L= SoE_max;

batt_init..         SoE_batt('1') =E= SoE_batt_ini + P_batt_charge('1') * CE_batt - P_batt_discharge('1') / CE_batt;

batt_discharge_init.. P_batt_discharge('1') =E= 0;

batt_balance(t)$(ord(t) > 1)..  SoE_batt(t) =E= SoE_batt(t-1) + P_batt_charge(t) * CE_batt - P_batt_discharge(t) / CE_batt;

batt_final..        SoE_batt('24') =G= 0;

batt_max(t)..       SoE_batt(t) =L= battery_capacity;

MODEL hybrid_ev /ALL/;

SOLVE hybrid_ev MINIMIZING total_cost USING MIP;

DISPLAY total_cost.l, Pgrid.l, Ppv.l, Pwind.l, P_batt_charge.l, P_batt_charge_solar.l, P_batt_charge_wind.l, P_batt_discharge.l, P_ev.l, SoE_ev.l, SoE_batt.l, drive_consumption, cheapest_price;

* Notlar:
* - Batarya modeli SoE_ev(t) ile EV batarya durumu için enerji akışını simüle eder.
* - Solar batarya modeli SoE_batt(t), P_batt_charge(t) ve P_batt_discharge(t) değişkenleriyle kurulmuştur.
* - Solar panel modeli solar_cap(t) ve Ppv(t) ile tanımlanmıştır.
* - Solar batarya, gündüz güneş enerjisini depolayarak akşam kullanıma sunar.
* - Rüzgar modeli wind_cap(t) ve Pwind(t) ile tanımlanmıştır.
* - Hibrit şebeke modelinde şebeke maliyeti, solar ve rüzgar kullanımı birlikte minimize edilir.
* - Kullanıcı davranışı home(t) ile EV'nin evde olduğu saatleri belirler.
