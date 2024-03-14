import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit



def normal_pdf(x_vector, mu=0, sigma=1):
    return (1/(sigma*np.sqrt(2*np.pi)))*np.exp(-((x_vector - mu)/sigma)**2/2)

def f(x_vector, theta0, theta1, sigma0, sigma1):
    # sigma = 100
    return 0.5*((1/(sigma0*np.sqrt(2*np.pi)))*np.exp(-((x_vector - theta0)/sigma0)**2/2) + 
            (1/(sigma1*np.sqrt(2*np.pi)))*np.exp(-((x_vector - theta1)/sigma1)**2/2))


def f_gauss1(x_vector, theta0, sigma0):
    salida = normal_pdf(x_vector, theta0, sigma0)
    return(salida)

def f_gauss2(x_vector, theta0, theta1, sigma0, sigma1):
    salida = (normal_pdf(x_vector, theta0, sigma0) + normal_pdf(x_vector, theta1, sigma1))/2
    return(salida)

def f_gauss3(x_vector, theta0, theta1, theta2, sigma0, sigma1, sigma2):
    salida = (normal_pdf(x_vector, theta0, sigma0) + normal_pdf(x_vector, theta1, sigma1) + 
              normal_pdf(x_vector, theta2, sigma2))/3
    return(salida)






# Test1
# x_val = np.arange(0, 1000, 1) Para
# g_val = (normal_pdf(x_val, mu=100, sigma=50) + normal_pdf(x_val, mu=700, sigma=50))/2


# Crear funcion, que reciba thetas y sigmas, calcule funcion g y determine cual es la mejor aproximacion 3 columnas, 2 columnas o 1 columna
# Basado en funcion de akaike, o también puede ser en sobrelape de las funciones de probabilidad (Asegurar mayor al 90%??).. Jensen Shannon, o Kullback Leibler son 
# otra posibilidad

x_val = np.arange(0, 254, 1)

g_val = (normal_pdf(x_val, mu= 74.5, sigma= 27)
    + normal_pdf(x_val, mu= 177, sigma= 24)
    + normal_pdf(x_val, mu= 100, sigma= 28)
    + normal_pdf(x_val, mu= 208, sigma= 11))/4

params1, cov1 = curve_fit(f_gauss1, x_val, g_val, [500, 100])
params2, cov2 = curve_fit(f_gauss2, x_val, g_val, [300, 500, 100, 100])
params3, cov3 = curve_fit(f_gauss3, x_val, g_val, [300, 500, 700, 100, 100, 100])

sum_error1 = sum((g_val - f_gauss1(x_val, *params1))**2)
sum_error2 = sum((g_val - f_gauss2(x_val, *params2))**2)
sum_error3 = sum((g_val - f_gauss3(x_val, *params3))**2)

print("Means")
print(params1[0:1])
print(np.sort(params2[0:2]))
print(np.sort(params3[0:3]))

idx2 = np.argsort(params2[0:2])+2
idx3 = np.argsort(params3[0:3])+3

print("Sigma")
print(params1[1:])
print(params2[idx2])
print(params3[idx3])


plt.subplot(1,3,1)
plt.title("1 - Gaussian")
plt.plot(x_val, g_val)
plt.plot(x_val, f_gauss1(x_val, *params1))
plt.xlabel("Error %.5f"%sum_error1)

plt.subplot(1,3,2)
plt.title("Sum of 2 gaussians")
plt.plot(x_val, g_val)
plt.plot(x_val, f_gauss2(x_val, *params2))
plt.xlabel("Error %.5f"%sum_error2)

plt.subplot(1,3,3)
plt.title("Sum of 3 gaussians")
plt.plot(x_val, g_val)
plt.plot(x_val, f_gauss3(x_val, *params3))
plt.xlabel("Error %.5f"%sum_error3)

plt.show()




