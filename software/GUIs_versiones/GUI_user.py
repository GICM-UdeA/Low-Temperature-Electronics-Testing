import sys
import time
import datetime
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from DAQ_multimetros import Multimetro
from motor_paso import MotorPaso
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

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

        self.lbl_interval = QLabel("Intervalo (segundos):")
        self.edit_interval = QLineEdit()
        self.layout.addWidget(self.lbl_interval)
        self.layout.addWidget(self.edit_interval)

        self.lbl_dy = QLabel("Valor de paso de motor (cm):")
        self.edit_dy = QLineEdit()
        self.layout.addWidget(self.lbl_dy)
        self.layout.addWidget(self.edit_dy)

        self.btn_correr_prueba = QPushButton("Correr Prueba")
        self.btn_correr_prueba.clicked.connect(self.run_test)
        self.layout.addWidget(self.btn_correr_prueba)

        self.central_widget.setLayout(self.layout)

        # Obtener la fecha y hora del sistema al iniciar la aplicación
        now = datetime.datetime.now()
        self.lbl_fecha_hora_auto.setText(now.strftime("%Y-%m-%d %H:%M:%S"))

    def run_test(self):
        nombre_prueba = self.edit_prueba.text()
        nombre_experimentador = self.edit_experimentador.text()

        altura_total = float(self.edit_altura_total.text())
        interval = float(self.edit_interval.text())
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

        # Aquí puedes ejecutar el script proporcionado con los valores ingresados.
        motor = MotorPaso("COM9")
        multimetro1 = Multimetro("COM23")

        motor.conectar()
        multimetro1.connect()

        values1 = []
        values_temporal = []
        for _ in range(n_lecturas):
            for _ in range(int(interval)):
             valor1_temporal = multimetro1.read_value()
             values_temporal.append(valor1_temporal)
             mean_value = np.mean(values_temporal)
            values1.append(mean_value)
            motor.enviar_numero(dy)
            time.sleep(interval)

        motor.desconectar()
        print("Prueba finalizada")

        # Guardar los datos en el archivo de texto en la carpeta
        with open(txt_file_path, "w") as f:
            f.write(f"Nombre de la Prueba: {nombre_prueba}\n")
            f.write(f"Nombre del Experimentador: {nombre_experimentador}\n")
            f.write(f"Fecha y Hora de la Prueba: {fecha_hora_prueba}\n")
            f.write(f"Altura Total de Barrido (cm): {altura_total}\n")
            f.write(f"Intervalo (segundos): {interval}\n")
            f.write(f"Valor de paso de motor (cm): {dy}\n")
            f.write(f"Valores del Multimetro 1: {values1}\n")

        # Crear un archivo CSV en la carpeta con el mismo nombre que la prueba y la fecha
        csv_file_path = os.path.join(folder_name, f"{nombre_prueba}_{now.strftime('%Y-%m-%d')}.csv")

        # Guardar los datos en el archivo CSV
        with open(csv_file_path, mode='w', newline='') as csv_file:
            fieldnames = ["Altura (cm)", "Temperatura (C)"]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            writer.writeheader()
            
            altura_actual = 0
            for temperatura in values1:
                writer.writerow({"Altura (cm)": altura_actual, "Temperatura (C)": temperatura})
                altura_actual += abs(dy)



        # Graficar los valores y guardar la gráfica en la carpeta
        plt.plot(values1)
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
