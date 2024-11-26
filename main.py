# Импорты библиотек
import os
import math
import tkinter as tk
from tkinter import filedialog
import gpxpy
import gpxpy.gpx
from geopy.distance import geodesic
import matplotlib.pyplot as plt
# Функция для выбора файла через tkinter
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("GPX files", "*.gpx")])
    return file_path
# Функции для расчетов расстояния
def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3  # Радиус Земли в метрах
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def great_circle_distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # Радиус Земли в метрах
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    return R * math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(delta_lambda))

# Обработка GPX файла
file_path = select_file()
if not file_path or not os.path.exists(file_path):
    print("Файл не выбран или не существует!")
else:
    with open(file_path, 'r', encoding='utf-8') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
