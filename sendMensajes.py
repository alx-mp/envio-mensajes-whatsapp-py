import flet as ft
import pywhatkit as kit
import time
import threading

# Global stop flag
stop_flag = False

# Function to send messages
def enviar_mensajes(custom_message, image_path):
    global stop_flag
    with open('phone_numbers.txt', 'r') as file:
        content = file.read()
    
    phone_numbers = [num.strip() for num in content.split(',') if num.strip() != '']
    for number in phone_numbers:
        if stop_flag:
            print("Envío de mensajes detenido.")
            break
        try:
            print(f"Enviando mensaje a {number}...")
            kit.sendwhats_image(number, image_path, custom_message, 13, tab_close=True, close_time=5)
            print(f"Mensaje enviado a {number}. Haciendo clic en el sitio para enviar...")
            time.sleep(5)
        except Exception as e:
            print(f"Error al enviar mensaje a {number}: {e}")
    print("Mensajes enviados con éxito.")

def main(page: ft.Page):
    global stop_flag
    page.title = "Enviar Mensajes de WhatsApp"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.window.width = 600  # Ajustar el ancho de la ventana
    page.window.height = 400  # Ajustar la altura de la ventana

    def seleccionar_imagen(e: ft.FilePickerResultEvent):
        if e.files:
            entry_image_path.value = e.files[0].path
            entry_image_path.update()

    pick_files_dialog = ft.FilePicker(on_result=seleccionar_imagen)
    page.overlay.append(pick_files_dialog)

    def enviar(e):
        custom_message = entry_message.value.strip()
        image_path = entry_image_path.value
        if custom_message and image_path:
            global stop_flag
            stop_flag = False  # Reset stop flag before starting new thread
            enviar_thread = threading.Thread(target=enviar_mensajes, args=(custom_message, image_path))
            enviar_thread.start()
            page.window.minimized = True  # Minimizar la ventana al enviar mensajes
        else:
            ft.alert("Por favor, completa ambos campos antes de enviar.")

    def window_event(e):
        if e.data == "close":
            confirm_dialog.open = True
            page.update()

    def yes_click(e):
        global stop_flag
        stop_flag = True  # Signal threads to stop
        confirm_dialog.open = False
        page.update()
        time.sleep(1)  # Give threads time to exit gracefully
        page.window.prevent_close = False
        page.window.close()

    def no_click(e):
        confirm_dialog.open = False
        page.update()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirma"),
        content=ft.Text("¿Realmente quieres salir y cerrar todos los procesos?"),
        actions=[
            ft.ElevatedButton("Sí", on_click=yes_click),
            ft.OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.window.prevent_close = True
    page.window.on_event = window_event
    page.overlay.append(confirm_dialog)

    # Create UI elements
    entry_message = ft.TextField(label="Mensaje personalizado:", multiline=True, expand=True, height=200)
    entry_image_path = ft.TextField(label="Ruta de la imagen:", width=400)
    btn_select_image = ft.ElevatedButton(text="Seleccionar Imagen", on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=False))
    btn_send = ft.ElevatedButton(text="Enviar Mensajes", on_click=enviar)

    page.add(
        entry_message,
        entry_image_path,
        btn_select_image,
        btn_send
    )

ft.app(target=main)
