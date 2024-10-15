import sys
import time
import datetime
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from DAQ_multimetros import Multimetro
from motor_paso import MotorPaso
from pt100_serial import PT100_serial
import csv

class LiveGraph(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        #self.canvas.setMinimumSize(600, 1000)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Gráfica en Tiempo Real")
        self.ax.set_xlabel("Muestras")
        self.ax.set_ylabel("Temperatura (°C)")

    def init_plot(self):
        self.line1, = self.ax.plot([], [], label='PT100_1')  # Etiqueta para Valor 1
        self.line2, = self.ax.plot([], [], label='PT100_2')  # Etiqueta para Valor 2
        self.values1 = []
        self.values2 = []
        self.ax.legend()

    def update_graph(self, data):
        self.values1.append(data[0])
        self.values2.append(data[1])
        self.line1.set_data(range(len(self.values1)), self.values1)
        self.line2.set_data(range(len(self.values2)), self.values2)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def clear_plot(self):
        self.values1 = []
        self.values2 = []
        self.line1.set_data([], [])
        self.line2.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

class TestApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cryo-GICM")
        self.setGeometry(100, 100, 800, 1000)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.lbl_prueba = QLabel("Nombre de la Prueba:")
        self.edit_prueba = QLineEdit()
        self.edit_prueba.setFixedWidth(200)  # Establece el ancho fijo deseado
        self.layout.addWidget(self.lbl_prueba)
        self.layout.addWidget(self.edit_prueba)

        self.lbl_experimentador = QLabel("Nombre del Experimentador:")
        self.edit_experimentador = QLineEdit()
        self.edit_experimentador.setFixedWidth(200)  # Establece el ancho fijo deseado
        self.layout.addWidget(self.lbl_experimentador)
        self.layout.addWidget(self.edit_experimentador)

        self.lbl_fecha_hora = QLabel("Fecha y Hora de la Prueba:")
        self.lbl_fecha_hora_auto = QLabel()
        self.layout.addWidget(self.lbl_fecha_hora)
        self.layout.addWidget(self.lbl_fecha_hora_auto)

        self.lbl_altura_total = QLabel("Altura Total de Barrido (cm):")
        self.edit_altura_total = QLineEdit()
        self.edit_altura_total.setFixedWidth(200)  # Establece el ancho fijo deseado
        self.layout.addWidget(self.lbl_altura_total)
        self.layout.addWidget(self.edit_altura_total)

        self.lbl_interval = QLabel("Intervalo (segundos):")
        self.edit_interval = QLineEdit()
        self.edit_interval.setFixedWidth(200)  # Establece el ancho fijo deseado
        self.layout.addWidget(self.lbl_interval)
        self.layout.addWidget(self.edit_interval)

        self.lbl_dy = QLabel("Valor de paso de motor (cm):")
        self.edit_dy = QLineEdit()
        self.edit_dy.setFixedWidth(200)  # Establece el ancho fijo deseado
        self.layout.addWidget(self.lbl_dy)
        self.layout.addWidget(self.edit_dy)

        self.btn_correr_prueba = QPushButton("Correr Prueba")
        self.btn_correr_prueba.setFixedWidth(120)  # Establece el ancho deseado
        self.btn_correr_prueba.setStyleSheet("background-color: green; color: white;") 
        self.btn_correr_prueba.clicked.connect(self.run_test)
        self.layout.addWidget(self.btn_correr_prueba)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedWidth(120)  # Establece el ancho deseado
        self.btn_reset.setStyleSheet("background-color: red; color: white;") 
        self.btn_reset.clicked.connect(self.reset_plot)
        self.layout.addWidget(self.btn_reset)

        self.btn_ir_a_origen = QPushButton("Ir a origen")
        self.btn_ir_a_origen.setFixedWidth(120)  # Establece el ancho deseado
        self.btn_ir_a_origen.clicked.connect(self.go_to_origin)
        self.layout.addWidget(self.btn_ir_a_origen)

        self.btn_guardar_datos = QPushButton("Guardar datos")
        self.btn_guardar_datos.setFixedWidth(120)  # Establece el ancho deseado
        self.btn_guardar_datos.setStyleSheet("background-color: blue; color: white;") 
        self.btn_guardar_datos.clicked.connect(self.save_data)
        self.layout.addWidget(self.btn_guardar_datos)

        self.central_widget.setLayout(self.layout)

        self.live_graph = LiveGraph()
        self.layout.addWidget(self.live_graph)
        self.live_graph.init_plot()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(10)  # Intervalo de actualización en milisegundos

        now = datetime.datetime.now()
        self.lbl_fecha_hora_auto.setText(now.strftime("%Y-%m-%d %H:%M:%S"))

        self.motor = None
        self.multimetro1 = None
        self.n_lecturas = 0
        self.dy = 0

    def run_test(self):
        nombre_prueba = self.edit_prueba.text()
        nombre_experimentador = self.edit_experimentador.text()

        altura_total = float(self.edit_altura_total.text())
        interval = float(self.edit_interval.text())
        self.dy = float(self.edit_dy.text())

        if not nombre_prueba or not nombre_experimentador:
            print("Por favor, complete todos los campos.")
            return

        now = datetime.datetime.now()
        fecha_hora_prueba = now.strftime("%Y-%m-%d %H:%M:%S")

        self.n_lecturas = int(altura_total / abs(self.dy))

        folder_name = f"{nombre_prueba}_{now.strftime('%Y-%m-%d')}"
        os.makedirs(folder_name, exist_ok=True)

        txt_file_path = os.path.join(folder_name, f"{nombre_prueba}.txt")
        graph_file_path = os.path.join(folder_name, f"{nombre_prueba}.png")

        self.motor = MotorPaso("COM25")
        #self.multimetro1 = Multimetro("COM23")
        self.pt1001 = PT100_serial("COM26")
        self.pt1002 = PT100_serial("COM10")

        self.motor.conectar()
        #self.multimetro1.connect()
        self.pt1001.conectar()
        self.pt1002.conectar()

        valor_anterior = None

        for _ in range(self.n_lecturas):
            #valor1 = self.multimetro1.read_value()
            valor1 = self.pt1001.read_temp()
            valor2 = self.pt1002.read_temp()

            if valor1 > 500:
                if valor_anterior is not None:
                    valor1 = valor_anterior

            self.live_graph.update_graph([valor1, valor2])
            valor_anterior = valor1
            self.motor.enviar_numero(self.dy)
            time.sleep(interval)
            QApplication.processEvents()

        self.motor.desconectar()
        self.pt1001.desconectar()
        self.pt1002.desconectar()

    def reset_plot(self):
        self.live_graph.clear_plot()
        self.n_lecturas = 0
        self.dy = 0
        now = datetime.datetime.now() #actualizamos fehca y hora
        self.lbl_fecha_hora_auto.setText(now.strftime("%Y-%m-%d %H:%M:%S"))

    def go_to_origin(self):
        self.motor = MotorPaso("COM9")
        self.motor.conectar()
        time.sleep(0.5)
        self.motor.enviar_numero(50)
        time.sleep(1)
        self.motor.desconectar()

    def update_graph(self):
        pass

    def save_data(self):
        nombre_prueba = self.edit_prueba.text()
        if not nombre_prueba:
            print("Por favor, ingrese el nombre de la prueba.")
            return

        now = datetime.datetime.now()
        folder_name = f"{nombre_prueba}_{now.strftime('%Y-%m-%d')}"
        os.makedirs(folder_name, exist_ok=True)

        # Guardar datos en archivo CSV
        csv_file_path = os.path.join(folder_name, f"{nombre_prueba}.csv")
        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Valor1", "Valor2"])  # Encabezados de las columnas

            # Agregar los datos de valor1 y valor2 en cada iteración
            for i in range(len(self.live_graph.values1)):
                csv_writer.writerow([self.live_graph.values1[i], self.live_graph.values2[i]])

        # Guardar información de la prueba en archivo de texto (.txt)
        txt_file_path = os.path.join(folder_name, f"{nombre_prueba}.txt")
        with open(txt_file_path, 'w') as txtfile:
            txtfile.write(f"Nombre de la Prueba: {nombre_prueba}\n")
            txtfile.write(f"Fecha y Hora de la Prueba: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write(f"Nombre del Experimentador: {self.edit_experimentador.text()}\n")
            txtfile.write(f"Altura Total de Barrido (cm): {self.edit_altura_total.text()}\n")
            txtfile.write(f"Intervalo (segundos): {self.edit_interval.text()}\n")
            txtfile.write(f"Valor de paso de motor (cm): {self.edit_dy.text()}\n")

        graph_file_path = os.path.join(folder_name, f"{nombre_prueba}.png")
        self.live_graph.figure.savefig(graph_file_path)

        print(f"Datos guardados en: {folder_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestApp()
    window.show()
    sys.exit(app.exec_())