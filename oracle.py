
import cx_Oracle
import datetime 
#OPERA =
#  (DESCRIPTION =
#    (ADDRESS_LIST =
#      (ADDRESS = (PROTOCOL = TCP)(HOST = 10.10.21.33)(PORT = 1521))
#    )
#    (CONNECT_DATA =
#      (SERVICE_NAME = OPERA)
#    )
#  )


print(datetime.date.today().strftime("%d.%m.%Y"))


cx_Oracle.init_oracle_client(lib_dir = r"C:\app\instantclient_19_19")
dsn_tns = cx_Oracle.makedsn('10.10.21.33', '1521', service_name='OPERA') # if needed, place an 'r' before any parameter in order to address special characters such as '\'.
conn = cx_Oracle.connect(user=r'OPERA', password='OPERA', dsn=dsn_tns) # if needed, place an 'r' before any parameter in order to address special characters such as '\'. For example, if your user name contains '\', you'll need to place 'r' before the user name: user=r'User Name'

c = conn.cursor()
c.execute('select resort, state from opera.resort') # use triple quotes if you want to spread your query across multiple lines
for row in c:
    print (row[0], '-', row[1]) # this only shows the first two columns. To add an additional column you'll need to add , '-', row[2], etc.
conn.close()








import xlsxwriter


# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('C:/test/demo.xlsx')
worksheet1 = workbook.add_worksheet(name="xxx")
worksheet2 = workbook.add_worksheet(name="yyy")
# Widen the first column to make the text clearer.
worksheet1.set_column('A:A', 20)


# Add a bold format to use to highlight cells.
bold1 = workbook.add_format({'bold': True})

# Write some simple text.
worksheet1.write('A1', 'Hello')

# Text with formatting.
worksheet1.write('A2', 'World', bold1)

# Write some numbers, with row/column notation.
worksheet1.write(2, 0, 123)
worksheet1.write(3, 0, 123.456)

# Add a bold format to use to highlight cells.
bold2 = workbook.add_format({'bold': True, 'font_color': 'red'})
Ibold2 = workbook.add_format({'bold': True, 'italic':True})
# Write some simple text.
worksheet2.write('A1', 'Hello')

# Text with formatting.
worksheet2.write('A2', 'World', bold1)

# Write some numbers, with row/column notation.
worksheet2.write(2, 0, 123,bold2)
worksheet2.write(3, 0, 123.456,Ibold2)



# Insert an image.
#worksheet.insert_image('B5', 'logo.png')

workbook.close()