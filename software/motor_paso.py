import serial

class MotorPaso:
    def __init__(self, port):
        self.port = port
        self.serial_connection = None

    def conectar(self):
        try:
            self.serial_connection = serial.Serial(self.port, baudrate=115200, timeout=1)
            print(f"Conexión establecida en el puerto {self.port}")
        except serial.SerialException:
            print("No se pudo establecer la conexión.")

    def desconectar(self):
        if self.serial_connection:
            self.serial_connection.close()
            print("Conexión cerrada.")

    def enviar_numero(self, numero):
        if self.serial_connection:
            try:
                # Agregar la letra 'M' al inicio del número
                mensaje = f"M{numero}".encode('utf-8')
                self.serial_connection.write(mensaje)
                print(f"{numero} cm enviado.")
            except Exception as e:
                print(f"Error al enviar el número: {e}")
        else:
            print("La conexión no está establecida. Debes conectar primero.")


