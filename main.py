import os
from re import S
from urllib.request import ProxyDigestAuthHandler
from flask import Flask, request, redirect, url_for, session, render_template, json
from numpy import array
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from approximaton import gauss_method
import logging
from flask import send_file
from aproksimacija import *

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('HELLO WORLD')

@app.route("/delete")
def home():
    if os.path.exists("plot.png"):
      os.remove('plot.png')
      set_global_polynom()
    return "success"
  
  
@app.route('/get_graph')
def get_image():
    filename = 'plot.png'
    return send_file(filename, mimetype='image/gif')

@app.route('/polinomial', methods=['POST'])
def poliniomialLsm():
    data = request.form
    print(data, 'data')
    a = request.form['array'].split(",")
    print(a,"a")
    newArray = []
    for i in range (len(a)):
        print(a[i])
        if a[i]!=',':
          newArray.append(float(a[i]))
    myPointsMatrix =(submit_values(newArray, int(len(newArray)/2)))
    return (str((button_select_points_lin_used(myPointsMatrix, int(len(newArray)/2), int(data['degree'])+1))))
    

@app.route('/degree', methods=['POST'])
def degreeLsm():
    data = request.json
    myPointsMatrix =(submit_values(data, int(len(data)/2)))
    return (str((button_select_points_pow_used(myPointsMatrix, int(len(data)/2)))))
  
  
@app.route('/log', methods=['POST'])
def logLsm():
    data = request.json
    myPointsMatrix = (submit_values(data, int(len(data)/2)))
    set_global_method("log")
    return (str((button_select_points_log_used(myPointsMatrix, int(len(data)/2)))))
  
  
@app.route('/exp', methods=['POST'])
def expLsm():
    data = request.json
    myPointsMatrix =(submit_values(data, int(len(data)/2)))
    set_global_method("exp")
    return (str((button_select_points_exp_used(myPointsMatrix, int(len(data)/2)))))
  
  
@app.route('/upload', methods=['POST'])
def fileUpload():
    target=os.path.join(UPLOAD_FOLDER,'test_docs')
    if not os.path.isdir(target):
        os.mkdir(target)
    logger.info("welcome to upload`")
    file = request.files['file'] 
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)
    session['uploadFilePath']=destination
    response=button_read_values_used(filename)
    return response
  
@app.route('/function', methods=['POST'])
def functionEntey():
  polinom = request.form['function']
  a = request.form['array'].split(",")
  print(a,"a")
  b = []
  for i in range (len(a)):
      print(a[i])
      if a[i]!=',':
        b.append(float(a[i]))
  return str(button_select_function_used(polinom, b, len(b)))

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)
    
flask_cors.CORS(app, expose_headers='Authorization')
