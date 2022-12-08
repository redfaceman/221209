import pymysql
from flask import Flask, render_template, request, flash, session, jsonify, redirect, url_for
import json

db = pymysql.connect(host='hjdb.cmux79u98wpg.us-east-1.rds.amazonaws.com',
                     port=3306, user='master', passwd='Abcd!234', db='hjdb', charset='utf8')
app = Flask(__name__)
app.config["SECRET_KEY"] = "asdfasdfas21341oiwejvcval1eaf"


@app.route('/')
def home():
    page_title = "HOME"
    return render_template('index.html', pageTitle=page_title)


@app.route('/login')
def login():
    page_title = "LOGIN"
    return render_template('login.html', pageTitle=page_title)


@app.route('/login', methods=['POST'])
def signin():
    db = pymysql.connect(host='hjdb.cmux79u98wpg.us-east-1.rds.amazonaws.com',
                         port=3306, user='master', passwd='Abcd!234', db='hjdb', charset='utf8')
    cursor = db.cursor()  # db 문 열기

    details = request.form
    user_id = details.getlist('login-id')[0]
    user_pw = details.getlist('login-pw')[0]
    if len(user_id) == 0 or len(user_pw) == 0:
        flash("아이디 혹은 비밀번호가 입력되지 않았습니다.")
        return render_template('login.html')
    else:
        sql = """
            SELECT unique_id,user_id, user_pawward, user_name FROM users
            where user_id = (%s)
        """
        cursor.execute(sql, user_id)
        user_in_db = cursor.fetchone()

        if user_in_db == None:
            flash("존재하지 않는 아이디입니다.")
            db.commit()  # db 저장
            db.close()  # db 문 닫기
            return render_template('login.html')
        elif int(user_pw) == user_in_db[2]:
            user_name = user_in_db[3]
            session['login_flag'] = True
            session['user_id'] = user_id
            session['_id'] = user_in_db[0]
            message = "{}님 환영합니다!".format(user_name)
            flash(message)
            db.commit()
            db.close()
            return redirect(url_for('home'))
        else:
            flash("잘못된 비밀번호를 입력하셨습니다.")
            db.commit()
            db.close()
            return render_template('login.html')


@app.route('/logout')
def logout():
    flash("로그아웃 되었습니다.")
    session['login_flag'] = False
    session['user_id'] = ""
    return redirect(url_for('home'))


@app.route('/join')
def join():
    page_title = "JOIN"
    return render_template('join.html', pageTitle=page_title)


@app.route('/join', methods=['POST'])
def signup():
    db = pymysql.connect(host='hjdb.cmux79u98wpg.us-east-1.rds.amazonaws.com',
                         port=3306, user='master', passwd='Abcd!234', db='hjdb', charset='utf8')
    cursor = db.cursor()

    details = request.form
    user_id = details.getlist('join-id')[0]
    user_pw = details.getlist('join-pw')[0]
    pw_confirm = details.getlist('join-confirm')[0]
    name = details.getlist('join-username')[0]
    email = details.getlist('join-email')[0]
    sql = """
            SELECT * FROM users
            where user_id = (%s)
    """
    cursor.execute(sql, user_id)
    id_check_result = cursor.fetchone()
    if id_check_result != None:
        db.commit()
        db.close()
        flash("이미 가입된 아이디입니다. 다른 아이디를 선택하세요.")
        return render_template('register.html')
    else:
        sql = """
            SELECT * FROM users
            where email = (%s)
        """
        cursor.execute(sql, email)
        email_check_result = cursor.fetchone()
        if email_check_result != None:
            db.commit()
            db.close()
            flash("이미 가입된 이메일 입니다.")
            return render_template('register.html')
        elif user_pw == pw_confirm:
            sql = """
                INSERT INTO
                users(
                    user_id
                    , user_pawward
                    , user_name
                    , email
                    )
                    VALUES
                    (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, user_pw, name, email))
            db.commit()
            db.close()
            flash("회원가입이 완료되었습니다.")
            return redirect(url_for('login'))
        else:
            db.commit()
            db.close()
            flash("비밀번호 확인이 일치하지 않습니다.")
            return render_template('register.html')
    # return redirect(url_for('login'))


@app.route('/users/<user_id>/edit')
def edit_profile(user_id):
    page_title = f"#{user_id} EDIT"
    return render_template('edit-profile.html', pageTitle=page_title)


@app.route('/questions')
def get_problems():
    db = pymysql.connect(host='hjdb.cmux79u98wpg.us-east-1.rds.amazonaws.com',
                         user='master', db='hjdb', password='Abcd!234', charset='utf8')
    curs = db.cursor()

    sql = """
    SELECT *
    FROM problem
    """

    curs.execute(sql)

    rows = curs.fetchall()
    json_str = json.dumps(rows, indent=4, sort_keys=True,
                          default=str, ensure_ascii=False)
    db.commit()
    db.close()
    return json_str, 200


@app.route('/questions', methods=['POST'])
def save_problems():
    db = pymysql.connect(host='hjdb.cmux79u98wpg.us-east-1.rds.amazonaws.com',
                         user='master', db='hjdb', password='Abcd!234', charset='utf8')
    curs = db.cursor()
    print(request.form)
    title = request.form.getlist('question-add-form__title')[0]
    comment = request.form.getlist('question-add-form__content')[0]
    user_unique_id = session['_id']

    sql = """insert into problem (problem_title, problem_comment, user_unique_id)
         values (%s,%s,%s)
        """
    curs.execute(sql, (title, comment, user_unique_id))

    # # # rows = curs.fetchall()

    # # # json_str = json.dumps(rows, indent=4, sort_keys=True, default=str)
    db.commit()
    db.close()
    return redirect(url_for("home"))


@app.route("/problem", methods=["DELETE"])
def delete_quest():
    db = pymysql.connect(host='hjdb.cmux79u98wpg.us-east-1.rds.amazonaws.com', user='master', password='Abcd!234', db="hjdb", port=3306)
    cursor = db.cursor()

    problem_id = request.form["problem_id"]

    sql = """DELETE from problem where problem_id = %s;"""
    # user_unique_id 대신 user_id를 가져오는 방법?
    # user_id = '$(sessionID)' 비교하는 방법?
    cursor.execute(sql, problem_id)
    db.commit()
    db.close()

    return jsonify({'msg': '댓글이 정상적으로 삭제되었습니다.'})


@app.route("/edit_problem/<int:problem_id>", methods=["GET", "PATCH"])
def edit_problem(problem_id):
    db = pymysql.connect(host='hjdb.cmux79u98wpg.us-east-1.rds.amazonaws.com', user='master', password='Abcd!234',
                         db="hjdb", port=3306)
    cursor = db.cursor()

    sql = """
        SELECT problem.problem_id, problem.problem_title, users.user_id, problem.problem_comment, problem.user_unique_id
        FROM problem
        INNER JOIN users ON problem.user_unique_id =users.unique_id;
        """
    cursor.execute(sql)
    rows = cursor.fetchall()

    json_str = json.dumps(rows, indent=4, sort_keys=True, default=str, ensure_ascii=False)

    if request.method == "PATCH":
        problem_title = request.get_json().get("problem_title")
        problem_content = request.get_json().get("problem_content")

        sql = "UPDATE problem set problem_title = %s, problem_comment = %s where problem_id = %s"

        cursor.execute(sql, (problem_content, problem_title, problem_id))
        db.commit()
        db.close()
        print("update success")

        return redirect(url_for("home"))

    return render_template('edit_problem.html')


@app.route('/questions/<quiz_id>')
def get_quiz(quiz_id):
    page_title = f"Question. {quiz_id}"
    return render_template('question.html', pageTitle=page_title)


if __name__ == '__main__':

    app.run('0.0.0.0', port=5000, debug=True)
