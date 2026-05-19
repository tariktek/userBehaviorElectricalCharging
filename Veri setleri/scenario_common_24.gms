SETS
   t  Hours / 1*24 /;

PARAMETERS
   price_grid(t)
   price_solar(t)
   price_wind(t)
   solar_cap(t)
   wind_cap(t)
   home(t)
   drive_consumption(t)
   load_house(t);

SCALARS
   daily_ev_need      / 7.1000 /
   ev_charge_max      / 2.3000 /
   SoE_ini            / 20 /
   SoE_min            / 10 /
   SoE_max            / 88.5 /
   CE_EV              / 0.95 /
   SoE_batt_ini       / 0 /
   battery_capacity   / 10 /
   batt_charge_max    / 2.3 /
   batt_discharge_max / 2.3 /
   CE_batt            / 0.95 /
   away_hours;

price_grid('1')  = 2.50;  price_solar('1') = 0.20; price_wind('1') = 0.50; solar_cap('1') = 0.00; wind_cap('1') = 1.49; load_house('1') = 2.55014; home('1') = 1;
price_grid('2')  = 2.50;  price_solar('2') = 0.20; price_wind('2') = 0.50; solar_cap('2') = 0.00; wind_cap('2') = 1.18; load_house('2') = 2.52340; home('2') = 1;
price_grid('3')  = 2.50;  price_solar('3') = 0.20; price_wind('3') = 0.50; solar_cap('3') = 0.00; wind_cap('3') = 0.93; load_house('3') = 2.58233; home('3') = 1;
price_grid('4')  = 2.50;  price_solar('4') = 0.20; price_wind('4') = 0.50; solar_cap('4') = 0.00; wind_cap('4') = 0.72; load_house('4') = 2.54167; home('4') = 1;
price_grid('5')  = 2.50;  price_solar('5') = 0.20; price_wind('5') = 0.50; solar_cap('5') = 0.00; wind_cap('5') = 0.75; load_house('5') = 2.47573; home('5') = 1;
price_grid('6')  = 2.50;  price_solar('6') = 0.20; price_wind('6') = 0.50; solar_cap('6') = 0.0101; wind_cap('6') = 1.02; load_house('6') = 2.47623; home('6') = 1;
price_grid('7')  = 2.50;  price_solar('7') = 0.20; price_wind('7') = 0.50; solar_cap('7') = 0.2018; wind_cap('7') = 1.35; load_house('7') = 2.45580; home('7') = 1;
price_grid('8')  = 3.30;  price_solar('8') = 0.20; price_wind('8') = 0.50; solar_cap('8') = 0.4779; wind_cap('8') = 1.74; load_house('8') = 2.44720; home('8') = 0;
price_grid('9')  = 3.30;  price_solar('9') = 0.20; price_wind('9') = 0.50; solar_cap('9') = 0.7000; wind_cap('9') = 2.15; load_house('9') = 2.44173; home('9') = 0;
price_grid('10') = 3.30;  price_solar('10')= 0.20; price_wind('10')= 0.50; solar_cap('10')= 0.8466; wind_cap('10')= 2.38; load_house('10')= 3.14613; home('10')= 0;
price_grid('11') = 3.30;  price_solar('11')= 0.20; price_wind('11')= 0.50; solar_cap('11')= 0.8558; wind_cap('11')= 2.44; load_house('11')= 2.66173; home('11')= 0;
price_grid('12') = 3.30;  price_solar('12')= 0.20; price_wind('12')= 0.50; solar_cap('12')= 0.7670; wind_cap('12')= 2.33; load_house('12')= 2.57600; home('12')= 0;
price_grid('13') = 3.30;  price_solar('13')= 0.20; price_wind('13')= 0.50; solar_cap('13')= 0.5687; wind_cap('13')= 2.06; load_house('13')= 2.61587; home('13')= 0;
price_grid('14') = 3.30;  price_solar('14')= 0.20; price_wind('14')= 0.50; solar_cap('14')= 0.2649; wind_cap('14')= 1.56; load_house('14')= 2.16240; home('14')= 0;
price_grid('15') = 3.30;  price_solar('15')= 0.20; price_wind('15')= 0.50; solar_cap('15')= 0.0417; wind_cap('15')= 1.19; load_house('15')= 1.29440; home('15')= 0;
price_grid('16') = 3.30;  price_solar('16')= 0.20; price_wind('16')= 0.50; solar_cap('16')= 0.00; wind_cap('16')= 1.00; load_house('16')= 1.90917; home('16')= 0;
price_grid('17') = 3.30;  price_solar('17')= 0.20; price_wind('17')= 0.50; solar_cap('17')= 0.00; wind_cap('17')= 0.94; load_house('17')= 1.39010; home('17')= 0;
price_grid('18') = 3.30;  price_solar('18')= 0.20; price_wind('18')= 0.50; solar_cap('18')= 0.00; wind_cap('18')= 1.14; load_house('18')= 1.63207; home('18')= 0;
price_grid('19') = 5.00;  price_solar('19')= 0.20; price_wind('19')= 0.50; solar_cap('19')= 0.00; wind_cap('19')= 1.56; load_house('19')= 1.46190; home('19') = 1;
price_grid('20') = 5.00;  price_solar('20')= 0.20; price_wind('20')= 0.50; solar_cap('20')= 0.00; wind_cap('20')= 2.13; load_house('20')= 0.73230; home('20') = 1;
price_grid('21') = 5.00;  price_solar('21')= 0.20; price_wind('21')= 0.50; solar_cap('21')= 0.00; wind_cap('21')= 2.66; load_house('21')= 0.41230; home('21') = 1;
price_grid('22') = 5.00;  price_solar('22')= 0.20; price_wind('22')= 0.50; solar_cap('22')= 0.00; wind_cap('22')= 3.03; load_house('22')= 0.43393; home('22') = 1;
price_grid('23') = 5.00;  price_solar('23')= 0.20; price_wind('23')= 0.50; solar_cap('23')= 0.00; wind_cap('23')= 3.32; load_house('23')= 0.44373; home('23') = 1;
price_grid('24') = 2.50;  price_solar('24')= 0.20; price_wind('24')= 0.50; solar_cap('24')= 0.00; wind_cap('24')= 3.54; load_house('24')= 0.44997; home('24') = 1;

drive_consumption(t) = 0;
away_hours = SUM(t$(home(t) = 0), 1);
drive_consumption(t)$(home(t) = 0 AND away_hours > 0) = daily_ev_need / away_hours;
