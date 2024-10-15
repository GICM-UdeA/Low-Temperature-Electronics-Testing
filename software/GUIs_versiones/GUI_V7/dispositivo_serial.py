import serial

class criogenia_serial:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

    def conectar(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
            return True
        except serial.SerialException as e:
            print(f"Error al conectar: {e}")
            return False

    def desconectar(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            return True
        else:
            return False

    def read_temp(self):
        if not self.ser or not self.ser.is_open:
            print("El puerto serial no está abierto. Primero, debes conectar.")
            return None

        try:
            self.ser.write(b'T')
            response = self.ser.readline().decode().strip()
            if response.startswith('U') and 'D' in response:
                values = response.split('D')
                tu = float(values[0][1:])
                td = float(values[1])
                return {'tu': tu, 'td': td}
            else:
                print("Respuesta del Arduino no válida.")
                return None
        except serial.SerialException as e:
            print(f"Error al leer la temperatura: {e}")
            return None
        
    def motor(self, numero):
        if self.ser:
            try:
                # Agregar la letra 'M' al inicio del número
                mensaje = f"M{numero}".encode('utf-8')
                self.ser.write(mensaje)
                #print(f"{numero} cm enviado.")
            except Exception as e:
                print(f"Error al enviar el número: {e}")
        else:
            print("La conexión no está establecida. Debes conectar primero.")
