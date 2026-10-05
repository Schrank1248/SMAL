import subprocess, sys

errors = subprocess.run(["python3", "SMALL_parserV2.py", sys.argv[1], "gign_prg.cpp"], capture_output=True)

if len(str(errors.stdout)) > 3:
	with open("errors.txt", "w") as f:
		f.writelines(str(errors.stdout)+"\n")
else:
	with open("errors.txt", "w") as f:
		f.writelines([])

with open("errors.txt") as f:
	err = f.readlines()
if len(err)>0:
	exit()

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

print(sys.argv)
if sys.argv[3] == "-upload":
	result = subprocess.run([
		"arduino-cli",
		"upload",
		"--fqbn", "arduino:renesas_uno:unor4wifi",
		"-p", sys.argv[2],
		"prg"
	], capture_output=True, text=True)

	print(result.stdout)
	print(result.stderr)
	print("Exit:", result.returncode)
	if result.returncode == 1:
		with open("errors.txt", "w") as f:
			f.writelines(["Upload fehlgeschlagen."])

