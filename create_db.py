import mysql.connector # pip install mysql-connector-python

mydb = mysql.connector.connect(
                                host = "localhost",
                                user="root",
                                passwd="root",
                                database = "predicts",
                                #auth_plugin='mysql_native_password',
                                )

mycursor = mydb.cursor()

# create predicts DB
#mycursor.execute("CREATE DATABASE predicts")

mycursor.execute("SHOW DATABASES")
for db in mycursor:
    print(db)

# テーブルの初期化
#mycursor.execute("DROP TABLE IF EXISTS predict")

#mycursor.execute("DELETE * FROM predict")

# create table 
# >>> from app import db
# >>> db.create_all()

# add data to a table User
# >>> from app import db, User
# >>> db.create_all()
# >>> a = User('Marie')
# >>> db.session.add(a)
# >>> db.session.commit()
# >>> exit()

# テーブルの作成
# mycursor.execute("""CREATE TABLE predict(
#     id INT(11) AUTO_INCREMENT NOT NULL, 
# #     total_day_charge Float NOT NULL, 
#     number_customer_service_calls INT(3) NOT NULL,
#     total_eve_charge Float NOT NULL,
#     output INT(1) NOT NULL,
#     created_at DateTime NOT NULL,
#     PRIMARY KEY (id)
#     )""")

# データの追加
# mycursor.execute("""INSERT INTO predict (total_day_charge, number_customer_service_calls, total_eve_charge, output)
#     VALUES ('21.1', '1', '12.5','0')
 #    """)

# 一覧の表示
mycursor.execute("SELECT * FROM predict")
 
for row in mycursor:
    print(row)
 
 
# 保存を実行
# mydb.commit()
 
# 接続を閉じる
# mydb.close()