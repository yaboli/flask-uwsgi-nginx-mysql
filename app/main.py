from flask import Flask, request, jsonify
import logging
import pymysql
import uuid
import configparser


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def get_connect():
    cf = configparser.ConfigParser()
    cf.read("config/mysql.ini")

    database = cf.get("app_info", "DATABASE")
    user = cf.get("app_info", "USER")
    password = cf.get("app_info", "PASSWORD")
    host = cf.get("app_info", "HOST")
    port = int(cf.get("app_info", "PORT"))

    conn = pymysql.connect(host=host,
                           user=user,
                           passwd=password,
                           db=database,
                           port=port,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    return conn


@app.route("/")
def hello():
    return "<h1 style='color:blue'>'Hello World!' from 'Flask + uWSGI + Nginx + MySQL'</h1>"


@app.route("/insert", methods=['POST'])
def insert():
    request_json = request.json
    username = request_json['username']
    password = request_json['password']
    user_type = 'DEV'
    user_id = str(uuid.uuid1())

    sql = "INSERT INTO `user` (`user_id`, `user_type`, `username`, `password`)" \
          "VALUES (%s, %s, %s, %s)"
    conn = get_connect()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, (user_id, user_type, username, password))
        conn.commit()
    except pymysql.Error as e:
        conn.rollback()
        return jsonify(error=e), 500
    finally:
        conn.close()
        return 'Data inserted successfully', 200


@app.route("/query", methods=['POST'])
def query():
    global result
    request_json = request.json
    username = request_json['username']
    password = request_json['password']
    conn = get_connect()
    try:
        with conn.cursor() as cursor:
            # Read a single record
            sql = "SELECT `id`, `user_id` FROM `user` " \
                  "WHERE `username`=%s AND `password`=%s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchall()
    except pymysql.Error as e:
        conn.rollback()
        return jsonify(error=e), 500
    finally:
        conn.close()
        return jsonify(result=result), 200


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
