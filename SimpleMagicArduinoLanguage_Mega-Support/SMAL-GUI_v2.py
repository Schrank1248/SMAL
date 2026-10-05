import sys
import os
import re
import threading
import time
import serial
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextBrowser
from PyQt6 import uic
from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerCustom

SERI = True
SerPau = True
SerPauRec = False
def SERIAL(log):
    global port, SerPauRec, SerPau
    while SERI:
        while SerPau and SERI:
            with serial.Serial(port=port, baudrate=9600, timeout=0.5) as ser: #115200
                line = ser.readline().decode("utf-8").strip()
                if line:
                    log.log_nachricht(datetime.now().strftime("%H:%M:%S.%f")[:-3]+" -> "+line, farbe = "#BBBBBB")
        if not SerPau:
            print("!!!")
            SerPauRec = True
            while not SerPau:
                pass

# --- 1. LADE DIE UI-DATEI ALS MAIN WINDOW TEMPLATE ---
base_path = os.path.dirname(__file__)
# !!! ERSETZE "mein_layout.ui" MIT DEINEM ECHTEN UI-DATEINAMEN !!!
UI_DATEI = os.path.join(base_path, "interface.ui")

Ui_MainWindow, QBaseClass = uic.loadUiType(UI_DATEI)

port = "*port*"

filename = "testSkript"

# --- 2. DER MAẞGESCHNEIDERTE SMAL-LEXER FÜR DEINE SPRACHE ---
class SMALLexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Stil-IDs für Scintilla
        self.STYLE_DEFAULT = 0
        self.STYLE_KEYWORD = 1      # control
        self.STYLE_FUNCTION = 2     # commands
        self.STYLE_BUILTIN = 3      # special
        self.STYLE_ATWORD = 4       # @w+
        self.STYLE_DECIMAL = 5      # Zahlen
        self.STYLE_STRING = 6       # Strings '' oder ""

        # Wortlisten aus deiner Kate-XML Definition
        self.control_words = {"event", "if", "while", "for"}
        self.commands_words = {"log", "setPin", "switchPin", "freeze", "asyncDelay", "setServo", "setPinAnalog", "getPin", "getPinAnalog"}
        self.special_words = {"init", "frameUpdate", "secondUpdate", "onPressed", "onReleased"}

    def language(self):
        return "SMAL"

    def description(self, style):
        styles = {
            self.STYLE_DEFAULT: "Default",
            self.STYLE_KEYWORD: "Keyword",
            self.STYLE_FUNCTION: "Function",
            self.STYLE_BUILTIN: "Built-in",
            self.STYLE_ATWORD: "AtWord",
            self.STYLE_DECIMAL: "Decimal",
            self.STYLE_STRING: "String"
        }
        return styles.get(style, "Default")

    def styleText(self, start, end):
        self.startStyling(start)
        text = self.parent().text()[start:end]

        # Tokenizer für Wörter, Strings, @Variablen und Dezimalzahlen
        tokens = re.findall(r'(@\w+|\b\d+(?:\.\d+)?\b|"[^"\\]*"|\'[^\'\\]*\'|\w+|\s+|\W)', text)

        for token in tokens:
            length = len(token.encode('utf-8'))

            if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                self.setStyling(length, self.STYLE_STRING)
            elif token.startswith('@'):
                self.setStyling(length, self.STYLE_ATWORD)
            elif re.match(r'^\d+(?:\.\d+)?$', token):
                self.setStyling(length, self.STYLE_DECIMAL)
            elif token in self.control_words:
                self.setStyling(length, self.STYLE_KEYWORD)
            elif token in self.commands_words:
                self.setStyling(length, self.STYLE_FUNCTION)
            elif token in self.special_words:
                self.setStyling(length, self.STYLE_BUILTIN)
            else:
                self.setStyling(length, self.STYLE_DEFAULT)


# --- 3. DIE HAUPT-ANWENDUNG (MAIN WINDOW) ---
class StartApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.serThr = threading.Thread(target = SERIAL, args = (self,), daemon = True)

        # Baut das Fenster und alle verschachtelten Widgets vollautomatisch auf
        self.setupUi(self)

        # !!! PASSE HIER DIE RECHTEN NAMEN AN, FALLS DU SIE IM DESIGNER GEÄNDERT HAST !!!
        self.editor = getattr(self, "frame", None)          # objectName deines Scintilla-Editor-Feldes
        self.konsole = getattr(self, "textBrowser", None)   # objectName deines QTextBrowsers (Fehlerausgabe)
        self.upload_btn = getattr(self, "uploadBTN", None)  # objectName deines Upload-Buttons
        self.compile_btn = getattr(self, "compileBTN", None)  # objectName deines Upload-Buttons

        self.menu_speichern = getattr(self, "actionSpeichern", None)
        if self.menu_speichern:
            self.menu_speichern.triggered.connect(self.save)
        self.menu_oeffnen = getattr(self, "actionOeffnen", None)
        if self.menu_oeffnen:
            self.menu_oeffnen.triggered.connect(self.open)

        # 1. Verbindung für den Button-Klick herstellen
        if self.upload_btn:
            self.upload_btn.clicked.connect(self.upload)
            print(f"Erfolg: '{self.upload_btn.objectName()}' wurde erfolgreich verbunden!")
        else:
            print("Fehler: Der Upload-Button wurde in der UI-Datei nicht gefunden.")

        if self.compile_btn:
            self.compile_btn.clicked.connect(self.kompile)
            print(f"Erfolg: '{self.compile_btn.objectName()}' wurde erfolgreich verbunden!")
        else:
            print("Fehler: Der Compile-Button wurde in der UI-Datei nicht gefunden.")
        # Verbinde den Port-Auswahl-Button
        self.port_btn = getattr(self, "portBTN", None)
        if self.port_btn:
            self.port_btn.clicked.connect(self.port_auswaehlen)

        # 2. Den Code-Editor konfigurieren
        if self.editor:
            self.setup_editor()

        # 3. Die Fehlerausgabe für den Dark Mode vorbereiten
        if self.konsole:
            self.konsole.setStyleSheet("background-color: #1A1A1A; color: #D4D4D4; font-family: monospace; font-size: 11pt;")
            self.log_nachricht("<center>David Cuntz 2026:<br><b>SMAL-IDE v2.0 running SMAL 1.0</b></center>")

    def setup_editor(self):
        DARK_BG = QColor("#1E1E1E")       # Hintergrundfarbe
        LIGHT_FG = QColor("#D4D4D4")      # Normaler Text (Grauweiß)

        # Lexer instanziieren
        lexer = SMALLexer(self.editor)

        # --- SCHRIFTART FÜR ALLE STILE SESTLEGEN ---
        editor_font = QFont("monospace", 11)
        editor_font.setStyleHint(QFont.StyleHint.TypeWriter)
        lexer.setDefaultFont(editor_font)
        for style in range(128):
            lexer.setFont(editor_font, style)

        # Standardfarben zuweisen
        lexer.setDefaultColor(LIGHT_FG)
        lexer.setDefaultPaper(DARK_BG)

        # Farben für die einzelnen Kate-Elemente definieren
        lexer.setColor(LIGHT_FG, lexer.STYLE_DEFAULT)
        lexer.setColor(QColor("#E5C07B"), lexer.STYLE_KEYWORD)   # control (Gelb/Gold)
        lexer.setColor(QColor("#61AFEF"), lexer.STYLE_FUNCTION)  # commands (Blau)
        lexer.setColor(QColor("#C678DD"), lexer.STYLE_BUILTIN)   # special (Lila)
        lexer.setColor(QColor("#DE5577"), lexer.STYLE_ATWORD)    # @Wort (Pink/Rot)
        lexer.setColor(QColor("#D19A66"), lexer.STYLE_DECIMAL)   # Zahlen (Orange)
        lexer.setColor(QColor("#98C379"), lexer.STYLE_STRING)    # Strings (Grün)

        # Jedem Stil den dunklen Hintergrund verpassen
        for style in range(128):
            lexer.setPaper(DARK_BG, style)

        # Lexer an den Editor koppeln
        self.editor.setLexer(lexer)

        # --- TABULATOR-EINSTELLUNGEN (Zwingend 2 Leerzeichen) ---
        self.editor.setIndentationsUseTabs(False)  # Keine echten Tabs (\t)
        self.editor.setTabWidth(2)                 # Genau 2 Leerzeichen Breite
        self.editor.setAutoIndent(True)            # Automatische Einrückung bei Enter

        # Cursor & aktive Zeile anpassen
        self.editor.setCaretForegroundColor(QColor("#FFFFFF")) # Weißer Cursor
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor("#2A2A2A")) # Zeilen-Highlighting

        # Zeilennummern-Rand einstellen
        self.editor.setMarginType(1, QsciScintilla.MarginType.NumberMargin)
        self.editor.setMarginWidth(1, "0000")
        self.editor.setMarginLineNumbers(1, True)
        self.editor.setMarginsBackgroundColor(QColor("#252525"))
        self.editor.setMarginsForegroundColor(QColor("#858585"))

        # UTF-8 erzwingen
        self.editor.setUtf8(True)

        # Optional: Standard-Code beim ersten Start anzeigen
        test_code = "@device (OutputPin 2)\nevent (secondUpdate)\n  switchPin(0)\n"
        self.editor.setText(test_code)

    def log_nachricht(self, text, farbe="#D4D4D4"):
        """Hilfsfunktion, um formatierte Nachrichten in die Fehlerausgabe zu schreiben"""
        if self.konsole:
            self.konsole.append(f"<span style='color: {farbe};'>{text}</span>")
            self.konsole.ensureCursorVisible()

    # --- DIESER CODE WIRD BEIM BUTTON-KLICK AUSGEFÜHRT ---
    def upload(self):
        global SerPauRec, SerPau
        SerPau = False
        while SerPauRec == False:
            pass
        SerPauRec = False
        self.konsole.clear() # Konsole leeren vor neuem Vorgang

        self.log_nachricht("<b>Hochladen...</b>", farbe="#61AFEF")

        QApplication.processEvents()

        code = self.editor.text()

        with open(filename+".sml", "w") as f:
            f.writelines([code])

        os.system("python3 SMAL.py "+filename+".sml "+port+" -upload")

        with open("errors.txt") as f:
            err = f.readlines()
        if len(err)>0:
            print(err[0])
            self.log_nachricht("<b>[FEHLER]</b> "+err[0], farbe = "#FF6666")
        else:
            self.log_nachricht("<b>[FERTIG]</b>", farbe="#61AFEF")
        SerPau = True

    def kompile(self):
        global port
        self.konsole.clear() # Konsole leeren vor neuem Vorgang

        self.log_nachricht("<b>Kompilieren...</b>", farbe="#61AFEF")
        QApplication.processEvents()
        code = self.editor.text()

        with open(filename+".sml", "w") as f:
            f.writelines([code])

        os.system("python3 SMAL.py "+filename+".sml "+port+" -noupload")

        with open("errors.txt") as f:
            err = f.readlines()
        if len(err)>0:
            print(err[0])
            self.log_nachricht("<b>[FEHLER]</b> "+err[0], farbe = "#FF6666")
        else:
            self.log_nachricht("<b>[FERTIG]</b>", farbe="#61AFEF")
    def port_auswaehlen(self):
        global port
        # 1. Alle verfügbaren Ports am PC automatisch suchen
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()

        # Erstellt eine Liste mit den Namen (z.B. ['/dev/ttyACM0', '/dev/ttyUSB0'])
        port_liste = []
        portF = []

        for p in ports:
            if p.description != "n/a":
                port_liste.append(p.description)
                portF.append(p.device)

        # Falls kein Arduino eingesteckt ist, zeigen wir einen Hinweis
        if not port_liste:
            self.log_nachricht("[WARNUNG] Kein serieller Port gefunden! Ist der Arduino eingesteckt?", farbe="#FFAA00")
            # Ein optionaler Dummy-Wert, damit die Liste nicht komplett leer ist
            port_liste = ["Keine Ports gefunden"]

        # 2. Das Auswahl-Popup (Dropdown) öffnen
        from PyQt6.QtWidgets import QInputDialog

        gewaehlter_port, ok_gedrueckt = QInputDialog.getItem(
            self,
            "Port auswählen",                  # Titel des Fensters
            "Wähle den Arduino-Port aus:",     # Text im Fenster
            port_liste,                        # Die Liste der gefundenen Ports
            0,                                 # Welcher Index standardmäßig vorausgewählt ist (0 = der erste)
            False                              # Der Nutzer darf keinen eigenen Text eintippen (nur auswählen)
        )

        # 3. Auswertung: Wenn der Nutzer auf "OK" geklickt hat
        if ok_gedrueckt and gewaehlter_port != "Keine Ports gefunden":
            # Wir speichern den Port in einer Variablen ab
            port = portF[port_liste.index(gewaehlter_port)]

            # Erfolgsmeldung in deiner Fehlerausgabe (QTextBrowser) anzeigen
            self.log_nachricht(f"[INFO] Port erfolgreich gesetzt auf: {portF[port_liste.index(gewaehlter_port)]}", farbe="#55FF55")
            if self.serThr.is_alive():
                SERI = False
                self.serThr.join()
                SERI = True
            self.serThr.start()
        else:
            self.log_nachricht("[INFO] Port-Auswahl abgebrochen.")
    def save(self):
        from PyQt6.QtWidgets import QFileDialog

        if not self.editor:
            return

        dateiname, _ = QFileDialog.getSaveFileName(
            self,
            "SMAL-Datei speichern",
            os.path.dirname(__file__),
            "SMAL Dateien (*.sml);;Alle Dateien (*)"
        )

        if dateiname:
            # Falls der Nutzer die Endung vergessen hat, hängen wir .sml an
            if not dateiname.endswith(".sml"):
                dateiname += ".sml"

            filename = dateiname

            try:
                mein_code = self.editor.text()
                with open(dateiname, "w", encoding="utf-8") as f:
                    f.write(mein_code)
                self.log_nachricht(f"[INFO] Datei erfolgreich gespeichert: {os.path.basename(dateiname)}", farbe="#55FF55")
            except Exception as e:
                self.log_nachricht(f"[FEHLER] Konnte Datei nicht speichern: {e}", farbe="#FF5555")
    def open(self):
        from PyQt6.QtWidgets import QFileDialog

        # Dateidialog öffnen (Filtert standardmäßig nach .sml Dateien)
        dateiname, _ = QFileDialog.getOpenFileName(
            self,
            "SMAL-Datei öffnen",
            os.path.dirname(__file__),
            "SMAL Dateien (*.sml);;Alle Dateien (*)"
        )

        if dateiname:
            try:
                with open(dateiname, "r", encoding="utf-8") as f:
                    code = f.read()
                    if self.editor:
                        self.editor.setText(code)
                self.log_nachricht(f"[INFO] Datei erfolgreich geladen: {os.path.basename(dateiname)}", farbe="#55FF55")
            except Exception as e:
                self.log_nachricht(f"[FEHLER] Konnte Datei nicht laden: {e}", farbe="#FF5555")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartApp()
    window.show()
    sys.exit(app.exec())
