import numpy as np
import pandas as pd
from scipy.integrate import odeint


#global SGPRE stack parameters and constants 
l= 1                # length of stack [m]
b= 1                # width of stack [m]
R= 8.31             # ideal gas constant [J mol−1 K−1]
F= 96485            # Faraday constant [As Eq-1]  
Raem = 0.00005      # AEM membrane resistance [ohm.m2] --FAS 20 0,5 Ohm.cm²
Rcem = 0.00017      # CEM memrbane resistance [ohm.m2] --FKS 20 1,7 Ohm.cm²
tk = 0.995          # transport number CEM [-]  -FKS 20 99%PS --> (0.99+1)/2=0.995
ta = 0.98           # transport number AEM [-]  -FAS 20 96%PS --> (0.96+1)/2=0.98
v_b = 0.01          # brine flow velocity [m s-1] 
f = 1/0.8           # obstruction factor (1/spacer shadow) [-]
eta_P = 0.85        # pump power efficiency 
d_spacer = 0.002    # distance between spacer rods [m] #check if used

# global model parameters 
it = 100            # sequence of values solved in ODEint
#it_nr = 200         # number of R in powerplot iteration
it_nr=20
#it_nr=50
Ru_start = 0.0001   # start resitance for powerplot iteration
Ru_factor = 1       # multiplies Rinternal to find max RU in powerplot iteration
l_max = 100         # upper boundary for iteration on stack length
beta =0.782         #stack tuning parameter


#-------------------------------------------------------------------------------------------------
def Ppump (Qb, Cb, Qr, Cr, h_b, T):
    #stack pumping power J [W]
    
    t =T-273
    
    mu_20  =  0.001   #viscosity at 20 °C [kg m-1 s-1] 
    
    Ac=1.37023 *(t-20)+ 8.36*np.power(10.,-4)*np.power((t-20),2) 
    Bc=109 + t
    
    mu = mu_20/(np.power(10,(Ac/Bc)))
    
    dH_cell = 2*h_b*b/(h_b+b) #check
    
    delta_Pb = mu/mu_20*0.273*v_b/(dH_cell)**2 #ref calibratie spacer testen 
    
    v_r = Qr/Qb*v_b
    
    delta_Pr =mu/mu_20*0.273*v_b/(dH_cell)**2
    
    P_pump = (l*delta_Pr*Qr+l*delta_Pb*Qb)/eta_P
    
    return (P_pump)


#-------------------------------------------------------------------------------------------------
def activ (C):
    gamma= -(3.786e-12)*C**3+(5.455e-8)*C*C-(1.426e-4)*C+7.629e-1
    act = C*gamma
    return act


#-------------------------------------------------------------------------------------------------
def EC_C (C_EC, T):
    
    #calculate EC 20°C ref http://www.aqion.de/site/130
    EC = 0.0942*C_EC-9.04e-6*C_EC**2 #taken from etienne voor NaCl tot 5 M
    
    n25=0.891e-3
    n20=1.003e-3   
    EC20 = EC*n25/n20 
    
    #calculate from 20°C to any other T
    t=T-273
    Ac=1.37023 *(t-20)+ 8.36*np.power(10.,-4)*np.power((t-20),2) 
    Bc=109 + t
    EC_T = EC20*(np.power(10,(Ac/Bc)))*0.1 #1mS/cm = 0.1 S/m
    
    return EC_T

#-------------------------------------------------------------------------------------------------

def ODE (Qb_in, Cb_in, Qr_in, Cr_in, Ru, h_b, T):
    
    # function returns an array descibing the concentration profile and power output of a co-current SGPRE stack
    def funct(y,x, N, h_r, h_b, Qb_in, Qr_in,T,Ru):

        #rename returned funct values
        Cb =y[0]
        Cr = y[1]

        #system of ODE's defined for a stack element dx with width b and thickness h_b    
        E_cell_x = beta*(tk+ta)*(R*T/F)*np.log(activ(Cb)/(activ(Cr))) # [V] OCV for 1CP
        R_cell_x = (f*h_b)/(EC_C(Cb,T))+(f*h_r)/(EC_C(Cr,T))+((Raem+Rcem)) # [ohm.m2] R of 1CP Resistance of 1 CP
        E_stack_x = E_cell_x/((1/N)+(R_cell_x/Ru)) # [V] voltage out for whole stack and external resitance Ru [ohm m2]
        I_cell_x = (E_stack_x/Ru) # [A m-2] current for stack width b / unit of pathlength

        J_current_x = I_cell_x/F #[mol m-2 s-1] moles of naCl flux per unit lentgh of pathlength
        J_diff_x = (J_current_x-J_current_x*(0.5*(tk+ta)))/(0.5*(tk+ta)) #[mol m-2 s-1] mol/s of NaCl diff (both membranes) for a unit of pathlenghth
        J_cell_x = J_current_x +J_diff_x # [mol m-2 s-1] ion flux for stack width b / unit of pathlength

        #print(J_diff_x,J_current_x,J_cell_x)

        dydx = [-J_cell_x*b/(Qb_in/N), J_cell_x*b/(Qr_in/N)] 
        #[mol m-3] from mass balance ion flux*dx (with allready in) and dC*Q/N


        return dydx

    
    #initial conditions and ODE interval
    y0 = (Cb_in, Cr_in)
    x= np.linspace( 0., l, it)

    #calculate number of CP based on flow and cell geometry
    N = Qb_in/(b*h_b*v_b)
    
    # equal width of compartments (can be based on equal pressure drop later (darcy, calculate spacer width)) 
    h_r = h_b
     
    # Solve ODE
    y = odeint(funct, y0, x, args = (N, h_r, h_b, Qb_in,Qr_in,T,Ru))
    
    return y

#---------------------------------------------------------------------------------------------------
def stack (Qb_in, Cb_in, Qr_in, Cr_in, Ru, h_b, T):
    y = ODE(Qb_in, Cb_in, Qr_in, Cr_in, Ru, h_b, T)
    #postcalculations
    N = Qb_in/(b*h_b*v_b)
    h_r = h_b
    
    Cb,Cr=y.T
    E_cell_x = beta*(tk+ta)*(R*T/F)*np.log((activ(Cb))/(activ(Cr))) #[V] local OCV at lenght position x
    R_cell_x = (f*h_b/(EC_C(Cb,T)))+(f*h_r)/(EC_C(Cr,T))+((Raem+Rcem))/(b*l)
   
    #[ohm]
    E_stack_x = E_cell_x/((1/N)+R_cell_x/(Ru)) #[V] V out for whole stack
    I_cell_x = E_stack_x/(Ru) #[A] 
    Ru =Ru     
    
    #check stack table pd
    R_mean =N*R_cell_x.mean() # [ohm]
    OCV_mean = N*E_cell_x.mean() # [V]
    U_mean = E_stack_x.mean() # [V]
    I_mean = I_cell_x.mean() # [A]
    S = N*l*b #[m2]
    P_out = U_mean*I_mean/S #[V A m-2]/m-2
    P_tot = U_mean*I_mean
    P_pump = Ppump (Qb_in, Cb_in, Qr_in, Cr_in, h_b, T)
    P_net = P_tot-P_pump
    #print(OCV_mean, U_mean + I_mean*R_mean, U_mean + I_mean*Ru)
    #calculating P_max here has no physical meaning, because changing Ru changes the concentration profile and thus Ri and Pmax. 
    SE = (Cb[0]-Cb[it-1])/Cb[0]*100
    #stack_table.to_csv("stacktable.csv", index = False, sep=';', encoding='utf-8')   
    #print('Ru', Ru,'R_mean', R_mean)
    #print(stack_table)
    x=np.array([U_mean, P_out,P_tot,P_pump,P_net,R_mean, I_mean, OCV_mean, N, S, Ru, h_b, Qb_in, Cb_in, Qr_in, Cr_in, T, SE ])
    return x


#---------------------------------------------------------------------------------------------------
def th_opt (Qb_in, Cb_in, Qr_in, Cr_in, T):

    #calculates array for different external resistances and cell thicknesses 
    thickness = np.array ([0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008, 0.0009, 0.001])
    output = np.zeros(18)
    for t in thickness:    
        RS = stack(Qb_in, Cb_in, Qr_in, Cr_in, Ru_start, t, T)
        Ru_end = RS[5]*Ru_factor
        S_local = RS[9]
        powerset = np.power(np.append(np.arange(Ru_start, Ru_end,(Ru_end-Ru_start)/it_nr), Ru_end),1.5)
        #np.savetxt("powerset.csv",powerset, delimiter=";")
        for x in powerset:
            output = np.vstack((output,stack(Qb_in, Cb_in, Qr_in, Cr_in, x, t, T)))
        output = np.delete(output, (0), axis = 0)      
        
    P_stack= np.amax(output, axis =0)[4] # 4maximal P_total-P_pump is taken for optimisation ipv P_W_m2
    index = np.argmax(output, axis =0)[4] #
    Ru_stack = output[index, 10]
    h_b_stack = output[index, 11]
    #np.savetxt("output.csv", output, delimiter=";")
    
    return h_b_stack

#---------------------------------------------------------------------------------------------------
def SGPRE (Qb_in, Cb_in, Qr_in, Cr_in, T, SE_desired):

    #check maximal desalination
    SE_max = (Cb_in - (Qb_in*Cb_in+Qr_in*Cr_in)/(Qb_in+Qr_in))/Cb_in
    
    if SE_desired > SE_max:
        
        print('SE_desired', SE_desired, 'is larger than SE_max', SE_max,'choose lower SE_desired' )
   
    else: 
 
        #calculate optimal thickness
        h_b = th_opt (Qb_in, Cb_in, Qr_in, Cr_in, T) 
    
        #calculates array for different external resistances
        output = np.zeros(18)
        RS = stack(Qb_in, Cb_in, Qr_in, Cr_in, Ru_start, h_b, T)
        Ru_end = RS[5]*Ru_factor
        S_local = RS[9]
        powerset = np.power(np.append(np.arange(Ru_start, Ru_end,(Ru_end-Ru_start)/it_nr), Ru_end),1.5)
      
        for x in powerset:
            output = np.vstack((output,stack(Qb_in, Cb_in, Qr_in, Cr_in, x, h_b, T)))
        output = np.delete(output, (0), axis = 0)      
        #np.savetxt("output.csv", output, delimiter=";")
        #first stack in the line,
        stack_nr = 1.
    
        P_stack = np.amax(output, axis =0)[4] #here optimum is for P/m2 optimization of cost 
        index = np.argmax(output, axis =0)[4]
        Ru_stack = output[index, 10]
        h_b_stack = output[index, 11]

        #calculate the stacks concentration profile and store in DF
        SGPRE_stack = ODE(Qb_in, Cb_in, Qr_in, Cr_in, Ru_stack, h_b_stack, T)   
        names = ['Cb','Cr']
        SIS = pd.DataFrame(SGPRE_stack, columns=names)
        
        #store additional values of intrest in DF

        SIS['P_stack'] = P_stack
        SIS['U_stack'] = output[index, 0]
        SIS['h_b_stack'] = h_b_stack
        SIS['Ru_stack'] = Ru_stack 
        SIS['Cb_out'] = SIS.at[it-1, 'Cb']
        SIS['Cr_out'] = SIS.at[it-1, 'Cr']
        SIS['SE'] = (Cb_in - SIS['Cb'])/Cb_in
        SIS['SE_out'] = SIS.at[it-1, 'SE']
        SIS['stack_nr'] = stack_nr
        
        #summarize stackinfo in summary DF
        summary = [np.insert(output[index,:], 0, stack_nr)]
        names = ['stack_nr','U_mean', 'P_W_m2','P_tot', 'P_pump_tot','P_net', 'R_mean', 'I_mean', 
                 'OCV_mean', 'N', 'S','Ru', 'h_b','Qb_in', 'Cb_in', 'Qr_in', 'Cr_in', 'T', 'SE']
        SIS_summary = pd.DataFrame(summary, columns=names)
        SIS_summary['SE'] = SIS.at[it-1, 'SE']
        
        #set pars for next loop
        Cb_loc = SIS.at[it-1, 'Cb']
        Cr_loc = SIS.at[it-1, 'Cr']
        Ru_loc = Ru_stack
        SE_out = SIS.at[it-1, 'SE']
        
        #print('stack_nr', stack_nr, 'Cb_out', Cb_loc, 'Cr_out',Cr_loc,'P_out_W_m2',P_stack/S_local, 'SE_out', SE_out)
        
        while SE_out < SE_desired:
            
            stack_nr = stack_nr+1
           
            output = np.zeros(18)
  
            RS = stack(Qb_in, Cb_loc, Qr_in, Cr_loc, Ru_loc, h_b, T)
            Ru_end = RS[5]*Ru_factor
            S_local = RS[9]
            powerset = np.power(np.append(np.arange(Ru_start, Ru_end,(Ru_end-Ru_start)/it_nr), Ru_end),1.5)
                
            for x in powerset:
                output = np.vstack((output,stack(Qb_in, Cb_loc, Qr_in, Cr_loc, x, h_b, T)))
            output = np.delete(output, (0), axis = 0)      
           
            #n-th stack in the line,
        
            P_stack= np.amax(output, axis =0)[4]
            index = np.argmax(output, axis =0)[4]
            Ru_stack = output[index, 10]
            h_b_stack = output[index, 11]
            
            SGPRE_stack = ODE(Qb_in, Cb_loc, Qr_in, Cr_loc, Ru_stack, h_b_stack, T)   
            names = ['Cb','Cr' ]
            df2 = pd.DataFrame(SGPRE_stack, columns=names)

            #store additional values of intrest in DF
            df2['P_stack'] = P_stack
            df2['U_stack'] =  output[index, 0]
            df2['h_b_stack'] = h_b_stack
            df2['Ru_stack'] = Ru_stack 
            df2['Cb_out']=df2.at[it-1, 'Cb']
            df2['Cr_out']=df2.at[it-1, 'Cr']
            df2['SE']= (Cb_in - df2['Cb'])/Cb_in
            df2['SE_out']=df2.at[it-1, 'SE']
            df2['stack_nr'] = stack_nr
            SE_out=df2.at[0,'SE_out']
            
            #concat to SIS dataframe
            
            SIS = pd.concat([SIS, df2] , ignore_index=True) 
    
            #generate data for summary dataframe
        
            summary=[np.insert(output[index,:], 0, stack_nr)]
            names = ['stack_nr','U_mean', 'P_W_m2','P_tot', 'P_pump_tot','P_net', 'R_mean', 'I_mean', 
                 'OCV_mean', 'N', 'S','Ru', 'h_b','Qb_in', 'Cb_in', 'Qr_in', 'Cr_in', 'T', 'SE']
            
            #SE represents local SE, to be calculated overall
            
            df2_summary = pd.DataFrame(summary, columns=names)
            df2_summary['SE']=df2.at[it-1, 'SE_out']
            SIS_summary = pd.concat([SIS_summary, df2_summary], ignore_index=True) 
            
            #set new values for iteration
            
            Cb_loc = df2.at[it-1, 'Cb']
            Cr_loc = df2.at[it-1, 'Cr']
            Ru_loc = Ru_stack
            #print('stack_nr', stack_nr, 'Cb_out', Cb_loc, 'Cr_out',Cr_loc,'P_out_W_m2',P_stack/S_local, 'SE_out', SE_out)
            
            if stack_nr*l > l_max:
                SE_out =1
                print('maximal pathlength exceeded')
        #store dataframes
        P_total = SIS_summary['P_net'].sum()
        
        SIS=SIS[['stack_nr','Cb','Cr','Cb_out','Cr_out','P_stack','U_stack','h_b_stack','Ru_stack','SE','SE_out']]

        
        #SIS.to_csv("output_SGPRE_SIS_model.csv", index = False, sep=';', encoding='utf-8')
        #SIS_summary.to_csv("summary_SGPRE_SIS_model.csv", index = False, sep=';', encoding='utf-8')   
        
        #print('SGPRE calculations are ready')
        #print('')
        #print('P_max_total (W): ',round(P_total))
        #print('number of stacks (-): ',stack_nr)
        #print('celpairs per stack (-):', round(SIS_summary.at[1, 'N']))
        #print('total cell surface (m2): ',round(S_local*stack_nr))
        #print('average P_max (W/m2): ', round(P_total/(S_local*stack_nr)))
        
        return ([P_total, stack_nr, S_local*stack_nr, P_total/(S_local*stack_nr)])