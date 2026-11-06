import sys
import os
# Configurar la variable de entorno para que Matplotlib sepa que debe usar pyside
os.environ['QT_API'] = 'PySide6'
import numpy as np
import matplotlib
# indicarle a matplotlib que el motor de renderizado grafico sera qt
matplotlib.use('QtAgg')
# importar la clase que convierte la figura de matplotlib en widget compatible con qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# importar la clase que crea el lienzo o contenedor grafico general
from matplotlib.figure import Figure

# importar las herramientas base de PySide6 para la ventana y el diseño (CORREGIDO: PySide6 en mayúscula)
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
# importar la clase visual generada desde el archivo .ui compilado
from ui_primer import Ui_MainWindow

class AnalizadorApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__() # inicializar las clases madres
        self.setupUi(self) # configurar la interfaz grafica
        
        # CORREGIDO: Ajustado a los nombres reales de ui_primer.py
        self.textEdit.setPlainText("1.0")   # Amplitud (textEdit)
        self.textEdit_2.setPlainText("2.0") # Frecuencia (textEdit_2)

        # CORREGIDO: Sintaxis de color arreglada
        self.figure = Figure(facecolor='#57E389') 
        self.canvas = FigureCanvas(self.figure) # crear un lienzo de matplotlib
        self.ax = self.figure.add_subplot(111) # agregar un subgrafico a la figura
        
        layout = QVBoxLayout(self.widget) # crear un diseño vertical para el widget central
        layout.setContentsMargins(0, 0, 0, 0) # eliminar los margenes del diseño
        layout.addWidget(self.canvas) # agregar el lienzo de matplotlib al diseño vertical

        self.pushButton_Actualizar.clicked.connect(self.actualizar_grafico) 
        self.actualizar_grafico() 

    def actualizar_grafico(self):
        try:
            amplitud = float(self.textEdit.toPlainText().strip())
            frecuencia = float(self.textEdit_2.toPlainText().strip())
        except ValueError:
            self.statusBar().showMessage(
                "Ingresá valores numéricos para la amplitud y la frecuencia."
            )
            return

        if not np.isfinite(amplitud) or not np.isfinite(frecuencia):
            self.statusBar().showMessage(
                "La amplitud y la frecuencia deben ser números finitos."
            )
            return

        self.statusBar().clearMessage()

        t = np.linspace(0, 2, 1000)
        y = amplitud * np.sin(2 * np.pi * frecuencia * t)
        
        self.ax.clear() # limpiar el grafico anterior
        self.ax.set_facecolor((87/255, 227/255, 137/255)) # establecer el color de fondo del grafico
        self.ax.plot(t, y, color='black') # dibujar la nueva curva en el grafico
        self.ax.set_xlabel('Tiempo (s)', color='black', fontsize=11) 
        self.ax.set_ylabel('Amplitud', color='black', fontsize=11) 
        self.ax.tick_params(colors='black') # CORREGIDO: es colors, no color
        self.ax.grid(True, color='gray', linestyle='--', alpha=0.5) 
        
        for spine in self.ax.spines.values(): 
            spine.set_color('black')
            
        self.figure.tight_layout() 
        self.canvas.draw() 

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    window = AnalizadorApp() 
    window.show() 
    sys.exit(app.exec())