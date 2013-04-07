import numpy as np
theta=180
thetarad = theta*np.pi/180.
theta1 = np.mod(thetarad/2.-np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi
theta2 = np.mod(-2.*np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi
theta3 = np.mod(thetarad/2.-np.arcsin(np.sin(thetarad/2.)/2.),2.*np.pi)*180./np.pi
print theta1, theta2, theta3
