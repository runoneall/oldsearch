import random
import string
from flask import *
import API
import Sqlite
app = Flask(__name__)

try:
    with open('database.sqlite', 'rb') as database:
        database.close()
except:
    with open('database.sqlite', 'wb') as database:
        database.close()
cursor = Sqlite.Database('database.sqlite')
try:
    cursor.find("SELECT * FROM Users LIMIT 1;")
except:
    cursor.exec('''
    CREATE TABLE "Users" (
        "id" INTEGER PRIMARY KEY AUTOINCREMENT,
        "User" TEXT NULL,
        "Pwd" TEXT NULL,
        "Key" TEXT NULL,
        "Allow" INTEGER NULL
    );
    ''')

def generate_random_key(length):
    all_chars = string.ascii_letters + string.digits + string.punctuation
    random_key = ''.join(random.choice(all_chars) for _ in range(length))
    return random_key

@app.route('/')
def hello():
    user_agent = request.headers.get('User-Agent')
    if 'Mobile' in user_agent:
        return render_template('m_index.html')
    return render_template('index.html')

@app.route('/logo')
def logo():
    return send_file('./templates/Logo.png', mimetype='image/png')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_input = request.form['search_input']
        return redirect(f'/search?query={search_input}')
    if request.method == 'GET':
        if request.args or request.args.get('query') != None:
            query = request.args['query']
            info_dict = API.Get(query=query)
            user_agent = request.headers.get('User-Agent')
            if 'Mobile' in user_agent:
                return render_template(
                    'm_search.html', 
                    target_search=query, 
                    info_dict=info_dict, 
                    info_dict_keys=list(info_dict.keys()),
                )
            return render_template(
                'search.html', 
                target_search=query, 
                info_dict=info_dict, 
                info_dict_keys=list(info_dict.keys()),
            )
        else:
            return "参数错误"
        
@app.route('/api', methods=['GET', 'POST'])
def api():
    if request.method == 'GET':
        user_agent = request.headers.get('User-Agent')
        if 'Mobile' in user_agent:
            return render_template('m_GetApi.html')
        return render_template('GetApi.html')
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            rep_data = {
                'state': 'Error', 
                'info': 'Invalid Content Type'
            }
            response = make_response(json.dumps(rep_data))
            response.headers['Content-Type'] = 'application/json'
            return response
        req_data = json.loads(request.data.decode('utf-8'))
        if 'search' not in req_data or 'user' not in req_data or 'key' not in req_data:
            rep_data = {
                'state': 'Error', 
                'info': 'Invalid Parameter'
            }
            response = make_response(json.dumps(rep_data))
            response.headers['Content-Type'] = 'application/json'
            return response
        query = req_data['search']
        user = req_data['user']
        auth_key = req_data['key']
        if not isinstance(query, str) or not isinstance(user, str) or not isinstance(auth_key, str):
            rep_data = {
                'state': 'Error', 
                'info': 'Invalid Type'
            }
            response = make_response(json.dumps(rep_data))
            response.headers['Content-Type'] = 'application/json'
            return response
        cursor = Sqlite.Database('database.sqlite')
        user_info = cursor.find(f"SELECT * FROM Users WHERE User = '{user}';")
        if user_info == None:
            rep_data = {
                'state': 'Error', 
                'info': 'Unknow User'
            }
            response = make_response(json.dumps(rep_data))
            response.headers['Content-Type'] = 'application/json'
            return response
        if user_info['Allow'] != 1:
            rep_data = {
                'state': 'Error', 
                'info': 'Not Allowed User'
            }
            response = make_response(json.dumps(rep_data))
            response.headers['Content-Type'] = 'application/json'
            return response
        if user_info['Key'] != auth_key:
            rep_data = {
                'state': 'Error', 
                'info': 'Auth Failed'
            }
            response = make_response(json.dumps(rep_data))
            response.headers['Content-Type'] = 'application/json'
            return response
        info_dict = API.Get(query=query)
        response = make_response(json.dumps(info_dict))
        response.headers['Content-Type'] = 'application/json'
        return response
    
@app.route('/api-user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if request.cookies.get('is_login'):
            return redirect('/api-user/panel')
        return render_template('api_login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cursor = Sqlite.Database('database.sqlite')
        user_info = cursor.find(f"SELECT * FROM Users WHERE User = '{username}';")
        if user_info == None:
            return redirect('/api-user/login')
        if user_info['Pwd'] == password:
            rep = make_response(render_template('login_success.html'))
            rep.set_cookie("is_login", "1")
            rep.set_cookie("username", username)
            return rep
        return redirect('/api-user/login')

@app.route('/api-user/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        if request.cookies.get('is_login'):
            return redirect('/api-user/panel')
        return render_template('api_signin.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        retype_password = request.form.get('retype_password')
        if password != retype_password:
            return redirect('/api-user/signin')
        cursor = Sqlite.Database('database.sqlite')
        if cursor.find(f"SELECT * FROM Users WHERE User = '{username}';") != None:
            return redirect('/api-user/signin')
        key = generate_random_key(15)
        cursor.exec(f"INSERT INTO Users (User, Pwd, Key, Allow) VALUES ('{username}', '{password}', '{key}', 1);")
        return render_template('signin_success.html')
    
@app.route('/api-user/panel', methods=['GET'])
def panel():
    if request.cookies.get('is_login'):
        username = request.cookies.get('username')
        cursor = Sqlite.Database('database.sqlite')
        user_info = cursor.find(f"SELECT * FROM Users WHERE User = '{username}';")
        return render_template('panel.html', user_info=user_info)
    return redirect('/api-user/login')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8501)