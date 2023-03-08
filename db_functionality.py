import psycopg2
from psycopg2 import Error

def push_todb(creds):
    conn = psycopg2.connect(user="postgres",
                              password="qwerty",
                              host="127.0.0.1",
                              port="5432",
                              database="postgres")
   
    # create a cursor object to execute queries
    cur = conn.cursor()
    cur.execute("INSERT INTO quiz (id, name, surname, phone, score, pass) VALUES (%s, %s, %s, %s, %s, %s)"
                ,(creds.nickname,
                 creds.name,
                 creds.surname,
                 creds.phone,
                 creds.score,
                 creds.score > 4))
    conn.commit()
    cur.close()
    conn.close()
