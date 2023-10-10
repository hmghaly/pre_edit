import json, time, re, copy
from flask import Flask, redirect, url_for, request,render_template, send_file, send_from_directory
from code_utils.general import *
from code_utils.backend_utils import *
from code_utils.rnn_utils import *
from code_utils.cat_utils import *
from code_utils.sqld_utils import *

app = Flask(__name__)

upload_dir="uploaded"
processing_dir="processing"
output_dir="output"
logs_dir="logs"
if not os.path.exists(upload_dir): os.makedirs(upload_dir)
if not os.path.exists(processing_dir): os.makedirs(processing_dir)
if not os.path.exists(output_dir): os.makedirs(output_dir)
if not os.path.exists(logs_dir): os.makedirs(logs_dir)

repl_log_fpath=os.path.join(logs_dir,"repl.txt")

wv_fpath0="data-models/editing_word2vec_1198062_20.model"
cur_wv_model=Word2Vec.load(wv_fpath0)

# nn_model_path="data-models/model-refined-full-20wv-1-408-1-128-1-0.001-50000.model"
# loaded_model_OLD=load_nn(nn_model_path,seq_nn_OLD,extract_ft_lb,epoch_i=5,cur_wv_path=wv_fpath0)

nn_model_path2="data-models/model-refined-nn-iter-full-new-1-408-1-256-1-0.0001-10000.model"
loaded_model=load_nn(nn_model_path2,seq_nn,extract_ft_lb,epoch_i=None,wv_model=cur_wv_model)

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
@app.route('/check_repl',methods = ['POST', 'GET'])
def check_repl():
    cur_dict={}
    cur_word = request.args.get('word')
    output=refined_first_token_dict.get(cur_word,{})
    cur_dict["output"]=output

    #cur_dict["link"]=cur_link
    # try: output=read_file(cur_link)
    # except: output=json.dumps(cur_dict) 
    return json.dumps(cur_dict) 

@app.route('/list_edits',methods = ['POST', 'GET'])
def list_edits():
    cur_list=[]
    repl_log_fopen=open(repl_log_fpath)
    for line0 in repl_log_fopen:
        cur_list.append(json.loads(line0))
    return json.dumps(cur_list)


@app.route('/dashboard',methods = ['POST', 'GET'])
def dashboard():
    # fopen=open("templates/dashboard_template.html")
    # content=fopen.read()
    # fopen.close()
    return read_file("templates/dashboard_template.html") #content


@app.route('/input',methods = ['POST', 'GET'])
def input_interface():
    fopen=open("templates/input_template.html")
    content=fopen.read()
    fopen.close()
    return content

#pre_edit(sent_str,nn_model_obj,first_token_dict,pred_threshold=0.5)
@app.route('/pre_edit_api',methods = ['POST', 'GET'])
def pre_edit_api():
    cur_dict={}
    posted_data_dict={}
    if request.method == 'POST':
        posted_data=request.data.decode("utf-8")
        posted_data_dict=json.loads(posted_data)    
    default_text="UN missions in DRC and CAR, Chad and Sudan"
    text0=posted_data_dict.get("text",default_text)
    freq_threshold0=posted_data_dict.get("freq_threshold",None)
    wt_threshold0=posted_data_dict.get("wt_threshold",0.3)
    cur_dict["text"]=text0
    pre_edited_html,valid_repl=pre_edit_html(text0,loaded_model,refined_first_token_dict,pred_threshold=wt_threshold0,freq_threshold=freq_threshold0)
    cur_dict["pre_edited_html"]=pre_edited_html
    cur_dict["repl_list"]=valid_repl
    return json.dumps(cur_dict)

@app.route('/log_repl',methods = ['POST', 'GET'])
def log_repl():
    cur_dict={}
    posted_data_dict={}
    if request.method == 'POST':
        posted_data=request.data.decode("utf-8")
        posted_data_dict=json.loads(posted_data)
    posted_data_dict["time"]=time.ctime()
    log_something(json.dumps(posted_data_dict),repl_log_fpath)
    cur_dict["success"]=True
    return json.dumps(cur_dict)


@app.route('/interface',methods = ['POST', 'GET'])
def interface():
    cur_dict={"request_type":"generic"}
    cur_link = request.args.get('link')
    cur_dict["link"]=cur_link
    try: output=read_file(cur_link)
    except: output=json.dumps(cur_dict) 
    return output 

@app.route('/process',methods = ['POST', 'GET'])
def process():
    #cur_dict={"request_type":"generic"}

    cur_dict={}
    #cur_dict=dict(request.form)
    if request.method == 'POST':
        posted_data=request.data.decode("utf-8")
        posted_data_dict=json.loads(posted_data)

        #cur_docx_path="uploaded/2212742_Case_Study_Handbook_ALK_part_1.docx"
        
        cur_docx_path=posted_data_dict.get("fpath")
        new_edit_pre_edit_list,all_repl_inst_list,analysis_dict=analyze_pre_edit_docx(cur_docx_path,loaded_model,refined_first_token_dict,pred_threshold=0.3)
        #new_edit_list=[(v[1],v[4],v[-1]) for v in new_edit_pre_edit_list]
        new_edit_list=[(v[0],v[-1]) for v in new_edit_pre_edit_list]
        cur_docx_fname=os.path.split(cur_docx_path)[-1]
        cur_html_fname=cur_docx_fname.replace(".docx",".html")
        if not cur_html_fname.endswith(".html"): cur_html_fname+=".html"
        cur_html_fpath=os.path.join(processing_dir,cur_html_fname)
        cur_template_fpath="templates/pre-editing_table_template_controls.html"
        edit_list2html(new_edit_list,cur_html_fpath,template_fpath=cur_template_fpath,headers=["Output"])
        cur_dict=copy.deepcopy(posted_data_dict)
        cur_dict["cur_html_fpath"]=cur_html_fpath
        #posted_data=posted_data.decode("utf-8")
        #cur_dict={"request_type":"POST"}
        #request.data 
        #cur_dict["data"]=posted_data_dict
        cur_dict["time"]=time.ctime()
        cur_dict["action"]="processed"
        cur_dict["success"]=True
        cur_dict["analysis_dict"]=analysis_dict
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

