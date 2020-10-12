import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})

def plot_histogram(dS,ax,xlabel,ymax,xrange=None,ylabel=True,quantile_text=True,nbins=50):
    if '[' in xlabel:
        unit=xlabel[xlabel.find("[")+1:xlabel.find("]")]
    elif '(' in xlabel:
        unit=xlabel[xlabel.find("(")+1:xlabel.find(")")]
    else:
        print("")
        

    q2l=dS.quantile(0.025)
    numdec=int(-np.floor(np.log10(abs(q2l)/10)))
    ax.axvline(q2l,ls="--",c='red')
    if quantile_text:
        ax.text(q2l,1.01*ymax,"2.5 % \n"+str(np.around(q2l,numdec))+" "+unit,horizontalalignment='center',fontsize='small')
    q1l=dS.quantile(0.16)
    ax.axvline(q1l,ls="--",c='red')
    if quantile_text:
        ax.text(q1l,1.12*ymax,"16 % \n"+str(np.around(q1l,numdec))+" "+unit,horizontalalignment='center',fontsize='small')
    q0=dS.quantile(0.50)
    ax.axvline(q0,ls="--",c='red')
    if quantile_text:
        ax.text(q0,1.01*ymax,"50 % \n"+str(np.around(q0,numdec))+" "+unit,horizontalalignment='center',fontsize='small')
    q1r=dS.quantile(0.84)
    ax.axvline(q1r,ls="--",c='red')
    if quantile_text:
        ax.text(q1r,1.12*ymax,"84 % \n"+str(np.around(q1r,numdec))+" "+unit,horizontalalignment='center',fontsize='small')
    q2r=dS.quantile(0.975)
    ax.axvline(q2r,ls="--",c='red')
    if quantile_text:
        ax.text(q2r,1.01*ymax,"97.5 % \n"+str(np.around(q2r,numdec))+" "+unit,horizontalalignment='center',fontsize='small')
    #print(np.around(q1l,3),np.around(q0,3),np.around(q1r,3))
    dS.hist(ax=ax,bins=nbins, edgecolor='black', linewidth=1.2)
    #ax.set_xticks([p.get_x() for p in ax[0].patches])
    for p in ax.patches:
        if (p.get_x()+p.get_width()<q2l) | (q2r<p.get_x()):
            plt.setp(p, 'facecolor', 'C2')
        elif (p.get_x()+p.get_width()<q1l) | (q1r<p.get_x()):
            plt.setp(p, 'facecolor', 'C1')            
    if ylabel: ax.set_ylabel("Counts")
    ax.set_xlabel(xlabel)
    if xrange: ax.set_xlim(xrange)
    ax.set_ylim([0,ymax])
    ax.grid(False)
    
    
    
# Taken from:
#https://stackoverflow.com/questions/18915378/rounding-to-significant-figures-in-numpy    
#The following constant was computed in maxima 5.35.1 using 64 bigfloat digits of precision
__logBase10of2 = 3.010299956639811952137388947244930267681898814621085413104274611e-1
def RoundToSigFigs_fp( x, sigfigs ):
    """
    Rounds the value(s) in x to the number of significant figures in sigfigs.
    Return value has the same type as x.

    Restrictions:
    sigfigs must be an integer type and store a positive value.
    x must be a real value.
    """
    if not ( type(sigfigs) is int or type(sigfigs) is long or
             isinstance(sigfigs, np.integer) ):
        raise TypeError( "RoundToSigFigs_fp: sigfigs must be an integer." )

    if sigfigs <= 0:
        raise ValueError( "RoundToSigFigs_fp: sigfigs must be positive." )

    if not np.isreal( x ):
        raise TypeError( "RoundToSigFigs_fp: x must be real." )

    xsgn = np.sign(x)
    absx = xsgn * x
    mantissa, binaryExponent = np.frexp( absx )

    decimalExponent = __logBase10of2 * binaryExponent
    omag = np.floor(decimalExponent)

    mantissa *= 10.0**(decimalExponent - omag)
    
    if mantissa < 1.0:
        mantissa *= 10.0
        omag -= 1.0

    return xsgn * np.around( mantissa, decimals=sigfigs - 1 ) * 10.0**omag