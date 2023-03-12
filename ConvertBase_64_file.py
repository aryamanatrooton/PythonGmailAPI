import base64
  
filename='Teri kami Akhil whatsapp status song video _ statu(360P).mp4.bin'

def convert_base64_file(filename):
    file = open(filename, 'rb')
    byte = file.read()
    file.close()
    with open(os.path.join(os.getcwd(), filename[:-4]), 'wb') as _f:
        _f.write(byte)
    print("Attached file  {0} is saved at".format(filename),os.getcwd())