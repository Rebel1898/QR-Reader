import os
import re
import cv2
from os.path import exists

import numpy
from PIL import Image
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path
from pyzbar.wrapper import ZBarSymbol
import warnings


def validatePDF(file):
    if file.endswith(".pdf") is True & exists(file) is True:
        return True
    if file.endswith(".jpg") is True & exists(file) is True:
        return True
    else:
        return False

def ExtraerQRdesdeIMG(img):
    listadoImagenes = []

    try:
        original = numpy.asarray(img.copy())
        listadoImagenes += Opening(original)
        listadoImagenes += Closing(original)

        listadoImagenes+= Erosion(original)

        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            x, y, w, h = cv2.boundingRect(approx)
            area = cv2.contourArea(c)
            ar = w / float(h)
            cv2.rectangle(original.copy(), (x, y), (x + w, y + h), (0, 0, 0), 0)
            if len(approx) == 4 and area > 1000 and (ar > .80 and ar < 1.3):
                for factor in range(1, 3):
                    ROI = original[y:y + factor * h, x:x + factor * w]
                    crop_img = original[y:y + factor * h, x:x + factor * w].copy()

                    listadoImagenes.append(ROI)
                    listadoImagenes.append(crop_img)

                    image_fileORIG = ROI.copy()

                    imagenErosionada = Erosion(image_fileORIG)
                    listadoImagenesOpen = Opening(image_fileORIG)
                    listadoImagenesClose = Closing(image_fileORIG)

                    listadoImagenes+= imagenErosionada
                    listadoImagenes+= listadoImagenesOpen
                    listadoImagenes+= listadoImagenesClose
    except Exception as error2:
        print("Error " + str(error2))
    return listadoImagenes


def GetQRValue(img):
    try:
        valor = decode(img, symbols=[ZBarSymbol.QRCODE])[0].data
    except Exception as e:
        if str(e) != "list index out of range":
            print(e)

        valor = ""

    if valor == "":
        try:
            det = cv2.QRCodeDetector(img)
            valor, pts, st_code = det.detectAndDecode(img)
            return valor
        except BaseException as e:
            return ""
    else:
        return valor


def Erosion(img):
    image = img.copy()
    arrayerosion =[]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    for i in range(0, 1):
        dilated = cv2.erode(gray.copy(), None, iterations=i + 1)
        arrayerosion.append(dilated)
    return arrayerosion

def Opening(img):
    listado =[]

    image = img.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernelSizes = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (7, 7)]
    z=0
    for kernelSize in kernelSizes:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        listado.append(opening)
        listado.append(kernel)

    return listado


def Closing(img):
    listado =[]
    image = img.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernelSizes = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (7, 7)]
    z = 0
    for kernelSize in kernelSizes:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
        closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        listado.append(closing)
        listado.append(kernel)
    return listado


def ReadQR(filepath):
        images = []
        archivoPart = filepath.split("\\")
        valor = ""
        if(filepath.endswith(".pdf")):
            images = convert_from_path(filepath)
        if(filepath.endswith(".jpg")):
            images.append(Image.open(filepath))

        for i in range(len(images)):
                valor = GetQRValue(images[i])
                if validarQRtext(valor):
                    return valor
                else:

                    listadoImagenes = ExtraerQRdesdeIMG(images[i])

                    for p in range(len(listadoImagenes)):
                        try:
                            valor = GetQRValue(listadoImagenes[p])

                            if valor != "":
                                print(valor)
                                return valor

                        except BaseException as e:
                            print(e.args[0])
                            continue

        if valor == "":
            print("ERROR: NO QR Detected in full document")
            return "ERROR: NO SE DETECTO QR"
        else:
            print(valor)
            return valor

def validarQRtext(QRtext):
    validation = False
    pattern = "\*{1,}[B,C,D,E,F,G,H,N,O,Q,R]+:"
    if re.search(pattern, str(QRtext)):
        validation = True
    return validation

def logger(message):
    file_object = open("C:\\Users\\X\\LOG.txt", 'a')
    file_object.write( message + "\n")
    file_object.close()

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    input_DIR = "C:\\Users\\X\\"
    output_DIR = "C:\\Users\\X\\"
    files = os.listdir(input_DIR)
    positivas = 0
    negativas = 0
    corruptas = 0

    for file in files:

        print("File " + file)
        if validatePDF(input_DIR + file) is False:
            print("File not validated")
            continue

        try:
            resultado = ReadQR(input_DIR + file)
        except BaseException as e:
            print(str(e))
            corruptas = corruptas + 1
            estado = "corrupto"
            logger("File " + file + ": " + estado)
            continue
        if resultado != "ERROR: NO SE DETECTO QR":
            print(resultado)
            print("OK")
            estado = "OK"
            positivas = positivas + 1
        else:
            print("KO")
            estado = "KO"
            negativas = negativas + 1

        logger("File " + file + ": " + estado )


    print("NEG" + str(negativas) + "\n")
    print("POS" + str(positivas) + "\n")
    print("CORR" + str(corruptas) + "\n")
    print("TOTAL" + str(negativas + positivas))

