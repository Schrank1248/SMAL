import subprocess, sys

subprocess.run(["python3", "SMALL_parserV2.py", sys.argv[1], "gign_prg.cpp"])

nfile = []

with open("run1.cpp") as f:
  nfile += f.readlines()
with open("gign_prg.cpp") as f:
  nfile += f.readlines()
with open("run2.cpp") as f:
  nfile += f.readlines()

with open("prg/prg.ino", "w") as f:
  f.writelines(nfile)

subprocess.run([
	"arduino-cli",
	"compile",
	"--fqbn", "arduino:renesas_uno:unor4wifi",
	"prg"
])

result = subprocess.run([
	"arduino-cli",
	"upload",
	"--fqbn", "arduino:renesas_uno:unor4wifi",
	"-p", "/dev/ttyACM0",
	"prg"
], capture_output=True, text=True)

print(result.stdout)
print(result.stderr)
print("Exit:", result.returncode)
