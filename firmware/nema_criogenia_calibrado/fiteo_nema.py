import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Datos de pasos
pasos = np.array([500, 600, 700, 800, 900, 1000, 1100, 1500, 1700, 1900, 2100, 2500, 3000, 7500])

# Datos de distancia en cm
distancia = np.array([2.1, 3.2, 3.6, 4.2, 4.8, 5.2, 5.8, 7.9, 9, 10, 11.1, 13.2, 15.9, 39.5])

# Función lineal para el ajuste de curva
def funcion_lineal(x, a, b):
    return a * x + b

# Realizar el ajuste de curva
parametros, covarianza = curve_fit(funcion_lineal, distancia, pasos)

# Obtener los parámetros ajustados
a, b = parametros

# Generar una serie de puntos para la función ajustada
distancia_ajuste = np.linspace(min(distancia), max(distancia), 100)
pasos_ajuste = funcion_lineal(distancia_ajuste, a, b)

# Graficar los datos y la función ajustada
plt.plot(distancia, pasos, 'ro', label='Datos')
plt.plot(distancia_ajuste, pasos_ajuste, 'b-', label='Ajuste de curva')
plt.xlabel('Distancia (cm)')
plt.ylabel('Pasos')
plt.legend()
plt.show()

# Imprimir la función ajustada
print("La función que mejor aproxima el valor de paso en función de la distancia real es:")
print("Pasos = {} * Distancia + {}".format(a, b))
