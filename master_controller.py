import subprocess

process1 = subprocess.Popen(r'C:\Users\LawrenceNeal\Desktop\Sailbot Code\acmr-simulator\Forwarder_Device.py',stdin = subprocess.PIPE, stdout = subprocess.PIPE )
output1 = process1.communicate()
print output1[0]

process2 = subprocess.Popen(r'C:\Users\LawrenceNeal\Desktop\Sailbot Code\acmr-simulator\Dummy_Publisher.py',stdin = subprocess.PIPE, stdout = subprocess.PIPE)
output2 = process2.communicate()
print output2[0]