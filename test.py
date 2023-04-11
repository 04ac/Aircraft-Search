from bs4 import BeautifulSoup
import requests

html_text = requests.get("https://www.airfleets.net/recherche/?key=N747NA")
soup = BeautifulSoup(html_text, "lxml")

