from flask import Flask, render_template, request
import pandas as pd
import sqlite3

app = Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/List')
def list_view():
    #データベースを読み込む
    db = sqlite3.connect('kofuku.db')
        
    df = pd.read_sql_query("SELECT * FROM dictionary", db)

    results = df.to_dict('records')
    
    db.close()
    
    if len(results) > 0:
        # 検索結果がある場合はそれを表示
        return render_template('list.html', results=results)
    else:
        return "データがありません"

@app.route('/Contact')
def Contact_view():
    return render_template('contact.html')

@app.route('/Management_add')
def Management_view():
    return render_template('Login.html')

@app.route('/search', methods=['POST'])
def search():
    # フォームから入力された単語を取得
    word = request.form['word']
    
    #データベースを読み込む
    db = sqlite3.connect('kofuku.db')

    df = pd.read_sql_query("SELECT * FROM dictionary", db)
    
    # 入力された単語をデータから部分一致検索し、意味を取得
    results = df[df['Word'].str.contains(word, case=False, na=False)][['Word', 'Meaning','Source']]

    db.close()
    
    if len(results) > 0:
        # 検索結果がある場合はそれを表示
        return render_template('index.html', results=results.to_dict('records'), word=word)
    else:
        # 検索結果がない場合はエラーメッセージを表示
        error_message = 'この用語は登録されていません: ' + word
        return render_template('index.html', error=error_message)
    

@app.route('/login', methods=['POSt'])
def login():
    # フォームから入力された単語を取得
    username = request.form['username']
    password = request.form['password']

    if username == "kazuki" and password == "kazu0923":
        #パスワードが一致した場合画面を表示
        return render_template('Management.html')
    else:
        #一致しない場合エラーメッセージを表示
        error_user = "miss"
        return render_template('Login.html', error=error_user)

@app.route("/Add", methods=["post"])
def Add():
    #フォームから入力された情報を取得
    new_word = request.form['Word_add']
    new_meaning = request.form['Meaning_add']
    new_source = request.form['Source_add']

    #データベースを読み込む
    db = sqlite3.connect('kofuku.db')

    cur = db.cursor()

    #SQL文
    sql = 'INSERT INTO dictionary (Word, Meaning, Source) VALUES (?, ?, ?)'

    #データの定義
    # word_data = new_word
    # meaning_data = new_meaning
    # source_data = new_source
    # data =[(word_data, meaning_data, source_data)]
    data =[(new_word, new_meaning, new_source)]

    #データの挿入
    cur.executemany(sql, data)
    # cur.execute('ALTER TABLE users RENAME TO dictionary')

    db.commit()

    cur.close()
    db.close()

    return render_template('Management.html')

@app.route("/Delete", methods=["post"])
def Delete():
    #フォームから入力された情報を取得
    Delete_ID = request.form['ID_delete']
    Delete_word = request.form['Word_delete']

    #データベースを読み込む
    db = sqlite3.connect('kofuku.db')

    cur = db.cursor()

    #複数条件を指定してレコードを削除
    cur.execute('DELETE FROM dictionary where ID= ? and Word= ? ',(Delete_ID, Delete_word))

    db.commit()

    cur.close()
    db.close()

    return render_template('Management.html')

@app.route("/Update", methods=["post"])
def Update():
    #フォームから現在のIDとWord情報を取得
    Original_ID = request.form['ID_original']
    Original_word = request.form['Word_original']
    #フォームから更新するフィールドと新しい値を取得
    field = request.form['field']
    new_value = request.form['new_value']
    
    #データベースを読み込む
    db = sqlite3.connect('kofuku.db')
    cur = db.cursor()
    
    try:
        #複数条件を指定してレコードを更新
        sql = f'UPDATE dictionary SET {field}= ? where Word= ? and id= ? '
        cur.execute(sql,(new_value, Original_word, Original_ID))
        db.commit()       
    except sqlite3.IntegrityError:
        # 一意性制約違反が発生した場合の処理
        db.rollback()
        return "更新する値が重複している可能性があります。", 400
    finally:
        #カーソルとデータベース接続を閉じる
        cur.close()
        db.close()
    
    return render_template('Management.html')



if __name__ == '__main__':
    app.run(debug=True)