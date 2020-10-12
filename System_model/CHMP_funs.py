import numpy as np
import GDEx.GDEx_funs as gedx
import SGPRE.SGPRE_funs as sg

from GCHPc.gchpp_simple_model import GCHPpType, GCHPp, calculate_ht_mass_flow, calculate_lt_supply, calculate_orc_mass_flow, calculate_t_bo, calculate_t_hto
from GCHPc.demand import ComodityType, Demand
from GCHPc.orc_m01 import BinaryType, ORC
from GCHPc.brine_properties import Brine

from HTPE.htpe import get_recovery
import REDp.sgpre as sgp

class OutOffCHMPRange(Exception): pass

#======================Underground heat exchange================================================
def C1(p):
    DE=0
    DM={}
    return p, DE,DM

#======================Production well==========================================================
def C2(p):
    DE=0
    DM={}
    return p, DE, DM

#[HTPE]======================Electrolytic metal recovery ==============================================
def C3(p):
    metal_list = {'cu': 'Cu2+','au': 'Au+', 'as': 'As3-','sb': 'Sb3-',
                  'sr':'Sr2+', 'ba':'Ba2+', 'pb':'Pb2+', 'al':'Al3+',
                  'ag':'Ag+',  'co':'Co2+', 'zn':'Zn2+', 'li':'Li+',
                  'ni':'Ni2+', 'cd':'Cd2+', 'ti':'Ti4+', 'mo':'Mo4+'}
#    # only metals with a reduction potential or oxidation potentiel larger or equal to Cu2+ + 2e- -> Cu E0=0.3419 V
#    # valency state of the metals in solution should be taken into account
#    #----------Check if parameters are within allowed range, if not stops ans returns nan--------
#    if  (not 30 <= p['t'] <= 200) or (not 1  <= p['p'] <= 30 ):
#        # ....Add somekind of logging functionality....        
#        return p,np.nan,{key:np.nan for key in metal_list}
#    
    DE=0
    DM={}   #Dictunary for output metals
    for m, ion in metal_list.items():
        if m in p.keys():
            result = get_recovery(flow_rate=p['q'], concentration=p[m] / 1000, metal=ion) 
            p[m] = p[m] * (1 - result['re'])
            
            DM[m] = result['M'] # g/s
            DM[m] *= 1000  # g/s to mg/s
            DM[m] /=p['q'] # (mg/s)/(L/s) = mg/L

            #DM[m]=result['M'] / 1000    #kg/s - value returned in g, as _monoad is None -> time equals 1s
            #DE -= result['E']           #kWh/s - as fulload is None -> time equals 1s (GTH: seems to be kW)
            DE -= result['P'] / 1000     #MW
    return p, DE, DM


#[GCHPc]======================Heat exchange ============================================================
def C4(p, ht_demand, lt_demand, brine, orc):
    gchpp = GCHPp(name='test', m_bi = p['q'], t_bi = p['t'], t_bo = 35., type=GCHPpType.parallel_serries)
    gchpp.brine = brine
    gchpp.brine.temperature = p['t']
    gchpp.brine.pressure = p['p']
    gchpp.brine.convert_gpl_to_wtp(concentration=p['s'], estimate=p['s']/gchpp.brine.tds)
    gchpp.brine.update_properties()
    gchpp.m_bi = p['q'] * gchpp.brine.density / 1000
    gchpp.ht_demand = ht_demand
    gchpp.lt_demand = lt_demand
    gchpp.orc = orc
    gchpp.orc.t_bi = p['t']
    gchpp.orc.get_t_bo(p['t'])
    gchpp.orc.n_cycle(p['t'])

    full_load = 1. # use 1. to get output in MW, otherwise uee full load hours (e.g., 8760 * .8)

    '''calculate_ht_mass_flow returns 3 results:
        ht_power: the maximal thermal supplied for high temperature heating in MW (float)
        ht_supply: geothermal heat supplied in MW x time step of the time curve (np.ndarray)
        ht_flow: brine mass flow rate over the high temperature heat exchanger in kg/s (np.ndarray)
    '''
    out = calculate_ht_mass_flow(gchpp=gchpp, cutoff=.6)
    gchpp.m_ht = out['ht_flow']                             # value in kg/s
    gchpp.ht_supply = out['ht_supply']                      # value in MW

    '''orc.calculate_output returns the electrical output in MWh (x time step of array)
       In case just one element is supplied by the flow_rate array, the returned value is in MW.
    '''
    gchpp.m_orc = calculate_orc_mass_flow(gchpp=gchpp)
    gchpp.t_th_o = calculate_t_hto(gchpp=gchpp)
    gchpp.orc_output = gchpp.orc.calculate_output(flow_rate=gchpp.m_orc, brine=gchpp.brine)

    '''calculate_lt_supply returns 2 results:
        lt_power: the maximal thermal supplied for low temperature heating in MW (float)
        lt_supply: geothermal heat supplied in MW x time step of the time curve (np.ndarray)
    '''
    out = calculate_lt_supply(gchpp=gchpp, cuttoff=1.)
    gchpp.lt_supply = out['lt_supply']


    '''Return results'''
    DH = np.average(gchpp.ht_supply) + np.average(gchpp.lt_supply)
    DH *= full_load                                      # in MWh
    DE = np.average(gchpp.orc_output) * full_load        # in MWh
    p['t'] = np.average(calculate_t_bo(gchpp))

    #print('-----------------------------------------------------')
    #print(f'orc props: {gchpp.orc.__dict__}')
    #print(f'brine props: {gchpp.brine.__dict__}')
    #print(f'mass flow: {gchpp.m_bi}  -  T_out: {p["t"]}°C')
    #print(f'heat supply: {DH} MWh  -  output orc: {DE} MW')

    DM={}

    return p, DE, DH, DM

#[GDEx]======================GasDiffusion electroprecipitation=========================================
def C5(p,random=True):
    #-----Use only metals where we have metal extraction data for the GDEx component------------- 
    metal_list=list( set(['al','li','sr','mn','ba','as','zn','rb','ni']) & set(p.keys()) )
    #-----metals that we do not have data on exctraction rate but could be present in the brine--
    extra_metal_list=list( set(['au','ag','fe','co','cu','cs','pb','cd','ti','mo','se','br','sb','f_','cr','hg','b_']) & set(p.keys()) )
    #----------Check if parameters are within allowed range, if not stops ans returns nan--------
    if (not 20 <= p['t'] <= 70) or (not 1  <= p['p'] <= 10 ):
        print("Component C5 out of range: T=", p['t'], ", P=",p['p'])
        # ....Add somekind of logging functionality....        
        return p,np.nan,{key:np.nan for key in metal_list+extra_metal_list}


    #----Calculate how much metal is extracted and update parameter list accordingly
    DM={}   #Dictunary for output metals
    for m in metal_list:
        metal_frac=eval(f"gedx.{m}Out(p) if random else gedx.{m}Out0(p)")
        metal=p[m]*metal_frac
        DM[m]=metal           #mg/L
        p[m]=p[m]-metal
        
        #DM[m]*=1e-6           #kg/L
        #DM[m]*=p['q']         #kg/s
        
    for m in extra_metal_list:
        metal_frac=np.random.uniform(0,1) #No data for recovery, using uniform distribution from 0 to 1 
        metal=p[m]*metal_frac
        DM[m]=metal           #mg/L
        p[m]=p[m]-metal
        
        #DM[m]*=1e-6           #kg/L
        #DM[m]*=p['q']         #kg/s
    #----------Calculate how much energy is used--------------------------------------------------
    DE=gedx.eOut(p) if random else gedx.eOut0(p)   #"kWh/kg"


    totalM=sum([m for m in DM.values()]) #kg/s 


    DE=DE*(1e-6*totalM*p['q']) #kWh/kg * (mg/L *kg/s ) =kWh/s
    DE*=3.6 #kWh/s to MW
    DE=-DE       #the component consumes energy
    return p,DE,DM

#[REDp]=====================Salt gradient power generation==============================================
def C6(p):
    salt_removal=0.22
    #------------------Flow rate of brine and fresh water-----------------------------------------
    q_brine=p['q']
    q_brine/=1000   #l/s to m3/s
    q_water=q_brine #Assume same amount of river water as as brine
    
    #---------------Temperature converted from °C to K--------------------------------------------
    T=p['t']
    T+=273.16       #°C to K    
    
    #---------Salanity of fresh water (assumed to be 1000 mg/L) converted to mmol/L---------------
    s_water= 1000 #ppm or mg/L fresh water nacl salinity?
    s_water/=58.4 #mmol/L assuming NaCl
    
    #---------Salanity of brine in mmol/L ---------------
    s_brine=p['s'] #g/L
    s_brine*=1000  #mg/L
    s_brine/=58.4  #mmol/L assuming NaCl
    
    #---------Salt gradient model----------------------------------------------------------------
    results=sg.SGPRE(q_brine,s_brine,q_water,s_water,T,salt_removal)
    DE=results[0] # in W
    DE /=1e6     # W to MW 
    
    #--------salt removal from brine----------------------------------------------
    p['s']*=(1-salt_removal)
    
    DM={}

    return p, DE, DM

#=====================Injection Well===============================================================
def C7(p):
    DE=0
    DM={}
    return p, DE,DM


