import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QTimer
from motor_paso import MotorPaso
from pt100_serial import PT100_serial
import time

# Configurar la comunicación serial con los Arduinos
myMotor = MotorPaso("COM9")
myTemp = PT100_serial("COM15")

myMotor.conectar()
myTemp.conectar()


# Función para obtener los datos de temperatura del Arduinos
def obtener_temperaturas():
    temp = myTemp.read_temp()
    if temp is not None:
        tu = temp.get('tu')
        td = temp.get('td')
        if tu is not None and td is not None:
            #print(f"Temperatura sensor 1 (TU): {tu}")
            #print(f"Temperatura sensor 2 (TD): {td}")
            return tu, td
        else:
            print("No se pudo obtener alguna de las temperaturas.")
    else:
        print("No se pudo obtener ninguna temperatura.")
    return None, None


# Función para controlar el motor de paso
def control_motor(temp2):
     if int(temp2) > 2048:
         time.sleep(5)
         myMotor.enviar_numero(-0.1)  # Enviar la orden al motor de paso

# Función para agregar datos al gráfico
def agregar_datos_grafico(temp1, temp2):
    window.x.append(time.time())
    window.y1.append(temp2)
    window.y2.append(temp1)
    window.ax.clear()
    window.ax.set_xlabel('Tiempo')
    window.ax.set_ylabel('Temperatura (°C)')
    window.ax.plot(window.x, window.y1, label='Sensor U: {:.2f} °C'.format(temp2))
    window.ax.plot(window.x, window.y2, label='Sensor D: {:.2f} °C'.format(temp1))
    window.ax.legend()
    window.ax.grid(True)  # Agregar cuadrícula
    window.ax.set_xticklabels([])
    window.canvas.draw()

# Función para actualizar el gráfico con los nuevos datos
def actualizar_grafico():
    temp1, temp2 = obtener_temperaturas()
    control_motor(temp2)
    agregar_datos_grafico(temp1, temp2)

# Función para resetear los datos del gráfico
def resetear_datos():
    window.x = []
    window.y1 = []
    window.y2 = []
    window.ax.clear()
    window.ax.set_xlabel('Tiempo (s)')
    window.ax.set_ylabel('Temperatura (°C)')
    window.ax.grid(True)  # Agregar cuadrícula
    window.canvas.draw()

# Función para enviar el número al motor
def enviar_numero_motor():
    numero = float(window.line_edit.text())  # Obtener el número de la casilla de texto
    myMotor.enviar_numero(numero)  # Enviar el número al motor
    #time.sleep(0.1)

# Crear la interfaz gráfica con PyQt y Matplotlib
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gráfico de Temperaturas")
        self.setGeometry(100, 100, 800, 600)

        self.x = []
        self.y1 = []
        self.y2 = []

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Tiempo (s)')
        self.ax.set_ylabel('Temperatura (°C)')
        self.ax.set_title('Temperaturas en vivo')
        self.ax.grid(True)  # Agregar cuadrícula
        self.canvas.draw()

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        button_layout = QVBoxLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setFixedWidth(200)  # Establecer un ancho fijo para la casilla de texto
        button_layout.addWidget(self.line_edit)
        self.send_button = QPushButton('Enviar a Motor')
        self.send_button.setFixedWidth(200)  # Establecer un ancho fijo para el botón
        self.send_button.clicked.connect(enviar_numero_motor)
        button_layout.addWidget(self.send_button)
        self.reset_button = QPushButton('Resetear Datos')
        self.reset_button.setFixedWidth(200)  # Establecer un ancho fijo para el botón
        self.reset_button.clicked.connect(resetear_datos)
        button_layout.addWidget(self.reset_button)

        layout.addLayout(button_layout)

        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(actualizar_grafico)
        self.timer.start(1)  # Actualizar cada 500 ms

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
