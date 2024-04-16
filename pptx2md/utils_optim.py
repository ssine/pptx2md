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

def compute_pdf_overlap(pdf_fun1, pdf_fun2):
    fun_array = np.vstack([pdf_fun1, pdf_fun2])
    intersection = np.min(fun_array, axis=0)
    pdf_overlap = np.sum(intersection)
    return(pdf_overlap)

def fit_column_model(x_val, g_val):

    q1 = np.quantile(x_val, 0.25)
    q2 = np.median(x_val)
    q3 = np.quantile(x_val, 0.75)

    # print("Using q1: %d, q2: %d, q3: %d"%(q1, q2, q3))

    try:
        params1, cov1 = curve_fit(f_gauss1, x_val, g_val, [q2, q2-q1])
    except:
        params1 = [q2, q2-1]
    
    try:
        params2, cov2 = curve_fit(f_gauss2, x_val, g_val, [q1, q3, q1, q1])
    except:
        params2 = [q1, q3, q1, q1]

    try:
        params3, cov3 = curve_fit(f_gauss3, x_val, g_val, [q1, q2, q3, q1, q2-q1, q1])
    except:
        params3 = [q1, q2, q3, q1, q2-q1, q1]

    # Extract area under the curve of the intersection
    auc1 = compute_pdf_overlap(f_gauss1(x_val, *params1), g_val)
    auc2 = compute_pdf_overlap(f_gauss2(x_val, *params2), g_val)
    auc3 = compute_pdf_overlap(f_gauss3(x_val, *params3), g_val)

    print("Using auc1: %.2f, auc2: %.2f, auc3: %.2f"%(auc1, auc2, auc3))

    if auc1>0.86:
        print("Selected 1")
        return(params1)
    elif auc2>0.86:
        print("Selected 2")
        return(params2)
    elif auc3>0.86:
        print("Selected 3")
        return(params3)
    else:
        idx = np.argmax([auc1, auc2, auc3])
        all_params = [params1, params2, params3]
        print("Selected %d"%(idx+1))
        return(all_params[idx])


if __name__ == "__main__":
    # Test1
    # x_val = np.arange(0, 1000, 1) Para
    # g_val = (normal_pdf(x_val, mu=100, sigma=50) + normal_pdf(x_val, mu=700, sigma=50))/2

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

    # Extract area under the curve of the intersection
    auc1 = compute_pdf_overlap(f_gauss1(x_val, *params1), g_val)
    auc2 = compute_pdf_overlap(f_gauss2(x_val, *params2), g_val)
    auc3 = compute_pdf_overlap(f_gauss3(x_val, *params3), g_val)

    plt.subplot(1,3,1)
    plt.title("1 - Gaussian")
    plt.plot(x_val, g_val)
    plt.plot(x_val, f_gauss1(x_val, *params1))
    plt.xlabel("Error %.5f. Intersection: %.3f"%(sum_error1, auc1))

    plt.subplot(1,3,2)
    plt.title("Sum of 2 gaussians")
    plt.plot(x_val, g_val)
    plt.plot(x_val, f_gauss2(x_val, *params2))
    plt.xlabel("Error %.5f. Intersection: %.3f"%(sum_error2, auc2))

    plt.subplot(1,3,3)
    plt.title("Sum of 3 gaussians")
    plt.plot(x_val, g_val)
    plt.plot(x_val, f_gauss3(x_val, *params3))
    plt.xlabel("Error %.5f. Intersection: %.3f"%(sum_error3, auc3))

    plt.show()