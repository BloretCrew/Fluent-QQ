import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

def main():
    print("Starting minimal app...")
    app = QApplication(sys.argv)
    w = QMainWindow()
    w.setWindowTitle("Minimal Test")
    w.show()
    print("Window shown, entering exec")
    # sys.exit(app.exec())
    # Just close immediately for test
    print("Closing...")

if __name__ == "__main__":
    main()
