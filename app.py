from flask import Flask, render_template, request
import requests
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configura los detalles del servidor SMTP de Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'matiasaburto653@gmail.com'
SMTP_PASSWORD = 'icaw srlx nonu tahr'

# URL del sitio web a verificar y texto específico a buscar
website_url = "https://catalogo.movistar.cl/tienda/outlet/celulares-reacondicionados?marca=847"
text_to_find = "iPhone 14"

app = Flask(__name__)

# Función para enviar un correo electrónico
def send_email(subject, body):

    body += f"\nTexto buscado: {text_to_find}"

    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = 'maburto@inech.cl'
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(SMTP_USERNAME, 'maburto@inech.cl', msg.as_string())
    server.quit()

# Función para realizar un ping al sitio web y buscar el texto en el front-end
def check_website():
    try:
        response = requests.get(website_url)
        if response.status_code == 200:
            if text_to_find in response.text:
                ping_result = "Sitio web en línea y texto encontrado"
                send_email("Texto encontrado", "El texto específico se encontró en el sitio web.")
            else:
                ping_result = "Sitio web en línea pero texto no encontrado"
        else:
            ping_result = "Error: Código de estado HTTP no válido"
    except Exception as e:
        ping_result = f"Error: {str(e)}"
    
    if "texto no encontrado" in ping_result:
        send_email("Texto no encontrado", "El texto específico no se encontró en el sitio web.")

    print(ping_result)

# Ruta para enviar un correo de prueba
@app.route('/test_email')
def test_email():
    subject = "Prueba de correo electrónico"
    body = "Este es un correo de prueba enviado desde tu aplicación Flask."
    send_email(subject, body)
    return "Correo de prueba enviado"

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        website = request.form['website']
        try:
            response = requests.get(website)
            if response.status_code == 200:
                ping_result = "Sitio web en línea"
            else:
                ping_result = "Error: Código de estado HTTP no válido"
        except Exception as e:
            ping_result = f"Error: {str(e)}"
        return render_template('index.html', ping_result=ping_result)
    return render_template('index.html')

if __name__ == '__main__':
    # Programa el ping cada 1 minuto
    schedule.every(5).minutes.do(check_website)
    
    # Ejecuta el planificador de tareas en segundo plano
    while True:
        schedule.run_pending()
        time.sleep(1)
