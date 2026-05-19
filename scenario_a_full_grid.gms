$TITLE Scenario A - Full Grid EV Charging

$include "Veri setleri/scenario_common_24.gms"

VARIABLES
   Pgrid(t)
   P_ev(t)
   total_cost;

POSITIVE VARIABLES Pgrid, P_ev;

EQUATIONS
   cost_def
   power_balance(t)
   ev_charge_limit(t)
   ev_charge_need;

cost_def..          total_cost =E= SUM(t, price_grid(t) * Pgrid(t));
power_balance(t)..  Pgrid(t) =E= load_house(t) + P_ev(t);
ev_charge_limit(t).. P_ev(t) =L= ev_charge_max;
ev_charge_need..    SUM(t, P_ev(t) * CE_EV) =G= daily_ev_need;

MODEL scenario_a_full_grid /ALL/;
SOLVE scenario_a_full_grid MINIMIZING total_cost USING LP;

DISPLAY total_cost.l, Pgrid.l, P_ev.l;
