import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import requests


st.title("Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API")
st.header("Шаг 1: Загрузка данных")

#Добавим интерфейс для загрузки файла с историческими данными
uploaded_file = st.file_uploader("Выберите CSV-файл", type=['csv'])
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.dataframe(data.head())
else:
    st.write("Пожалуйста, загрузите CSV-файл")

#Добавим интерфейс для выбора города
if uploaded_file is not None:
    st.header("Шаг 2: Выбор города")
    сity_list = data['city'].unique()
    сity_name = st.selectbox("Выберите город", ["Список городов"] + list(сity_list))

    if сity_name == "Список городов":
        st.warning("Выберите город из списка")

#Отобразим описательную статистику наших данных
if uploaded_file is not None:
    st.header("Шаг 3: Описательная статистика")
    if st.checkbox("Показать описательную статистику:"):
        st.write(data[data['city'] == сity_name].describe(include='all'))

    if сity_name == "Список городов":
        st.warning("Выберите город из списка, чтобы увидеть статистику")

#Добавим интерфейс для указания API Key
if uploaded_file is not None:

    st.header("Шаг 4: API key")
    api_key = st.text_input("Введите Ваш API key:")

    if not api_key:
        st.warning("API key отсутствует")
    if api_key:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": сity_name,
                  "appid": api_key,
                  "units": "metric"}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            st.write("Code: 200 OK")

            df = response.json()
            temperature = df["main"]["temp"]
            time = df["sys"]["sunrise"]
            season = pd.to_datetime(time, unit='s').month

            st.header(f"Шаг 5: Визуализация статистики по температуре для {сity_name}")
            st.write("Идет процесс отрисовки, ожидайте, пожалуйста...")
            city_data = data[data['city'] == сity_name]
            city_data['timestamp'] = pd.to_datetime(city_data['timestamp'])
            city_data.sort_values(by='timestamp', ascending=True, inplace=True)

            city_data['avg_temp'] = city_data.groupby('season')['temperature'].transform(lambda row: row.mean())
            city_data['std_temp'] = city_data.groupby('season')['temperature'].transform(lambda row: row.std())

            city_data['lower_bound'] = city_data['avg_temp'] - 2 * city_data['std_temp']
            city_data['upper_bound'] = city_data['avg_temp'] + 2 * city_data['std_temp']
            city_data['is_anomaly'] = (city_data['temperature'] > city_data['upper_bound'])|(city_data['temperature'] < city_data['lower_bound'])

            min_temp = city_data['temperature'].min()
            max_temp = city_data['temperature'].max()
            mean_temp = city_data['temperature'].mean()

            #Настройка графика
            fig, ax = plt.subplots(figsize=(16, 10))
            ax.set_facecolor('white')
            # Линия временного ряда
            sns.lineplot(data=city_data, x='timestamp', y='temperature', label='Температура', color='blue', ax=ax)

            ax.plot(city_data['timestamp'], city_data['lower_bound'], color='skyblue', linestyle='--', label='Lower bound')
            ax.plot(city_data['timestamp'], city_data['upper_bound'], color='red', linestyle='--', label='Upper bound')

            #Настройка для аномальных точек
            sns.scatterplot(data=city_data[city_data['is_anomaly']],
                            x='timestamp',
                            y='temperature',
                            color='red',
                            label='Аномалии',
                            ax=ax)

            # Отображение минимум, максимум и среднее
            ax.axhline(y=min_temp, color='green', linestyle='--', label=f'Мин. темп. ({min_temp:.1}°C)')
            ax.axhline(y=max_temp, color='orange', linestyle='--', label=f'Макс. темп. ({max_temp:.1f}°C)')
            ax.axhline(y=mean_temp, color='black', linestyle='--', label=f'Ср. темп. ({mean_temp:.1f}°C)')

            ax.set_title(f'Временной ряд с аномалиями для города {сity_name}')
            ax.set_xlabel('Дата')
            ax.set_ylabel('Температура')
            ax.legend()

            #Для корректного отображения годов на оси Дата
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

            plt.tight_layout()
            #Отображение графика в Streamlit
            st.pyplot(fig)
            #plt.show()

            city_data = city_data[city_data["timestamp"].dt.month == season]

            lower_bound = city_data.iloc[0]["lower_bound"]
            upper_bound = city_data.iloc[0]["upper_bound"]

            if lower_bound <= temperature <= upper_bound:
                st.write(f"Температура в норме")
                st.write(f"ТСтатистика:")
                st.write(f"Текущая температура: {temperature}")
                st.write(f"Нижняя граница: {lower_bound:.2f}")
                st.write(f"Верхняя температура: {upper_bound:.2f}")
                st.write(f"Минимальная температура: {min_temp:.2f}")
                st.write(f"Максимальная температура: {max_temp:.2f}")
                st.write(f"Средняя температура: {min_temp:.2f}")
            else:
                st.write(f"Температура выходит за пределы нормы")
                st.write(f"Статистика:")
                st.write(f"Текущая температура: {temperature}")
                st.write(f"Нижняя граница: {lower_bound:.2f}")
                st.write(f"Верхняя температура: {upper_bound:.2f}")
                st.write(f"Минимальная температура: {min_temp:.2f}")
                st.write(f"Максимальная температура: {max_temp:.2f}")
                st.write(f"Средняя температура: {min_temp:.2f}")
        if response.status_code == 401:
            st.warning('{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."}')




