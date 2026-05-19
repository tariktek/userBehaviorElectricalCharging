$TITLE Scenario B - Hybrid Grid with Solar and Wind

$include "Veri setleri/scenario_common_24.gms"

VARIABLES
   Pgrid(t)
   Ppv(t)
   Pwind(t)
   P_ev(t)
   total_cost;

POSITIVE VARIABLES Pgrid, Ppv, Pwind, P_ev;

EQUATIONS
   cost_def
   power_balance(t)
   solar_limit(t)
   wind_limit(t)
   ev_charge_limit(t)
   ev_charge_need;

cost_def..          total_cost =E= SUM(t, price_grid(t)*Pgrid(t)
                                           + price_solar(t)*Ppv(t)
                                           + price_wind(t)*Pwind(t));
power_balance(t)..  Pgrid(t) + Ppv(t) + Pwind(t) =E= load_house(t) + P_ev(t);
solar_limit(t)..    Ppv(t) =L= solar_cap(t);
wind_limit(t)..     Pwind(t) =L= wind_cap(t);
ev_charge_limit(t).. P_ev(t) =L= ev_charge_max;
ev_charge_need..    SUM(t, P_ev(t) * CE_EV) =G= daily_ev_need;

MODEL scenario_b_hybrid_grid /ALL/;
SOLVE scenario_b_hybrid_grid MINIMIZING total_cost USING LP;

DISPLAY total_cost.l, Pgrid.l, Ppv.l, Pwind.l, P_ev.l;
