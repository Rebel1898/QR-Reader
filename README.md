# QR-Reader
This script reads QR in all the pdfs and jpg in the input folder. It also checks the resulting text matches the pattern required in B2G portuguese invoices.

To increase detection rate, it processes the image (erosion,closing and opening) the images extracted from the PDF. The detection rate assesed with 1000 invoices was 97% with only 3% false negatives.


Reference: https://pyimagesearch.com/2021/04/28/opencv-morphological-operations/
