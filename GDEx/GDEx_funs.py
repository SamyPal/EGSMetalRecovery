import numpy as np

#------------------------------------------------Energy output functions-------------------------------------------------------------------------------------
def eOut0(P):
    A=1.3529312060941647    #const
    B=0.0016362141049857705    #mg
    C=-8.196073337777638e-06    #ca
    D=-0.0049871888864530655    #s
    E=1.7076258958316184    #ewe
    F=-0.00011957753143042316    #t
    G=0.07557845354792651    #ph
    return np.exp(A+B*P['mg']+C*P['ca']+D*P['s']+E*P['ewe']+F*P['t']+G*P['ph'])
def eOut(P):
    A=np.random.normal(1.3529312060941647,0.35421523420348194)    #const
    B=np.random.normal(0.0016362141049857705,0.0001816070254566603)    #mg
    C=np.random.normal(-8.196073337777638e-06,1.5739463852203642e-05)    #ca
    D=np.random.normal(-0.0049871888864530655,0.0022209604229630527)    #s
    E=np.random.normal(1.7076258958316184,0.40714694288472036)    #ewe
    F=np.random.normal(-0.00011957753143042316,0.006561245183509716)    #t
    G=np.random.normal(0.07557845354792651,0.02397543467409868)    #ph
    return np.exp(A+B*P['mg']+C*P['ca']+D*P['s']+E*P['ewe']+F*P['t']+G*P['ph'])

#--------------------------------------------------Li and Al fraction functions (LAB brine)---------------------------------------------------------------------
def alOut0(P):
    A=9.243112683565625    #const
    B=0.0007290528430428293    #mg
    C=2.3766108826381692e-05    #ca
    D=-0.6104172351984469    #ph
    E=-0.01023763417929939    #s
    F=-0.8547529374417671    #ewe
    G=0.0077546360321853955    #t
    out=A+B*P['mg']+C*P['ca']+D*P['ph']+E*P['s']+F*P['ewe']+G*P['t']
    return 1.0/(1.0+np.exp(-out))
def alOut(P):
    A=np.random.normal(9.243112683565625,1.173464899400799)    #const
    B=np.random.normal(0.0007290528430428293,0.0005482925615291159)    #mg
    C=np.random.normal(2.3766108826381692e-05,4.982003931049452e-05)    #ca
    D=np.random.normal(-0.6104172351984469,0.09299424362214656)    #ph
    E=np.random.normal(-0.01023763417929939,0.006459516129063303)    #s
    F=np.random.normal(-0.8547529374417671,1.1856402922543547)    #ewe
    G=np.random.normal(0.0077546360321853955,0.025068322281798946)    #t
    out=A+B*P['mg']+C*P['ca']+D*P['ph']+E*P['s']+F*P['ewe']+G*P['t']
    return 1.0/(1.0+np.exp(-out))
def liOut0(P):
    A=-2.166550880352732    #const
    B=-0.00038544070761357166    #mg
    C=0.0001293845078422753    #ca
    D=0.1054253807914887    #ph
    E=0.01679336165131661    #s
    F=0.21394153681811745    #ewe
    G=0.0005523783360058092    #t
    out=A+B*P['mg']+C*P['ca']+D*P['ph']+E*P['s']+F*P['ewe']+G*P['t']+A+B*P['mg']+C*P['ca']+D*P['ph']+E*P['s']+F*P['ewe']+G*P['t']
    return 0.4/(1.0+np.exp(-out))
def liOut(P):
    A=np.random.normal(-2.166550880352732,1.3101146056856243*0.4)    #const
    B=np.random.normal(-0.00038544070761357166,0.0006121410989070693*0.4)    #mg
    C=np.random.normal(0.0001293845078422753,5.562157094757528e-05*0.4)    #ca
    D=np.random.normal(0.1054253807914887,0.10382340100353452*0.4)    #ph
    E=np.random.normal(0.01679336165131661,0.0072117252341071065*0.4)    #s
    F=np.random.normal(0.21394153681811745,1.3237078201188375*0.4)    #ewe
    G=np.random.normal(0.0005523783360058092,0.02798752240326006*0.4)    #t
    out=A+B*P['mg']+C*P['ca']+D*P['ph']+E*P['s']+F*P['ewe']+G*P['t']+A+B*P['mg']+C*P['ca']+D*P['ph']+E*P['s']+F*P['ewe']+G*P['t']
    return 0.4/(1.0+np.exp(-out))

#------------------------------------------------------Metal fraction output (Romanian brine)------------------------------------------------------------
#=========== sr_outin_ratio ================
def srOut0(P):
    return 0.5257908570355769

def srOut(P):
    return np.random.uniform(0.20062035881026619,0.8509613552608877)

#=========== mn_outin_ratio ================
def mnOut0(P):
    return 0.7452830188679245

def mnOut(P):
    return np.random.uniform(0.5718417329165071,0.9187243048193419)

#=========== ba_outin_ratio ================
def baOut0(P):
    return 0.6388517319065052

def baOut(P):
    return np.random.uniform(0.42613028355806853,0.851573180254942)

#=========== as_outin_ratio ================
def asOut0(P):
    return 0.2556322162771051

def asOut(P):
    return np.random.uniform(0.14564772812816223,0.36561670442604793)

#=========== zn_outin_ratio ================
def znOut0(P):
    return 0.6081385525204168

def znOut(P):
    return np.random.uniform(0.2537763305646441,0.9625007744761895)

#=========== rb_outin_ratio ================
def rbOut0(P):
    return 0.03482587064676618

def rbOut(P):
    return np.random.uniform(0,0.08407708923687397)

#=========== ni_outin_ratio ================
def niOut0(P):
    return 0.5

def niOut(P):
    return np.random.uniform(0.13061586057419156,0.8693841394258084)


