import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QTimer
from pt100_serial import PT100_serial
import time

# Configurar la comunicación serial con los Arduinos
pt1001 = PT100_serial("COM28")
pt1002 = PT100_serial("COM10")
pt1001.conectar()
pt1002.conectar()

# Función para obtener los datos de temperatura de los Arduinos
def obtener_temperaturas():
    temp1 = pt1001.read_temp()
    temp2 = pt1002.read_temp()
    return temp1, temp2+2.5

# Función para actualizar el gráfico con los nuevos datos
def actualizar_grafico():
    temp1, temp2 = obtener_temperaturas()
    window.x.append(time.time())
    window.y1.append(temp1)
    window.y2.append(temp2)
    window.ax.clear()
    window.ax.set_xlabel('Tiempo')
    window.ax.set_ylabel('Temperatura (°C)')
    window.ax.plot(window.x, window.y1, label='Sensor 1: {:.2f} °C'.format(temp1))
    window.ax.plot(window.x, window.y2, label='Sensor 2: {:.2f} °C'.format(temp2))
    window.ax.legend()
    window.ax.grid(True)  # Agregar cuadrícula
    window.ax.set_xticklabels([])
    window.canvas.draw()

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

        self.reset_button = QPushButton('Resetear Datos')
        self.reset_button.clicked.connect(resetear_datos)
        layout.addWidget(self.reset_button)

        self.widget = QWidget()
        self.widget.setLayout(layout)
        self.setCentralWidget(self.widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(actualizar_grafico)
        self.timer.start(500)  # Actualizar cada 500 ms

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
