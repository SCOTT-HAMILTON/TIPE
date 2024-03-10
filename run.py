from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import PhidgetException
from matplotlib import pyplot as plt
import numpy as np
import time
import csv

gain = 1
offset = 0

calibrated = False
tared = False


def onVoltageRatioChange(self, voltageRatio):
    if calibrated and tared:
        force = (voltageRatio - offset) * gain


def tareScale(ch):
    global offset, tared
    num_samples = 250
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
    num_samples = 250
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
    dataInterval = ch.getDataInterval() / 1000.0
    duration = durationms / 1000.0
    n = 0
    with open(output_file, "w") as csvfile:
        writer = csv.writer(csvfile)
        while True:
            t = time.time()
            mes = gain * (ch.getVoltageRatio() - offset)
            writer.writerow([t, mes])
            n += 1
            if time.time() - start > duration:
                break
            time.sleep(dataInterval - (time.time() - t))
    print(f"{n} entrées on été sauvegardées dans {output_file}.")


def plotCsv(last_record_file):
    data = np.genfromtxt(last_record_file, delimiter=",")
    print(data)
    time = data[:, 0]
    force = data[:, 1]
    plt.close(1)
    plt.figure(1)
    plt.plot(time, force, "*-", label="force=f(t)")
    plt.xlabel("t (s)")
    plt.grid()
    plt.legend()
    plt.show()


def try_connect(ch):
    try:
        ch.openWaitForAttachment(1000)
        ch.setOnVoltageRatioChangeHandler(onVoltageRatioChange)
        ch.setDataInterval(8)  # 125Hz
        ch.setBridgeGain(8)  # GAIN x128
        print(f"MaxDataInterval={ch.getMaxDataInterval()}")
        print(f"DataRate={ch.getDataRate()}")
        print(f"DataInterval={ch.getDataInterval()}")
        print(f"Gain={ch.getBridgeGain()}")
        # ch.setVoltageRatioChangeTrigger(0)
        # pour recevoir tout les trigger à chaque intervalle
        return True
    except PhidgetException as e:
        print(e)
        return False


def main():
    global gain, calibrated, tared
    connected = False
    voltageRatioInput0 = VoltageRatioInput()
    connected = try_connect(voltageRatioInput0)

    last_record_file = None

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
                print(f"tare terminé (offset={offset})")
            if line == "calibrer":
                print(
                    "appliquez une force connue à la jauge de contrainte puis indiquez la valeur choisie (par exemple '123.4' pour 123,4 Kg):"
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
                last_record_file = output_file
            if line == "trace":
                if last_record_file is None:
                    print("impossible de tracer, aucun précédent enregistrement...")
                else:
                    plotCsv(last_record_file)
            if line == "trace-fichier":
                file = input("entrez le nom du fichier à tracer: ")
                plotCsv(file)
            if line == "connect":
                while True:
                    if not try_connect(voltageRatioInput0):
                        r = input("réessayer ? (o/n)")
                        if r != "o":
                            break
                    else:
                        connected = True
                        break
        except (Exception, KeyboardInterrupt) as e:
            print(e)
            pass

    voltageRatioInput0.close()


main()
