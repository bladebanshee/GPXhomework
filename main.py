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

# Функция расчета расстояния методом большого круга
def great_circle_distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # Радиус Земли в метрах
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Функция расчета расстояния по формуле гаверсинуса
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371e3  # Радиус Земли в метрах
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))

# Функция для учета высоты
def calculate_distance_with_elevation(lat1, lon1, ele1, lat2, lon2, ele2, method):
    if method == geodesic:
        flat_distance = method((lat1, lon1), (lat2, lon2)).meters
    else:
        flat_distance = method(lat1, lon1, lat2, lon2)
    elevation_difference = abs(ele2 - ele1)
    return math.sqrt(flat_distance ** 2 + elevation_difference ** 2)

# Основная функция обработки GPX-файла
def process_gpx(file_path):
    with open(file_path, 'r', encoding='utf-8') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    total_distance_geodesic = 0
    total_distance_great_circle = 0
    total_distance_haversine = 0
    total_elevation_gain = 0
    total_elevation_loss = 0
    times = []
    speeds = []

    points = []
    elevations = []

    # Сбор данных из треков
    for track in gpx.tracks:
        for segment in track.segments:
            previous_point = None
            for point in segment.points:
                if previous_point:
                    # Расчет расстояний
                    total_distance_geodesic += calculate_distance_with_elevation(
                        previous_point.latitude, previous_point.longitude, previous_point.elevation or 0,
                        point.latitude, point.longitude, point.elevation or 0, geodesic
                    )
                    total_distance_great_circle += calculate_distance_with_elevation(
                        previous_point.latitude, previous_point.longitude, previous_point.elevation or 0,
                        point.latitude, point.longitude, point.elevation or 0, great_circle_distance
                    )
                    total_distance_haversine += calculate_distance_with_elevation(
                        previous_point.latitude, previous_point.longitude, previous_point.elevation or 0,
                        point.latitude, point.longitude, point.elevation or 0, haversine_distance
                    )

                    # Учет перепадов высоты
                    elevation_diff = (point.elevation or 0) - (previous_point.elevation or 0)
                    if elevation_diff > 0:
                        total_elevation_gain += elevation_diff
                    else:
                        total_elevation_loss -= elevation_diff

                    # Учет времени
                    if previous_point.time and point.time:
                        time_diff = (point.time - previous_point.time).total_seconds()
                        if time_diff > 0:
                            speed = geodesic((previous_point.latitude, previous_point.longitude),
                                             (point.latitude, point.longitude)).meters / time_diff
                            speeds.append(speed)
                            times.append(time_diff)

                previous_point = point
                points.append((point.latitude, point.longitude))
                elevations.append(point.elevation or 0)
                # Вывод результатов
    print(f"Файл: {file_path}")
    print(f"Общее расстояние (геодезическое): {total_distance_geodesic:.2f} м")
    print(f"Общее расстояние (большой круг): {total_distance_great_circle:.2f} м")
    print(f"Общее расстояние (гаверсинус): {total_distance_haversine:.2f} м")
    print(f"Общий подъем: {total_elevation_gain:.2f} м")
    print(f"Общий спуск: {total_elevation_loss:.2f} м")

    if times:
        total_time = sum(times)
        average_speed = sum(speeds) / len(speeds)
        print(f"Общее время: {total_time:.2f} сек")
        print(f"Средняя скорость: {average_speed:.2f} м/с")
        print(f"Максимальная скорость: {max(speeds):.2f} м/с")
        print(f"Минимальная скорость: {min(speeds):.2f} м/с")

    # Построение графиков
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot([p[1] for p in points], [p[0] for p in points], label="Маршрут")
    plt.xlabel("Долгота")
    plt.ylabel("Широта")
    plt.title("Карта маршрута")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(range(len(elevations)), elevations, label="Высота")
    plt.xlabel("Точка")
    plt.ylabel("Высота (м)")
    plt.title("Профиль высоты")
    plt.legend()

    plt.tight_layout()
    plt.show()

# Основной запуск
if __name__ == "__main__":
    file_path = select_file()
    if file_path:
        process_gpx(file_path)
    else:
        print("Файл не выбран.")
