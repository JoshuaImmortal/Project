from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random, string


app = Flask(__name__)
mysql = MySQL(app)
app.config['MySQL_HOST'] = 'localhost'
app.config['MySQL_USER'] = 'root'
app.config['MySQL_PASSWORD'] = ''
app.config['MySQL_DB'] = 'Notes'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] =   False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/Create', methods=['POST'])
def database():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""CREATE DATABASE `Notes`""")
        mysql.connection.commit()
        return("Database Created")
    except Exception as E:
         return(f"An error occured: {str(E)}", 500)

@app.route('/Create/table', methods=["POST"])
def table():
    try:
        create = mysql.connection.cursor()
        create.execute("""USE `Notes`""")
        create.execute("""CREATE TABLE IF NOT EXISTS `Create_note`(
                    `ID` INT PRIMARY KEY AUTO_INCREMENT,
                    `Note_Title` VARCHAR(100) NOT NULL,
                    `Note_Content` LONGTEXT NOT NULL,
                    `Author` VARCHAR(50) NOT NULL,
                    `Email` VARCHAR(50) NOT NULL,
                    `Date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP); 
                    """)
        mysql.connection.commit()
        create.execute("""CREATE TABLE IF NOT EXISTS `Email_DB`(
                    `Email` VARCHAR(50) NOT NULL,
                    `Token` VARCHAR(10));""")
        mysql.connection.commit()
        return("Table Created")
    except Exception as E:
         return(f"An error occured: {str(E)}", 500)
    

@app.route('/emailer/table', methods=['POST'])
def emailer(): 
    try: 
        Token_set = string.ascii_letters + string.digits
        Random_Token = random.sample(Token_set, 5)
        Token = ''.join(Random_Token)
        email = request.json['email']
        Insert = mysql.connection.cursor()
        Insert.execute("""USE `Notes`""")
        Insert.execute("""INSERT INTO `Email_DB` VALUES (%s, %s)""",(email, Token))
        mysql.connection.commit()
        Token_Msg = Message(
            'Verification Token',
            sender = 'restated.immortal@gmail.com',
            recipients = [email]
            )
        Token_Msg.body = Token
        mail.send(Token_Msg)
        return 'Sent'
    except Exception as E:
         return(f"An error occured: {str(E)}", 500)

@app.route('/verify', methods=['GET'])
def verify():
    try:
        email = request.json['email']
        Inputted_Token = request.json['Token']
        Insert = mysql.connection.cursor()
        Insert.execute("""USE `Notes`""")
        Insert.execute("""SELECT `Token` FROM `Email_DB` WHERE `Email` = %s""",(email,))
        Row = Insert.fetchone()
        if Inputted_Token == Row[0]:
            return("You have been registered")
        else:
            Insert.execute("""DELETE FROM `Email_DB` WHERE `Email` = %s""",(email,))
            mysql.connection.commit()
            return("You have not registered yet")
    except Exception as E:
         return(f"An error occured: {str(E)}", 500)
     
@app.route('/Create/note', methods=["POST"])
def create_note():
    try:
        Insert = mysql.connection.cursor()
        Insert.execute("""USE `Notes`""")
        email = request.json['email']
        id = request.json['id']
        note_title = request.json['note_title']
        note_content = request.json['note_content']
        author = request.json['author']
        Insert.execute("""INSERT INTO `Create_note` VALUES (%s, %s, %s, %s, %s, now())""",
                    (id, note_title, note_content, author, email,))
        mysql.connection.commit()
        Insert.execute("""SELECT * FROM `Create_note` WHERE author = %s""",(author,))
        Result = Insert.fetchall()
        return jsonify(Result[0])
    except Exception as E:
         return(f"An error occured: {str(E)}", 500)   

@app.route('/Access/note', methods=["GET"])
def access_note():
        try:
            Access = mysql.connection.cursor()
            Access.execute("""USE `Notes`""")
            author = request.json['author']
            Access.execute("""SELECT * FROM `Create_note` WHERE author = %s""",(author,))
            feedback = Access.fetchall()                                                                                                                                                                                                                                             
            return jsonify(feedback[0])
        except Exception as E:
         return(f"An error occured: {str(E)}", 500)

@app.route('/Update/note_title', methods=["PUT"])   
def update_note_title():
        try:
            Insert = mysql.connection.cursor()
            Insert.execute("""USE `Notes`""")
            author = request.json['author']
            note_title = request.json['note_title']    
            Insert.execute("""UPDATE `Create_note` SET Note_Title = %s WHERE Author = %s""",(note_title, author,))
            mysql.connection.commit()
            return jsonify(author, note_title)
        except Exception as E:
         return(f"An error occured: {str(E)}", 500)

@app.route('/Update/note_content', methods=["PUT"])   
def update_note_content():
        try:
            Insert = mysql.connection.cursor()
            Insert.execute("""USE `Notes`""")
            author = request.json['author']
            note_content = request.json['note_content']    
            Insert.execute("""UPDATE `Create_note` SET Note_Content = %s WHERE Author = %s""",(note_content, author))
            mysql.connection.commit()
            return jsonify(author, note_content)
        except Exception as E:
         return(f"An error occured: {str(E)}", 500)


@app.route('/Delete/note', methods=["DELETE"])
def delete_note():
        try:
            Insert = mysql.connection.cursor()
            Insert.execute("""USE `Notes`""")
            author = request.json['author']
            Delete_query = """DELETE FROM `Create_note` WHERE Author = %s"""
            Insert.execute(Delete_query, (author,))
            mysql.connection.commit()
            return "Successful"
        except Exception as E:
         return(f"An error occured: {str(E)}", 500)
   
if(__name__=='__main__'):
    app.run(debug=True)