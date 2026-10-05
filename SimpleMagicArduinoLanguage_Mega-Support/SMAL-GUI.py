import tkinter, os, serial, threading
from tkinter import filedialog
from tkinter import ttk
from datetime import datetime
import serial.tools.list_ports

file = ""

conWin = 0
ports = []
UpPort = ""

def conWinClose():
  global conWin, ports, con, UpPort
  if len(ports) > 0:
    upload.config(state="normal")
    UpPort = ports[int(con.get())].device
    print("!!!", UpPort)
    serThr.start()
    upload.config(text = "Upload -> "+UpPort+": "+ports[int(con.get())].description)
  conWin.destroy()

def selectController():
  global conWin, ports, con
  p = serial.tools.list_ports.comports()
  ports = []
  for i in p:
    if i.description != "n/a":
      ports.append(i)
  con.set("0")
  conWin = tkinter.Tk()
  conWin.geometry("500x300")

  for i, port in enumerate(ports):
    if port.description != "n/a":
      print(f"Device: {port.device}, Description: {port.description}, HWID: {port.hwid}")
      tkinter.Radiobutton(conWin, text = port.description, variable = con, value = str(i)).pack()

  done = tkinter.Button(conWin, text = "Fertig", command = conWinClose)
  done.place(rely=1.0, relx=1.0, x=0, y=0, anchor="se", relwidth = 1.0)
  conWin.mainloop()

lines = []

def SERIAL():
  while SERI:
    with serial.Serial(port=UpPort, baudrate=9600, timeout=1) as ser: #115200
      while SerCom and SERI:
        line = ser.readline().decode("utf-8").strip()
        if line:
          lines.append(datetime.now().strftime("%H:%M:%S.%f")[:-3]+" -> "+line+"\n")
    while (not SerCom) and SERI:
      pass

def upload():
  global file, SerCom
  upload.config(text = "einen Moment bitte...")
  SerCom = False
  if file == "" or type(file) == tuple:
    while file == "" or type(file) == tuple:
      file = filedialog.askopenfilename()
    filBTN.config(text = "["+file.split("/")[-1]+"] - Andere Datei waehlen")
  print(file)
  os.system("python3 SMAL.py "+file+" "+UpPort)
  Ls = []
  with open("errors.txt") as f:
    Ls = f.readlines()
  if len(Ls) > 0:
    tkinter.messagebox.showerror("Fehler!", Ls[0])
  SerCom = True
  upload.config(text = "Upload")

def fileSLCT():
  global file
  file = filedialog.askopenfilename()
  if (not file == "") and (not type(file) == tuple):
    filBTN.config(text = "["+file.split("/")[-1]+"] - Andere Datei waehlen")
    print("[[]]")
  print(file)

window = tkinter.Tk()
window.geometry("500x300")

usbBTN = tkinter.Button(window, text = "Controller auswaehlen", command = selectController)
filBTN = tkinter.Button(window, text = "Datei auswaehlen", command = fileSLCT)
upload = tkinter.Button(window, text = "Upload", command = upload)

con = tkinter.StringVar()
upload.config(state="disabled")

usbBTN.pack(fill = "x")
upload.pack(fill = "x")
filBTN.pack(fill = "x")

SerCom = True
SERI = True

serThr = threading.Thread(target=SERIAL)
# serThr.start()


frame = ttk.Frame(window)
frame.pack(padx=20, pady=20, fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame)
scrollbar.pack(side="right", fill="y")

text_label = tkinter.Text(
    frame,
    wrap="word",
    yscrollcommand=scrollbar.set,
    bg=window.cget("bg"),
    relief="flat",
    font=("Arial", 11),
    padx=5, pady=5,
)
text_label.pack(side="left", fill="both", expand=True)
text_label.config(state="disabled")

def queue_pruefen():
  global lines
  scDown = 0
  if scrollbar.get()[1] == 1.0:
    scDown = 1
  text_label.config(state="normal")
  for i in lines:
    text_label.insert("end", i)
  if scDown:
    text_label.see("end")
  text_label.config(state="disabled")
  lines = []
  window.after(10, queue_pruefen)

queue_pruefen()

window.mainloop()

SERI = False
