from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import PhidgetException
import time

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
    for i in range(num_samples):
        offset += ch.getVoltageRatio()
        time.sleep(ch.getDataInterval() / 1000.0)

    offset /= num_samples
    tared = True


def calibrateScale(ch, targetForce):
    global gain, calibrated
    num_samples = 50
    mes = 0
    for i in range(num_samples):
        mes += ch.getVoltageRatio()
        time.sleep(ch.getDataInterval() / 1000.0)
    gain = targetForce / mes
    calibrated = True


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
                print()
                gain = float(input("entrée un gain: "))
                calibrated = True
        except (Exception, KeyboardInterrupt):
            pass

    voltageRatioInput0.close()


main()
