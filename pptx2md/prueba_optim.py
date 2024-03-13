import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit



def normal_pdf(x_vector, mu=0, sigma=1):
    return (1/(sigma*np.sqrt(2*np.pi)))*np.exp(-((x_vector - mu)/sigma)**2/2)

def f(x_vector, theta0, theta1, sigma0, sigma1):
    # sigma = 100
    return 0.5*((1/(sigma0*np.sqrt(2*np.pi)))*np.exp(-((x_vector - theta0)/sigma0)**2/2) + 
            (1/(sigma1*np.sqrt(2*np.pi)))*np.exp(-((x_vector - theta1)/sigma1)**2/2))


def f_gauss1(x_vector, theta0, theta1, sigma0, sigma1):
    salida = (normal_pdf(x_vector, theta0, sigma0) + normal_pdf(x_vector, theta1, sigma1))/2
    return(salida)

def f_gauss2(x_vector, theta0, theta1, sigma0, sigma1):
    salida = (normal_pdf(x_vector, theta0, sigma0) + normal_pdf(x_vector, theta1, sigma1))/2
    return(salida)

def f_gauss3(x_vector, theta0, theta1, theta2, sigma0, sigma1, sigma2):
    salida = (normal_pdf(x_vector, theta0, sigma0) + normal_pdf(x_vector, theta1, sigma1) + 
              normal_pdf(x_vector, theta2, sigma2))/3
    return(salida)


x_val = np.arange(0, 1000, 1)
g_val = (normal_pdf(x_val, mu=100, sigma=50) + normal_pdf(x_val, mu=700, sigma=50))/2

params, cov = curve_fit(f_gauss3, x_val, g_val, [300, 500, 700, 100, 100, 100])

print(params)

plt.subplot(2,1,1)
plt.plot(x_val, g_val)
plt.subplot(2,1,2)
plt.plot(x_val, f_gauss3(x_val, *params))
plt.show()