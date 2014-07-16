import glob
import os 
import numpy as np
from scipy.interpolate import LinearNDInterpolator


def _parse_xfoil_polar(f_name): 
    f = open(f_name,'rb')

    #skip the first 7 lines
    for i in xrange(7): 
        f.readline()

    #grab the reynolds_number
    data = f.readline().split()
    Re = float(data[5])*10**int(data[7])

    #skip 3 more lines
    for i in xrange(3): 
        f.readline()

    #alpha, Cl, Cd, Cdp, CM, Top_Xtr, Bot_Xtr
    data = []
    for line in f: 
        data.append(map(float, line.split()))
        
    f.close()

    return Re, np.array(data)


def get_ClCd_interpolant(): 
    dirname = os.path.dirname(__file__)
    search = os.path.join(dirname, "*.dat")
    files = glob.glob(search)


    points = []
    Cl = []
    Cd = []

    for f in files: 
        Re, data = _parse_xfoil_polar(f)
        #inputs
        
        alpha = data[:,0]
        Re = np.ones(alpha.shape)*Re

        points.extend(np.vstack((Re, alpha)).T)
        #outputs
        Cd.extend(data[:,2])
        Cl.extend(data[:,1])


    Cl_interp = LinearNDInterpolator(points, Cl, fill_value=1.0, rescale=True)
    Cd_interp = LinearNDInterpolator(points, Cd, fill_value=1.0, rescale=True)

    return Cl_interp, Cd_interp


if __name__ == "__main__": 

    # Re, data = parse_xfoil_polar('re200000.dat')
    # print Re, data.shape

    # Re, data = parse_xfoil_polar('re500000.dat')
    # print Re, data.shape

    Cl, Cd = get_ClCd_interpolant()
    print Cl(200000, -8.750 )
    print Cd(200000, -8.750 )

