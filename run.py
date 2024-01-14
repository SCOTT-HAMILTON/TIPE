from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import PhidgetException
import time
import csv

gain = 1
offset = 0

calibrated = False
tared = False


def onVoltageRatioChange(self, voltageRatio):
    if calibrated and tared:
        force = (voltageRatio - offset) * gain
        print(f"Force: {force}")


def tareScale(ch):
    global offset, tared
    num_samples = 50
    dataInterval = ch.getDataInterval() / 1000.0
    for i in range(num_samples):
        offset += ch.getVoltageRatio()
        time.sleep(dataInterval)

    offset /= num_samples
    tared = True


def calibrateScale(ch, targetForce):
    global gain, calibrated
    if not tared:
        print("il faut tarer avant de calibrer...")
        return
    num_samples = 50
    mes = 0
    dataInterval = ch.getDataInterval() / 1000.0
    for i in range(num_samples):
        mes += ch.getVoltageRatio()
        time.sleep(dataInterval)
    gain = targetForce / (mes / num_samples - offset)
    calibrated = True

def runRecord(ch, durationms, output_file):
    if not calibrated or not tared:
        print("Il faut tarer et calibrer avant de faire un enregistrement.")
    start = time.time()
    dataInterval = ch.getDataInterval()/1000.0
    duration = durationms / 1000.0
    n = 0
    with open(output_file, 'w') as csvfile:
        writer = csv.writer(csvfile)
        while True:
            t = time.time()
            mes = gain*(ch.getVoltageRatio()-offset)
            writer.writerow([t, mes])
            n += 1
            if time.time()-start > duration:
                break
            time.sleep(dataInterval - (time.time()-t))
    print(f"{n} entrées on été sauvegardées dans {output_file}.")

def main():
    voltageRatioInput0 = VoltageRatioInput()
    voltageRatioInput0.setOnVoltageRatioChangeHandler(onVoltageRatioChange)
    while True:
        try:
            voltageRatioInput0.openWaitForAttachment(1000)
        except PhidgetException as e:
            print(e)
            r = input("réessayer ? (o/n)")
            if r != "o":
                exit(1)

    voltageRatioInput0.setDataInterval(250)
    voltageRatioInput0.setBridgeGain(Phidget22.BRIDGE_GAIN_128)
    print(f"MaxDataInterval={voltageRatioInput0.getMaxDataInterval()}")
    print(f"DataRate={voltageRatioInput0.getDataRate()}")
    print(f"DataInterval={voltageRatioInput0.getDataInterval()}")
    # voltageRatioInput0.setVoltageRatioChangeTrigger(0)
    # pour recevoir tout les trigger à chaque intervalle

    while True:
        try:
            line = input(">")
            if line == "exit":
                break
            if line == "tare":
                print("Libérez la jauge de contrainte puis appuyez sur entrée...")
                input()
                print("tare en cours...")
                tareScale(voltageRatioInput0)
                print("tare terminé (offset={offset}")
            if line == "calibration":
                print(
                    "appliquez une force connue à la jauge de contrainte puis indiquez la valeur choisie (par exemple '123.4' pour 123,4 N):"
                )
                force = float(input())
                calibrateScale(voltageRatioInput0, force)
                print(f"gain={gain}")
            if line == "set gain":
                gain = float(input("entrez un gain: "))
                calibrated = True
            if line == "record":
                output_file = input("entrez un nom de fichier de sauvegarde: ")
                durationms = int(input("entrez une durée d'enregistrement en ms: "))
                runRecord(voltageRatioInput0, durationms, output_file)
        except (Exception, KeyboardInterrupt):
            pass

    voltageRatioInput0.close()


main()
