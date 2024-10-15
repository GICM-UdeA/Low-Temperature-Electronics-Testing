import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import serial
from motor_paso import MotorPaso
from collections import deque

myMotor = MotorPaso("COM9")
myMotor.conectar()

def enviar_numero_motor(window):
    numero = float(window.line_edit.text())  # Obtener el número de la casilla de texto
    myMotor.enviar_numero(numero)  # Enviar el número al motor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Inicializar la conexión serial
        self.ser = serial.Serial('COM17', 115200)  # Reemplaza 'COMX' con el puerto serial correcto

        # Crear las colas para almacenar los datos
        self.cola1 = deque(maxlen=50)
        self.cola2 = deque(maxlen=50)

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Gráfica en Tiempo Real')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Crear la gráfica
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.grid()
        self.line1, = self.ax.plot([], label='Sensor 1: ')
        self.line2, = self.ax.plot([], label='Sensor 2: ')
        self.ax.legend()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        # Crear una casilla de texto y un botón para enviar el número al motor
        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)
        move_button = QPushButton('Mover motor', self)
        move_button.setFixedWidth(200)
        move_button.clicked.connect(lambda: enviar_numero_motor(self))
        layout.addWidget(move_button)

        # Crear el botón para cerrar la conexión serial
        button = QPushButton('Cerrar conexión serial', self)
        button.setFixedWidth(200)
        button.clicked.connect(self.close_serial)
        layout.addWidget(button)

        self.show()

        # Iniciar la actualización de la gráfica
        self.update_plot()

    def update_plot(self):
        try:
            while True:
                data = self.ser.readline().decode().strip().split(',')
                if len(data) == 2:
                    temp1, temp2 = float(data[1]), float(data[0])
                    self.cola1.append(temp1)
                    self.cola2.append(temp2)
                    self.line1.set_data(range(len(self.cola1)), self.cola1)
                    self.line2.set_data(range(len(self.cola2)), self.cola2)
                    self.line1.set_label(f'Sensor 1: {temp1}')
                    self.line2.set_label(f'Sensor 2: {temp2}')
                    self.ax.relim()
                    self.ax.autoscale_view()
                    self.ax.legend()
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()
        except KeyboardInterrupt:
            pass

    def close_serial(self):
        self.ser.close()
        myMotor.desconectar()
        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
