import numpy.random as rd
import numpy as np
import pandas as pd
import System_model.CHMP_funs as cf

from GCHPc.demand import ComodityType, Demand
from GCHPc.orc_m01 import BinaryType, ORC
from GCHPc.brine_properties import Brine

#=====================Randomizer===================================================================
def randomizer(d):
    """Takes in a dictionary with lists of length 1,2, and 3. The output is a dictionary with same keys
    as the input dictionary.
    The value for each key is a:
        random number from a triangular distribution for a length three list,
        random number from a uniform distribution for a length two list,
        the value of the input list for a length one list.
    """
    randD={}
    for key in d:
        if len(d[key])==3:
            randD[key]=rd.triangular(d[key][0],d[key][1],d[key][2])
        elif len(d[key])==2:
            randD[key]=rd.uniform(d[key][0],d[key][1])
        elif len(d[key])==1:
            randD[key]=d[key][0]
    return randD



#=====================Full Monte Carlo loop===================================================================
def full_monte_carlo_loop(num_mc_runs,param_dist,GCHPc_params):

    #------------------------Initializing lists that collect output distributions------------------------------
    param_hist={ }
    for key in param_dist:
        param_hist[key]=[]

    #---Electric power----
    E_hist=[]
    E3_hist=[]
    E4_hist=[]
    E5_hist=[]
    E6_hist=[]
    E7_hist=[]

    #---Extracted metals---
    M3_hist={}
    M5_hist={}

    #---Heat power----
    H4_hist=[]

    #----------------------Monte carlo loop-----------------------------------------------------------------
    for i in range(int(num_mc_runs)):
        print(i,end=",")
        #-------------------------Random parameter dictionary-------------------------
        rand_param=randomizer(param_dist)
        #saving i-th realization of the parameter dicionary
        for key in rand_param:
            param_hist[key].append(rand_param[key])
            
        #-------------------------running through the CHPM components-------------------------
        Esum=0
        
        #print('HTPE',end=",")
        #[HTPE]--------Electrolysis, component no. 3---------------------------------------------
        rand_param,W,M=cf.C3(rand_param)    
        E3_hist.append(W) 
        for key in M:
            if key not in M3_hist: M3_hist[key]=[]
            M3_hist[key].append(M[key])
        Esum+=W
        #print('GCHPc',end=",")
        #[GCHPc]--------Geothermal Plant, component no. 4--------------------------------------
        ht_heat=Demand(comodity_type=ComodityType.HEAT, curve=GCHPc_params["ht_heat_curve"], t_supply=GCHPc_params["ht_heat_t_supply"], t_return=GCHPc_params["ht_heat_t_return"])    
        lt_heat=Demand(comodity_type=ComodityType.HEAT, curve=GCHPc_params["lt_heat_curve"], t_supply=GCHPc_params["lt_heat_t_supply"], t_return=GCHPc_params["lt_heat_t_return"])
        orc = ORC(name='orc', t_bi=rand_param['t'], type=BinaryType.ocr_acc)
        brine = Brine(name='test', tds=GCHPc_params['brine_tds'], temperature=rand_param['t'], pressure=rand_param['p'])
        #print(rand_param['s'],end=",")
        rand_param,W,H,_=cf.C4(p=rand_param, ht_demand=ht_heat, lt_demand=lt_heat, brine=brine, orc=orc)  
        #print(rand_param['s'],end=",")
        E4_hist.append(W)
        H4_hist.append(H)
        Esum+=W
        
        #print('GDEx',end=",")
        #[GDEx]---------Gas diffusion, component no. 5--------------------------------------------------
        rand_param,W,M=cf.C5(rand_param)
        E5_hist.append(W)
        for key in M:
            if key not in M5_hist: M5_hist[key]=[]
            M5_hist[key].append(M[key])    
        if np.isnan(W) == False:
            Esum+=W
        #print('REDp',end=",")
        #[REDp]--------Salt gradient plant, component no. 6------------------------------------------------
        rand_param,W,_=cf.C6(rand_param)
        E6_hist.append(W)
        Esum+=W    
 
        #--------Injection Well, component no. 7---------------------------------------------
        rand_param,W,_=cf.C7(rand_param)    
        E7_hist.append(W)
        Esum+=W

        #--------Total sums-----------------------------------------------------------------------
        E_hist.append(Esum)


    #--------------Collecting all result data into one pandas dataframe-----------------------------
    df=pd.DataFrame(param_hist)

    #[HTPE]---------Electrolysis, component no. 3--------------
    df['E3']=E3_hist
    for key in M3_hist:
        df[key+'_3']=M3_hist[key]

    #[GCHPc]--------Geothermal Plant, component no. 4---------- 
    df['E4']=E4_hist
    df['H4']=H4_hist  

    #[GDEx]---------Gas diffusion, component no. 5------------
    df['E5']=E5_hist    
    for key in M5_hist:
        df[key+'_5']=M5_hist[key]

    #[REDp]---------Salt gradient plant, component no. 6----------
    df['E6']=E6_hist    

    #[Total]-------------------------------------------------
    df['E']=E_hist
    
    return df




#=====================Custom Monte Carlo loop================================================================
# Very slow, ... need to swap dataframes out for numpy arrays in critical places
#import sys
#def custom_monte_carlo_loop(num_mc_runs,param_dist,c_order):
#    
#    #-----check if c_order list contains only strings--------------------------------------------------------
#    known_components=['C3','C4','C5','C6']
#    if not (c_order and all(isinstance(c, str) for c in c_order)):
#        raise ValueError("c_order must be a list of strings! For example "+str(known_components))
#    
#    
#    #-----------------Main dataframe created------------------------------------------------------------------
#    df=pd.DataFrame()
#    
#    #----------------------Monte carlo loop-------------------------------------------------------------------
#    for i in range(int(num_mc_runs)):
#        print(str(i)+', ', end='', flush=True)
#        #-------------------------Random parameter dictionary-------------------------------------------------
#        p=randomizer(param_dist)
#        
#        #saving i-th realization of the parameter dicionary
#        df0=pd.Series(p).to_frame().T
#        #-------------------------running through the CHPM components-----------------------------------------
#        Esum=0
#        c_order=[c.upper() for c in c_order] #make sure all letters all capitalized 
#        for c in c_order:
#            #----check if function for the component exists---------------------------------------------------
#            if c in known_components:
#                p, E, H, M=eval("run_"+c+"(p)")
#
#                #------------storing p values after they have gone through component--------------------------
#                for key,value in p.items():
#                    df0[key+'_'+c]=value  
#                #-------------storing electric energy, heat and metal values----------------------------------
#                df0['E_'+c]=E
#                df0['H_'+c]=H
#                if type(M) is dict:
#                    for key,value in M.items():
#                        df0[key+'_'+c]=value
#                #-------------summing upp total electric energy-----------------------------------------------
#                Esum+=E
#            else:
#                error_message=c+" is not a known component and its, the following components are available:"
#                for c in known_components:
#                    error_message+='\n'+c
#                raise ValueError(error_message)
#
#        #--------Total sums-----------------------------------------------------------------------------------
#        df0['Esum']=Esum
#        
#        #-------Adding results from i-th monte carlo run to main dataframe------------------------------------
#        df=pd.concat([df,df0],axis=0,ignore_index=True)
#
#    return df
#
#
#
#
#
#
##============================Wrapper function of components called in custom monte carlo loop==============================
##...input and output of components should maybe be standardized instead, and call them directly in custom monte carlo loop?
#
#
##[HTPE]--------Electrolysis, component no. 3---------------------------------------------
#def run_C3(p):
#    p,E,M=cf.C3(p)    
#    H=np.nan
#    return p, E, H, M
#
##[GCHPc]--------Geothermal Plant, component no. 4--------------------------------------
#def run_C4(p):
#
#    ht_heat=Demand(comodity_type=ComodityType.HEAT, curve=np.array([3]), t_supply=120, t_return=80)
#    lt_heat=Demand(comodity_type=ComodityType.HEAT, curve=np.array([5]), t_supply=60, t_return=40)
#    orc = ORC(name='orc', t_bi=p['t'], type=BinaryType.ocr_acc)
#    brine = Brine(name='test', tds=.03, temperature=p['t'], pressure=p['p'])
#    
#    p,E,H,_=cf.C4(p, ht_demand=ht_heat, lt_demand=lt_heat, brine=brine, orc=orc)  
#    M=np.nan
#    
#    return p, E, H, M
#
#
##[GDEx]---------Gas diffusion, component no. 5--------------------------------------------------
#def run_C5(p):
#    p,E,M=cf.C5(p)
#    H=np.nan
#    return p, E, H, M    
#
##[REDp]--------Salt gradient plant, component no. 6------------------------------------------------
#def run_C6(p):
#    p,E,_=cf.C6(p)
#    M=np.nan
#    H=np.nan
#    return p, E, H, M