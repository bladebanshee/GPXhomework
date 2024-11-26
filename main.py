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
