import numpy as np
#import sys

def get_levels():
    """
    Returns an array with the ES energies as a function of strain Ex, 
    also returned
    """
    Ex=np.linspace(0,20,50)
    return Ex,np.array([np.sort(get_ES(E_field=[i,0,0])[0]) for i in Ex])

def get_ES_ExEy(Ex,Ey):
    """
    Returns the six transition energies in GHz of the ES of the NV centre, 
    when given the Energies of the Ex and Ey transitions in GHz
    """
    
    strain=abs(Ex-Ey)/2.0
    return np.sort(get_ES(E_field=[strain,0,0],Ee0= Ey+strain-1.94)[0])


def get_ES_ExEy_plottable(Ex,Ey,height):
    """
    Returns an array plottable with qt.Plot2D of the six transition energies 
    in GHz of the ES of the NV centre, when given the Energies of the Ex and 
    Ey transitions in GHz
    """
    x=get_ES_ExEy(Ex,Ey)
    y=np.zeros(3*len(x))
    for ii in range(len(x)):
        x=np.append(x,x[ii]-0.0001)
        x=np.append(x,x[ii]+0.0001)
        y[3*ii+1]=height
    return np.sort(x),y
    
def get_ES(E_field=[0.,0.,0.],B_field=[0.,0.,0.],Ee0=-1.94,transitions=True):
    """Returns the eigenvalues and eigenvectors of the NV excited state 
    pertubation matrix.
    inputs:
    - E-field xyz vector in GHz
    - B-field xyz vector in GHz
    - Energy offset for the eigenvalues
    - boolean transitions - whether to return the transition energies 
    (ms0 energies increased by the zero-field splitting)
    """
    
    Ex = E_field[0]
    Ey = E_field[1]
    Ez = E_field[2]
    Bx = B_field[0]
    By = B_field[1]
    Bz = B_field[2]
    lambdaA2=1.0    
    lambda_par=5.3           #observed
    lambda_ort=1.5*lambda_par      #unknown, calculated by Maze, p9
    D1A1=2.87/3           #observed
    D2A1=1.42/3            #observed
    D2E1=1.55/2             #observed
    D2E2=.2/np.sqrt(2)        #observed

    w2=np.sqrt(2)
    
    Vss = np.matrix([[D2A1, 0, D2E2*w2, 0, 0, 0],
                    [0, D2A1, 0, D2E2 *w2, 0, 0],
                    [D2E2*w2, 0, -2*D2A1, 0, 0, 0],
                    [0, D2E2*w2, 0, -2*D2A1, 0, 0],
                    [0, 0, 0, 0, D2A1 - 2*D2E1, 0],
                    [0, 0, 0, 0, 0, D2A1 + 2*D2E1]])
            
    Vso = np.diag([-lambda_par, -lambda_par, 0, 0, lambda_par, lambda_par])
    
    Ve = np.matrix([[Ez, 0, 0, 0, Ey, Ex],
                   [0, Ez, 0, 0, -Ex, Ey],
                   [0, 0, Ez + Ex, -Ey, 0, 0],
                   [0, 0, -Ey, Ez - Ex, 0, 0],
                   [Ey, -Ex, 0, 0, Ez, 0],
                   [Ex, Ey, 0, 0, 0, Ez]])
    Vb = np.matrix([[0, 1j*(Bz + lambdaA2*Bz), 1j*(By)/w2, 1j*(Bx)/w2, 0, 0],
                    [-1j*(Bz + lambdaA2*Bz), 0, 1j*(Bx)/w2, -1j*(By)/w2, 0, 0],
                    [-1j*(By)/w2, -1j*(Bx)/w2, 0, -1j*lambdaA2*Bz, 1j*(By)/w2, -1j*(Bx)/w2],
                    [-1j*(Bx)/w2, 1j*(By)/w2, -1j*lambdaA2*Bz,    0, -1j*(Bx)/w2, -1j*(By)/w2],
                    [0, 0, -1j*(By)/w2, 1j*(Bx)/w2, 0, 0],
                    [0, 0, 1j*(Bx)/w2, 1j*(By)/w2, 0, 0]])
      
   
    VGSoffset =  np.diag([0, 0, 3*D1A1, 3*D1A1, 0, 0]) if transitions else 0
  
   
    V = Vss + Vso + Ve + Vb + VGSoffset
    
    w,v=np.linalg.eig(V)
    
    return np.real(w+Ee0),v
    
