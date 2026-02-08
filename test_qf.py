import sys
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow

def main():
    print("Starting QFluentWidgets test...")
    app = QApplication(sys.argv)
    w = FluentWindow()
    w.show()
    print("FluentWindow shown")
    # app.exec()
    print("Closing...")

if __name__ == "__main__":
    main()
