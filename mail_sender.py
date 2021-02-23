import mimetypes
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import smtplib
import secret_token


def prepare_msg(subject):
    msg = MIMEMultipart()
    # setup the parameters of the message
    msg['From'] = secret_token.email_from
    msg['To'] = secret_token.email_to
    msg['Subject'] = subject
    return msg


def prepare_file(filename):
    filepath = 'documents/'+filename  # Имя файла
    print(filepath)
    if os.path.isfile(filepath):  # Если файл существует
        ctype, encoding = mimetypes.guess_type(filepath)  # Определяем тип файла на основе его расширения
        if ctype is None or encoding is not None:  # Если тип файла не определяется
            ctype = 'application/octet-stream'  # Будем использовать общий тип
        maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип
        with open(filepath, 'rb') as fp:
            file = MIMEBase(maintype, subtype)  # Используем общий MIME-тип
            file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
            fp.close()
            encoders.encode_base64(file)  # Содержимое должно кодироваться как Base64
        file.add_header('Content-Disposition', 'attachment', filename=filename)  # Добавляем заголовки
        return file
    return None


def send_mail(msg):
    server = smtplib.SMTP('smtp.gmail.com: 587')  #Создаем сервер
    server.starttls()
    server.login(msg['From'], secret_token.password)  # Логинимся
    server.sendmail(msg['From'], msg['To'], msg.as_string())  # Отправляем сообщение
    server.quit()


def sendmsg(subject, file_name):
    msg = prepare_msg(subject)
    msg.attach(prepare_file(file_name))
    send_mail(msg)
    print("successfully sent email to %s:" % (msg['To']))


