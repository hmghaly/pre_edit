import json, time, re, copy
from flask import Flask, redirect, url_for, request,render_template, send_file, send_from_directory
from code_utils.general import *
from code_utils.backend_utils import *
from code_utils.rnn_utils import *
from code_utils.cat_utils import *
from code_utils.sqld_utils import *

app = Flask(__name__)

upload_dir="uploaded"
if not os.path.exists(upload_dir): os.makedirs(upload_dir)

nn_model_path="data-models/model-refined-full-20wv-1-408-1-128-1-0.001-50000.model"
loaded_model=load_nn(nn_model_path,seq_nn_OLD,extract_ft_lb,epoch_i=5)

refined_first_token_dict_fpath="data-models/refined_first_token_dict.sqld"
refined_first_token_dict=open_sqld(refined_first_token_dict_fpath)

no_context_first_token_dict_fpath="data-models/no_context_first_token_dict.sqld"
no_context_first_token_dict=open_sqld(no_context_first_token_dict_fpath)


#app = Flask(__name__, static_url_path='/assets')

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



@app.route('/upload',methods = ['POST', 'GET'])
def upload():
    cur_dict={}
    if request.method == 'POST':
        posted_data=request.data.decode("utf-8")
        posted_data_dict=json.loads(posted_data)
        uploaded_file_dict=posted_data_dict.get("uploaded_file",{})
        file_content=uploaded_file_dict.get("data","")
        file_name=uploaded_file_dict.get("name","")
        file_name=re.sub("\s+","_",file_name)
        uploaded_fpath=os.path.join(upload_dir,file_name)
        write_base64(file_content,uploaded_fpath)
        posted_data_dict.pop('uploaded_file', None)
        cur_dict=copy.deepcopy(posted_data_dict)

        cur_dict["fpath"]=uploaded_fpath
        #cur_dict["data"]=posted_data_dict
        cur_dict["time"]=time.ctime()
        cur_dict["action"]="upload"
        cur_dict["success"]=True
        fopen=open("query_log.txt","a")
        fopen.write(json.dumps(cur_dict)+"\n")
        fopen.close()

    return json.dumps(cur_dict)


@app.route('/assets/<path:path>')
def serve_file(path):
    return send_from_directory('assets', path)

 
@app.route("/")
def index():
    fopen=open("templates/index_template.html")
    content=fopen.read()
    fopen.close()
    return content #json.dumps(dict0) #render_template("input.html")

