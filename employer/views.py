from django.shortcuts import render
import mysql.connector
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

# Create your views here.

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='34679o',
    database='derrotewaschbaer',
    autocommit=True
)

cursor = db.cursor(buffered=True)


@api_view(['GET'])
def get_all_employers(request):
    global cursor
    cursor.execute('SELECT * FROM employer;')
    data = {'all_employers_list': cursor.fetchall()}
    return Response(data, status=200)



def new_employer(request, name: str = "Name", surname: str = "Surname") -> HttpResponse:
    """
    If you don`t have a surname - input 'NULL'

    Returns an id of new row
    """
    global cursor
    cursor.execute(f'INSERT INTO employer (name, surname) VALUES ("{name}", "{surname}");')
    cursor.execute('SELECT * FROM employer;')
    # context = {'row_id': cursor.fetchall()[-1][0]}
    return HttpResponse(f"{cursor.fetchall()[-1][0]}")


# new_employer('"I DID IT"')
cursor.execute('SELECT * FROM employer')
print(cursor.fetchall()[-1])
# for i in cursor:
#     print(i.__class__)
#     print('---')

