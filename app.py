import json, time
from flask import Flask, redirect, url_for, request,render_template


#app = Flask(__name__)

app = Flask(__name__, static_url_path='/assets')

# @app.route('/success/<name>')
# def success(name):
#     return 'welcome %s'% name



# @app.route('/login',methods = ['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         user = request.form['nm']
#         return redirect(url_for('success',name = user))
#     else:
#         user = request.args.get('nm')
#         return redirect(url_for('success',name = user))

@app.route('/process',methods = ['POST', 'GET'])
def process():
    #cur_dict={"request_type":"generic"}
    cur_dict={}
    #cur_dict=dict(request.form)
    if request.method == 'POST':
        posted_data=request.data.decode("utf-8")
        posted_data_dict=json.loads(posted_data)
        #posted_data=posted_data.decode("utf-8")
        #cur_dict={"request_type":"POST"}
        #request.data
        cur_dict["data"]=posted_data_dict
        cur_dict["time"]=time.ctime()
        fopen=open("query_log.txt","a")
        fopen.write(json.dumps(cur_dict)+"\n")
        fopen.close()

    return json.dumps(cur_dict)

    # if request.method == 'POST':
    #     user = request.form['nm']
    #     return redirect(url_for('success',name = user))
    # else:
    #     user = request.args.get('nm')
    #     return redirect(url_for('success',name = user))


 
@app.route("/")
def hello_world():
    fopen=open("templates/index_template.html")
    content=fopen.read()
    fopen.close()
    return content #json.dumps(dict0) #render_template("input.html")
#return render_template("input.html", title="Hello")
