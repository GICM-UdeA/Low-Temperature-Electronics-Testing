import sys
import time
import datetime
import os
import matplotlib.pyplot as plt
from DAQ_multimetros import Multimetro
from motor_paso import MotorPaso
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
import numpy as np

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cryo-GICM")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.lbl_prueba = QLabel("Nombre de la Prueba:")
        self.edit_prueba = QLineEdit()
        self.layout.addWidget(self.lbl_prueba)
        self.layout.addWidget(self.edit_prueba)

        self.lbl_experimentador = QLabel("Nombre del Experimentador:")
        self.edit_experimentador = QLineEdit()
        self.layout.addWidget(self.lbl_experimentador)
        self.layout.addWidget(self.edit_experimentador)

        self.lbl_fecha_hora = QLabel("Fecha y Hora de la Prueba:")
        self.lbl_fecha_hora_auto = QLabel()
        self.layout.addWidget(self.lbl_fecha_hora)
        self.layout.addWidget(self.lbl_fecha_hora_auto)

        self.lbl_altura_total = QLabel("Altura Total de Barrido (cm):")
        self.edit_altura_total = QLineEdit()
        self.layout.addWidget(self.lbl_altura_total)
        self.layout.addWidget(self.edit_altura_total)

        self.lbl_dy = QLabel("Valor de paso de motor (cm):")
        self.edit_dy = QLineEdit()
        self.layout.addWidget(self.lbl_dy)
        self.layout.addWidget(self.edit_dy)

        self.btn_correr_prueba = QPushButton("Correr Prueba")
        self.btn_correr_prueba.clicked.connect(self.run_test)
        self.layout.addWidget(self.btn_correr_prueba)

        # Botón "Ir a origen"
        self.btn_ir_a_origen = QPushButton("Ir a Origen")
        self.btn_ir_a_origen.clicked.connect(self.ir_a_origen)
        self.layout.addWidget(self.btn_ir_a_origen)

        self.central_widget.setLayout(self.layout)

        # Obtener la fecha y hora del sistema al iniciar la aplicación
        now = datetime.datetime.now()
        self.lbl_fecha_hora_auto.setText(now.strftime("%Y-%m-%d %H:%M:%S"))

    def ir_a_origen(self):
        # Esta función se ejecutará al presionar el botón "Ir a Origen"
        motor = MotorPaso("COM10")
        motor.conectar()
        motor.enviar_numero(100)
        time.sleep(0.1)
        motor.desconectar()


    def run_test(self):
        nombre_prueba = self.edit_prueba.text()
        nombre_experimentador = self.edit_experimentador.text()

        altura_total = float(self.edit_altura_total.text())
        dy = float(self.edit_dy.text())

        if not nombre_prueba or not nombre_experimentador:
            print("Por favor, complete todos los campos.")
            return

        # Obtener la fecha y hora actual
        now = datetime.datetime.now()
        fecha_hora_prueba = now.strftime("%Y-%m-%d %H:%M:%S")

        # Calcular el número de lecturas en función de la altura total y el valor de paso del motor
        n_lecturas = int(altura_total / abs(dy))

        # Crear una carpeta con el nombre de la prueba y la fecha
        folder_name = f"{nombre_prueba}_{now.strftime('%Y-%m-%d')}"
        os.makedirs(folder_name, exist_ok=True)

        # Ruta completa para el archivo de texto y la gráfica
        txt_file_path = os.path.join(folder_name, f"{nombre_prueba}.txt")
        graph_file_path = os.path.join(folder_name, f"{nombre_prueba}.png")

        # Inicializar motor y multimetro
        motor = MotorPaso("COM10")
        multimetro1 = Multimetro("COM26")

        motor.conectar()
        multimetro1.connect()

        last_10_values = []  # Lista para almacenar los últimos 10 valores
        T_values = []

        for i in range(0,n_lecturas):
            valor1 = multimetro1.read_value()
            last_10_values.append(valor1)

            # Mantener solo los últimos 10 valores en la lista
            if len(last_10_values) > 10:
                last_10_values.pop(0)

            # Calcular la diferencia entre el último valor y el primero de los últimos 10 valores
            diff = abs(last_10_values[-1] - last_10_values[0])

            # Si la diferencia es menor que 0.2, salimos del bucle
            if diff < 0.2:
                T_values.append(last_10_values[-1])
                motor.enviar_numero(dy)
                i+=1

        motor.desconectar()

        # Guardar los datos en el archivo de texto en la carpeta
        with open(txt_file_path, "w") as f:
            f.write(f"Nombre de la Prueba: {nombre_prueba}\n")
            f.write(f"Nombre del Experimentador: {nombre_experimentador}\n")
            f.write(f"Fecha y Hora de la Prueba: {fecha_hora_prueba}\n")
            f.write(f"Altura Total de Barrido (cm): {altura_total}\n")
            f.write(f"Valor de paso de motor (cm): {dy}\n")
            f.write(f"Valores del Multimetro 1: {T_values}\n")

        # Graficar los valores y guardar la gráfica en la carpeta
        plt.plot(T_values)
        plt.title("Height vs Temperature")
        plt.ylabel("T [°C]")
        plt.xlabel("z [cm]")
        plt.grid()
        plt.savefig(graph_file_path)
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())
