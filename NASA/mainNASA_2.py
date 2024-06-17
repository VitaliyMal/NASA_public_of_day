import requests
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
from tkinter import messagebox
from googletrans import Translator
import os
from tkinter import filedialog
import json


translator = Translator()

api_key = "YOU_API_KEY"
url = "https://api.nasa.gov/planetary/apod"
img = None  # Глобальная переменная для изображения

def get_apod_image():
    global img  # Объявляем img как глобальную переменную
    date = entry_date.get()
    params = {"api_key": api_key, "date": date}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if "url" in data:
            image_url = data["url"]
            explanation = data["explanation"]

            # Перевод объяснения на русский
            translation = translator.translate(explanation, dest='ru')
            explanation_ru = translation.text

            image_data = requests.get(image_url).content
            img = Image.open(BytesIO(image_data))
            img = img.resize((800, 800))

            photo = ImageTk.PhotoImage(img)

            label.config(image=photo)
            label.image = photo

            text_explanation.delete(1.0, tk.END)  # Очистить текстовый блок перед добавлением нового текста
            text_explanation.insert(tk.END, f"Объяснение: {explanation_ru}")

            button_save.config(state=tk.NORMAL)  # Включаем кнопки "Сохранить" и "Загрузить"
            button_load.config(state=tk.NORMAL)

        else:
            print("Не удалось получить информацию о картинке дня.")
    else:
        print("Ошибка при выполнении запроса:", response.status_code)

def save_data():
    global img  # Объявляем img как глобальную переменную
    save_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "saves")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    date = entry_date.get()

    image_path = os.path.join(save_dir, f"apod_{date}.jpg")
    img.save(image_path)

    text_path = os.path.join(save_dir, f"apod_{date}.txt")
    with open(text_path, "w", encoding="utf-8") as file:
        file.write(text_explanation.get(1.0, tk.END))

    json_data = {
        "image_path": image_path,
        "text_path": text_path
    }

    json_path = os.path.join(save_dir, f"apod_{date}.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file)

    #print("Данные сохранены.")
    #showinfo(title="Информация", message="Успешно сохранено")
    messagebox.showinfo("Сохранение", "Данные успешно сохранены.")

def load_data():
    file_type = filedialog.askopenfilename(initialdir=os.path.join(os.path.dirname(os.path.realpath(__file__)), "saves"),
                                           title="Выберите файл для загрузки",
                                           filetypes=(("JSON файлы", "*.json"),))

    if file_type:
        with open(file_type, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            image_path = data["image_path"]
            text_path = data["text_path"]

            img = Image.open(image_path)
            photo = ImageTk.PhotoImage(img)

            label.config(image=photo)
            label.image = photo

            with open(text_path, "r", encoding="utf-8") as text_file:
                loaded_text = text_file.read()
                text_explanation.delete(1.0, tk.END)
                text_explanation.insert(tk.END, loaded_text)

root = tk.Tk()
root.title("NASA Image of the Day // Dev Maltsev with AI")

button_save = tk.Button(root, text="Сохранить", command=save_data, state=tk.DISABLED)
button_save.pack(side=tk.LEFT)

button_load = tk.Button(root, text="Загрузить", command=load_data, state=tk.DISABLED)
button_load.pack(side=tk.LEFT)

label_date = tk.Label(root, text="Введите дату (гггг-мм-дд):")
label_date.pack(side=tk.LEFT)

entry_date = tk.Entry(root)
entry_date.pack(side=tk.LEFT)

button = tk.Button(root, text="Получить картинку дня", command=get_apod_image)
button.pack(side=tk.LEFT)

label = tk.Label(root)
label.pack()

text_explanation = tk.Text(root, wrap=tk.WORD, height=15, width=100)
text_explanation.pack()

scrollbar = tk.Scrollbar(root, command=text_explanation.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_explanation.config(yscrollcommand=scrollbar.set)

root.mainloop()