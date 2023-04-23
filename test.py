from bs4 import BeautifulSoup
import numpy as np
import urllib
import requests
import easyocr
import cv2

img = cv2.imread('Images/Registration_test.jpg')
reader = easyocr.Reader(['en'], gpu=False)
text = reader.readtext(img, detail=0)
print(type(text[0].strip()))