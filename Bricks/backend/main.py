from dotenv import load_dotenv
from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
import hashlib
import jwt
import logging
import os
from models import db, Delete, Group, GroupMember, Mention, Notification, Problem, Project, ProjectSort, Record, SearchHistory, Tag,  TagTextBox, TextBox, User
from sqlalchemy import create_engine, text
from time import time

load_dotenv()

db_username = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')
db_name = os.environ.get('DB_NAME')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
CORS(app, resources={r"/*": {'origins': "*"}})

#連線到伺服器上的 MySQL
db_url = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_url)

app.config.from_object(__name__)
auth = HTTPTokenAuth(scheme='Bearer')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
db.init_app(app)

#hash password
def hash_password(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    return hashed_password

#verify token
@auth.verify_token
def verify_token(token):
    conn = engine.connect()
    print(jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256']))
    try:
        data = jwt.decode(token,
                          app.config['SECRET_KEY'],
                          algorithms=['HS256'])
    except:
        return False

    selectUserEmail = f"""
        SELECT user_email FROM users
        WHERE user_email = '{data['user_email']}';
    """
    ret = conn.execute(text(selectUserEmail))
    ret_list = ret.fetchall()
    if ret_list is None:
        return False
    ret = User.query.filter_by(user_email = data['user_email']).one()
    return ret.id


# hello world route
@app.route('/', methods=['GET'])
def greetings():
    return ("Hello, world!")


@app.route('/bricks', methods=['GET'])
def bricks():
    return ("Bricks專案管理實用工具讚讚!")


@app.route('/login', methods=['GET', 'POST'])
def login():
    response_object = {'status': 'success'}
    response_object['message'] = "登入成功"
    try:
        conn = engine.connect()
    except:
        response_object['status'] = "failure"
        response_object['message'] = "資料庫連線失敗"
        return jsonify(response_object)

    #取得檔案
    post_data = request.get_json()
    user_email = post_data.get("user_email")
    #對比信箱，如正確回傳 user_id
    try:
        selectUserId = f"""
            SELECT id, user_password FROM users
            WHERE user_email = "{post_data.get("user_email")}";
        """
        result = conn.execute(text(selectUserId))
        result_list = result.fetchall()
        response_object['user_id'] = result_list[0][0]
        print(123)
        ret = User.query.filter_by(user_email = user_email).one()
        user_password = ret.user_password
        print(user_password)
        if user_password != hash_password(post_data.get("user_password")):
            response_object['status'] = "failure"
            response_object['message'] = "您的密碼不正確，請再試一次"
            return jsonify(response_object)
    except IndexError:
        response_object['status'] = "failure"
        response_object['message'] = "您的帳號不正確，請再試一次"
        return jsonify(response_object)
    except:
        response_object['status'] = "failure"
        response_object['message'] = "SELECT user_id 失敗"
        return jsonify(response_object)

    token = jwt.encode(
        {
            'user_email': post_data.get("user_email"),
            'exp': int(time() + 60 * 60 * 24 * 30),
            'status': "success",
            'message': "登入成功"
        },
        app.config['SECRET_KEY'],
        algorithm='HS256')
    result.close()
    conn.close()
    return token


#註冊 --> 對比信箱及存入信箱、密碼及使用者名稱
@app.route('/register', methods=['POST'])
def register():
    response_object = {'status': 'success'}
    response_object['message'] = "信箱註冊成功"
    try:
        conn = engine.connect()
    except:
        response_object['status'] = "failure"
        response_object['message'] = "資料庫連線失敗"
        return jsonify(response_object)
    post_data = request.get_json()
    if ((post_data.get("user_email") == None) |
        (post_data.get("user_password") == None) |
        (post_data.get("user_name") == None)):
        response_object['status'] = "failure"
        response_object['message'] = "有缺失信箱、密碼和使用者名稱回傳值"
        return jsonify(response_object)
    try:
        isRegisted = f"""
            SELECT IF(SUM(IF(user_email != "{post_data.get("user_email")}", 0, 1))>0, 1, 0) AS exist FROM users;
        """
        result = conn.execute(text(isRegisted))
        result_list = result.fetchall()
        if (result_list[0][0] == 0):
            hashed_password = hash_password(post_data.get("user_password"))
            addAccount = f"""
            INSERT INTO users (user_email, user_password, user_name)
            VALUES ("{post_data.get("user_email")}", "{hashed_password}"," {post_data.get("user_name")}");
            """
            print(hashed_password)
            conn.execute(text(addAccount))
            conn.execute(text("COMMIT;"))
        else:
            response_object['status'] = "failure"
            response_object['message'] = "此信箱已被註冊過"
            return jsonify(response_object)

        selectUserId = f"""
            SELECT id FROM users
            WHERE user_email = "{post_data.get("user_email")}";
        """
        result2 = conn.execute(text(selectUserId))
        result2_list = result2.fetchall()
        response_object['user_id'] = result2_list[0][0]

    except:
        response_object['status'] = "failure"
        response_object['message'] = "SELECT user_id 失敗 或 INSERT 失敗"
        return jsonify(response_object)

    result.close()
    result2.close()
    conn.close()
    return jsonify(response_object)


#加入使用者資訊 #取出資訊如果為list 要轉字串
@app.route('/register/survey', methods=['POST'])
def register_survey():
    response_object = {'status': 'success'}
    response_object['message'] = "使用者調查註冊成功"
    try:
        conn = engine.connect()
    except:
        response_object['status'] = "failure"
        response_object['message'] = "資料庫連線失敗"
        return jsonify(response_object)
    post_data = request.get_json()
    try:
        addInfo = f"""
            UPDATE users
            SET user_purpose = "{",".join(post_data.get("user_purpose"))}", user_identity = "{(post_data.get("user_identity"))}", user_otherTool = "{",".join(post_data.get("user_otherTool"))}" 
            WHERE id = {(post_data.get("user_id"))};
        """
        conn.execute(text(addInfo))
        conn.execute(text("COMMIT;"))

        selectId = f"""
            SELECT user_email FROM users
            WHERE id = {(post_data.get("user_id"))};
        """
        result = conn.execute(text(selectId))
        response_object['user_email'] = result.fetchall()[0][0]

    except Exception as e:
        response_object['status'] = "failure"
        response_object['message'] = "INSERT userInfo 失敗"
        logging.exception('Error at %s', 'division', exc_info=e)

    conn.close()
    return jsonify(response_object)

@app.route('/project_index', methods=['POST'])
@auth.login_required
def get_project():
    conn = engine.connect()
    response_object = {"status": "success"}
    post_data = request.get_json()
    user_id = auth.current_user()
    found = False

    if post_data.get("project_status") == "normal":
        nor_query = """
                    SELECT * FROM project WHERE user_id = {} AND project_trashcan = 0 AND project_ended = 0
                    ORDER BY project_type;
                """.format(user_id)
        SQL_data = conn.execute(text(nor_query))
        keys = list(SQL_data.keys())
        data = [dict(zip(keys, row)) for row in SQL_data.fetchall()]
        conn.close()
        found = True
        response_object["items"] = data
        conn.close()

    if post_data.get("project_status") == "ended":
        end_query = """
                    SELECT * FROM project WHERE user_id = {} AND project_trashcan = 0 AND project_ended = 1
                    ORDER BY project_type;
                """.format(user_id)
        SQL_data = conn.execute(text(end_query))
        keys = list(SQL_data.keys())
        data = [dict(zip(keys, row)) for row in SQL_data.fetchall()]
        found = True
        response_object["items"] = data
        conn.close()

    if post_data.get("project_status") == "trashcan":
        trash_query = """
                    SELECT * FROM project WHERE user_id = {} AND project_trashcan = 1
                    ORDER BY project_type;
                """.format(user_id)
        SQL_data = conn.execute(text(trash_query))
        keys = list(SQL_data.keys())
        data = [dict(zip(keys, row)) for row in SQL_data.fetchall()]
        found = True
        response_object["items"] = data
        conn.close()

    if found == False:
        response_object["status"] = "failed"
        response_object["message"] = "沒找到"

    return jsonify(response_object)


@app.route('/set_project_end', methods=['POST'])
def set_end():
    response_object = {"status": "success"}
    try:
        conn = engine.connect()
        post_data = request.get_json()
        set_query = """
                        UPDATE project SET project_ended = 1 WHERE id = {};
                    """.format(post_data.get("project_id"))
        conn.execute(text(set_query))
        conn.execute(text("COMMIT;"))
        conn.close()
        response_object["message"] = "修改成功"

    except Exception as e:
        response_object["status"] = "failed"
        response_object["message"] = str(e)

    return jsonify(response_object)


@app.route('/add_project', methods=['POST'])
@auth.login_required
def add_project():
    response_object = {"status": "success"}
    try:
        conn = engine.connect()
        post_data = request.get_json()

        Inquery = """
            INSERT INTO project (project_type, project_image, project_name, project_trashcan, project_ended, project_edit, project_visible, project_comment, user_id)
            VALUES 
            ("{}", "{}", "{}", {}, {}, {}, {}, {}, {});
        """.format(post_data.get("project_type"),
                   post_data.get("project_image"),
                   post_data.get("project_name"),
                   post_data.get("project_trashcan"),
                   post_data.get("project_ended"),
                   post_data.get("project_isEdit"),
                   post_data.get("project_isVisible"),
                   post_data.get("project_isComment"),
                   auth.current_user())

        #執行SQL指令
        conn.execute(text(Inquery))
        conn.execute(text("COMMIT;"))
        #關閉連線
        conn.close()
        response_object["message"] = "新增{}成功".format(
            post_data.get("project_name"))

    except Exception as e:
        response_object["status"] = "failed"
        response_object["message"] = str(e)

    return jsonify(response_object)


@app.route('/add_type', methods=['PUT'])
def add_type():
    response_object = {"status": "success"}
    try:
        conn = engine.connect()
        post_data = request.get_json()
        set_query = """
                        UPDATE project SET project_type = '{}' WHERE id = {};
                    """.format(post_data.get("project_type"),
                               post_data.get("project_id"))
        conn.execute(text(set_query))
        conn.execute(text("COMMIT;"))
        conn.close()
        response_object["message"] = "修改成功"

    except Exception as e:
        response_object["status"] = "failed"
        response_object["message"] = str(e)

    return jsonify(response_object)


@app.route('/personal_setting', methods=['POST'])
@auth.login_required
def personal_setting():
    try:
        conn = engine.connect()
        response_object = {"status": "success"}
        post_data = request.get_json()

        nor_query = """
                        SELECT * FROM users WHERE id = {};
                    """.format(auth.current_user())
        SQL_data = conn.execute(text(nor_query))
        keys = list(SQL_data.keys())
        data = [dict(zip(keys, row)) for row in SQL_data.fetchall()]
        conn.close()
        response_object["items"] = data

    except Exception as e:
        response_object["status"] = "failed"
        response_object["message"] = str(e)


@app.route('/notification', methods=['POST'])
@auth.login_required
def notification():
    response_object = {'status': 'success'}
    try:
        conn = engine.connect()
    except:
        response_object['status'] = "connect failure"
    user_id = auth.current_user()
    try:
        notificationInfo = f"""SELECT *
        FROM notification
        JOIN mention
        ON notification.id=mention.notification_id
        WHERE mention.notification_recipient_id={user_id};"""

        result = conn.execute(text(notificationInfo))
        cols = list(result.keys())
        data = [dict(zip(cols, row)) for row in result.fetchall()]

        response_object['items'] = data
    except:
        response_object['status'] = "algorithm failure"

    result.close()
    conn.close()
    return jsonify(response_object)


@app.route('/search', methods=['POST'])
def search():

    response_object = {'status': 'success'}
    try:
        conn = engine.connect()
    except:
        response_object['status'] = "connect failure"

    global search_content
    search_content = request.get_json().get("search_content")
    S_DATA = []

    try:
        searchResult = f"""SELECT * FROM project;"""

        result = conn.execute(text(searchResult))
        cols = list(result.keys())
        data = [dict(zip(cols, row)) for row in result.fetchall()]

        for project_info in data:
            if lcs(project_info) > 0:
                S_DATA.append(project_info)

        S_DATA.sort(key=lcs, reverse=True)

        response_object['items'] = S_DATA
    except:
        response_object['status'] = "algorithm failure"

    result.close()
    conn.close()

    return jsonify(response_object)


def lcs(data):
    str1 = search_content
    str2 = data['project_name']
    str1_len = len(str1)
    str2_len = len(str2)

    dp = [[0 for x in range(str1_len + 1)] for y in range(str2_len + 1)]

    for i in range(1, str2_len + 1):
        for j in range(1, str1_len + 1):
            if (str1[j - 1] == str2[i - 1]):
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[str2_len][str1_len]


if __name__ == "__main__":
    app.run(debug=True)
