import email, smtplib, ssl
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime 
import pyodbc 


# Parsing - Database
#  "Data Source=HOTELAGENT\SQLexpress;Initial Catalog=Parsing;User ID=onlineParsingMachime;Password=12A-dd7e34%3482*dwk^hoeDif-su2112@41!1G+Gjudu#643Edf"
PconnStr = "Driver={SQL Server Native Client 11.0};Server=HOTELAGENT\SQLEXPRESS;Database=Emailer;UID=onlineParsingMachime;PWD=12A-dd7e34%3482*dwk^hoeDif-su2112@41!1G+Gjudu#643Edf"

toSend_conn = pyodbc.connect(PconnStr)
toSend_cursor = toSend_conn.cursor()
setSent_conn = pyodbc.connect(PconnStr)
setSent_cursor = setSent_conn.cursor()

toSend = True
while toSend:
    toSend_cursor.execute('''
        select top 1 id,subject,body,
            to_email,att_file_pattern,att_file_path,
            receiver_email,
            sender_email,mail_server,password,
            result,start_sent_time,end_sent_time
            from [dbo].[SendEmail] 
        where [start_sent_time] is null 
        order by id
    ''')
    toSend_rows = toSend_cursor.fetchall()
    toSend = len(toSend_rows) > 0
    for row in toSend_rows:
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = row.sender_email
        message["To"] = row.to_email
        message["Subject"] = row.subject
        #message.attach(MIMEText(row.body, "plain"))
        message.attach(MIMEText(row.body, "html"))
        if (row.att_file_path !=None and 
            row.att_file_path !=""):
            all_files = os.listdir(row.att_file_path) 
            files = [f for f in all_files if re.match(row.att_file_pattern, f)]
            for filename in files:
                with open(row.att_file_path + filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                # Encode file in ASCII characters to send by email    
                encoders.encode_base64(part)
                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                # Add attachment to message and convert message to string
                message.attach(part)
                #os.remove(row.att_file_path + filename)
        text = message.as_string()
        # Log in to server 
        print('Sending email at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
        setSent_cursor.execute('''
            update [dbo].[SendEmail] 
            set start_sent_time = CURRENT_TIMESTAMP
            where id = ?
        ''', row.id )
        setSent_conn.commit()
        result="ok"
        with smtplib.SMTP(row.mail_server) as server:
            try:
                #server.login(row.sender_email, row.password)
                server.sendmail(row.sender_email, row.receiver_email.split(";"), text)
            except Exception as e:
                result = str(e)

        print('Finished at '+ datetime.datetime.now().strftime("%A, %d.%m.%Y %X") +'\n')
        setSent_cursor.execute('''
            update [dbo].[SendEmail] 
            set end_sent_time = CURRENT_TIMESTAMP, result = ?
            where id = ?
        ''', result, row.id )
        setSent_conn.commit()








