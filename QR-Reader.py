import os
import re
import cv2
from os.path import exists
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

def ExtraerQRdesdeIMG(img, nombrearchivo, rutaImagen):
    listadoImagenes = []

    try:
        original = img.copy()
        listadoImagenes += Opening(rutaImagen,output_DIR + "OP_KERNEL.jpg","KERNEL")
        listadoImagenes += Closing(rutaImagen,output_DIR + "CLO_KERNEL.jpg","KERNEL")

        listadoImagenes.append(Erosion(rutaImagen,output_DIR + "ER.jpg"))
        z = 0
        r = 0

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
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 0)

            r = r + 1
            if len(approx) == 4 and area > 1000 and (ar > .80 and ar < 1.3):
                for factor in range(1, 3):
                    ROI = original[y:y + factor * h, x:x + factor * w]
                    crop_img = img[y:y + factor * h, x:x + factor * w].copy()

                    qrImage = output_DIR + nombrearchivo + str(z) + '_QR.jpg'
                    cropimage = output_DIR + nombrearchivo + str(z) + "crop.jpg"
                    qrImageErosion = output_DIR + nombrearchivo + str(z) + '_QRErosion.jpg'
                    qrImageOpening = output_DIR + nombrearchivo + str(z) + "KERNEL.jpg"
                    qrImageClosing = output_DIR + nombrearchivo + str(z) + "CLO_KERNEL.jpg"

                    cv2.imwrite(qrImage, ROI)
                    cv2.imwrite(cropimage, crop_img)

                    image_file = Image.open(qrImage)
                    image_file = image_file.convert('1')
                    image_file.save(qrImage)
                    imagenErosionada = Erosion(qrImage, qrImageErosion)
                    listadoImagenesOpen = Opening(qrImage, qrImageOpening, "KERNEL")
                    listadoImagenesClose = Closing(qrImage, qrImageClosing, "KERNEL")
                    listadoImagenes.append(qrImage)
                    listadoImagenes.append(imagenErosionada)
                    listadoImagenes.append(cropimage)
                    listadoImagenes += listadoImagenesOpen
                    listadoImagenes += listadoImagenesClose
                    z = z + 1

    except Exception as error2:
        print("Error processing IMG" + str(error2))
    return listadoImagenes


def GetQRValue(rutaimage, img):
    try:
        valor = decode(Image.open(rutaimage), symbols=[ZBarSymbol.QRCODE])[0].data
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


def Erosion(rutaimagen, newFilepath):
    image = cv2.imread(rutaimagen)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    for i in range(0, 1):
        dilated = cv2.erode(gray.copy(), None, iterations=i + 1)
        cv2.imwrite(newFilepath, dilated)
    return newFilepath

def Opening(rutaimagen,newFilepath,clave):
    listado =[]
    image = cv2.imread(rutaimagen)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernelSizes = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (7, 7)]
    z=0
    for kernelSize in kernelSizes:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        nombreArchivo = newFilepath.replace(clave, clave + str(z))
        cv2.imwrite(nombreArchivo, opening)
        listado.append(nombreArchivo)
        z = z+1

    return listado


def Closing(rutaimagen, newFilepath, clave):
    listado =[]
    image = cv2.imread(rutaimagen)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernelSizes = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (7, 7)]
    z = 0
    for kernelSize in kernelSizes:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
        closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        nombreArchivo = newFilepath.replace(clave, clave + str(z))
        cv2.imwrite(nombreArchivo, closing)
        listado.append(nombreArchivo)
        z = z+1

    return listado


def ReadQR(filepath, output_DIR):
        images = []
        archivoPart = filepath.split("\\")
        nombrearchivo = archivoPart[len(archivoPart) - 1]
        valor = ""
        if(filepath.endswith(".pdf")):
            images = convert_from_path(filepath)
        if(filepath.endswith(".jpg")):
            images.append(Image.open(filepath))

        for i in range(len(images)):
                imagen = output_DIR + nombrearchivo + '_page_' + str(i) + '.jpg'
                images[i].save(imagen, 'JPEG')
                img = cv2.imread(imagen)
                valor = GetQRValue(imagen, img)
                if validarQRtext(valor):
                    print("QR found!")
                    return valor
                else:

                    listadoImagenes = ExtraerQRdesdeIMG(img, nombrearchivo, imagen)

                    for p in range(len(listadoImagenes)):
                        try:
                            img = cv2.imread(listadoImagenes[p])
                            valor = GetQRValue(listadoImagenes[p], img)

                            if valor != "":
                                print("QR found!")
                                print(valor)
                                return valor

                        except BaseException as e:
                            print(e.args[0])
                            print("NO QR ON PAGE")
                            continue

        if valor == "":
            print("ERROR:  QR not found on document")
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
    file_object = open("C:\\Users\\X\\Desktop\\QR\\LOG.txt", 'a')
    file_object.write( message + "\n")
    file_object.close()

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    input_DIR = "C:\\Users\\X\\QR\\INPUT\\"
    output_DIR = "C:\\Users\\X\\QR\\OUTPUT\\"
    files = os.listdir(input_DIR)
    input_DIR = "C:\\Users\\X\\QR\\PDFMAYO\\"
    output_DIR = "C:\\Users\\X\\QR\\IMG\\"
    files = os.listdir(input_DIR)
    positivas = 0
    negativas = 0
    corruptas = 0

    for file in files:

        print("ARCHIVO " + file)
        if validatePDF(input_DIR + file) is False:
            print("Either the file doesn't exist or it is not an image or a pdf")
            continue

        try:
            resultado = ReadQR(input_DIR + file, output_DIR)
        except BaseException as e:
            print(str(e))
            corruptas = corruptas + 1
            estado = "Corrupt file"
            logger("Archivo " + file + ": " + estado)
            continue
        if resultado != "ERROR: NO SE DETECTO QR":
            FINALDIC = resultado
            print(FINALDIC)
            if validarQRtext(resultado) == True:
                print("The QR value passed the validation")
            print("OK")
            estado = "OK"
            positivas = positivas + 1
        else:
            print("KO")
            estado = "KO"
            negativas = negativas + 1

        print("File " + file + ": " + estado)
        logger("File " + file + ": " + estado )


    print("NEG" + str(negativas) + "\n")
    print("POS" + str(positivas) + "\n")
    print("CORR" + str(corruptas) + "\n")
    print("TOTAL" + str(negativas + positivas))

