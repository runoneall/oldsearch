from flask import *
import crawler
app = Flask(__name__)

@app.route('/')
def hello():
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
            info_dict = crawler.Get_Links(f'q={query}')
            if info_dict == {}:
                return render_template(
                    'noResult.html', 
                    target_search=query,
                )
            # max_page = crawler.GetMaxPage(f'q={query}')
            return render_template(
                'search.html', 
                target_search=query, 
                info_dict=info_dict, 
                info_dict_keys=list(info_dict.keys()),
                # max_page=max_page
            )
        else:
            return "参数错误"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=47)