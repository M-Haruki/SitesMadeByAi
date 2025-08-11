import pymysql.cursors


def get_db_connection():
    return pymysql.connect(
        host="localhost",
        port=63306,
        user="sites_made_by_ai",
        password="2wcypnINRh]51)Q!",
        db="sites_made_by_ai",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def create_session(session_id: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # セッションの作成クエリを実行
            sql = "insert into sessions (session_id) values (%s)"
            cursor.execute(sql, (session_id,))
            connection.commit()
            return
    finally:
        connection.close()


def check_session(session_id: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # セッションの存在確認クエリを実行
            sql = "select count from sessions where session_id = %s"
            cursor.execute(sql, (session_id,))
            result = cursor.fetchone()
            if result and result["count"] < 100:  # 利用回数の制限を確認
                return True
            return False
    finally:
        connection.close()


def increment_session_count(session_id: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # セッションの利用回数をインクリメントするクエリを実行
            sql = "update sessions set count = count + 1 where session_id = %s"
            cursor.execute(sql, (session_id,))
            connection.commit()
    finally:
        connection.close()


def register_history(
    role: str,
    content: str,
    session_id: str,
):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # ヒストリーの登録クエリを実行
            sql = "insert into historys (role ,content, session_id) values (%s, %s, %s)"
            cursor.execute(sql, (role, content, session_id))
            connection.commit()
    finally:
        connection.close()


def get_history(session_id: str):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # セッションに紐づくヒストリーを取得するクエリを実行
            sql = "select role, content from historys where session_id = %s order by id"
            cursor.execute(sql, (session_id,))
            result = cursor.fetchall()
            return result
    finally:
        connection.close()
