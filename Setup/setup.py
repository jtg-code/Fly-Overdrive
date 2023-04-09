import os
import anki_sdk.utils as utils

def install():
    f = open("requirements.txt", "r")
    for line in f:
        print(f"Installing: {line}")
        os.system(f'pip install {line}')
        print(f"Installed: {line}")
    f.close()

def addCars():
    carlist = utils.scanner(False)
    f = open("address.txt", "w")
    for car in carlist:
        f.write(f"{car.address} \n")
    f.close()



install()
addCars()