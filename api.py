'''
Created on Nov 23, 2017

@author: Sara
'''
import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from PdfToText import search,PdfToTextFile
from multiprocessing import Process, freeze_support
import random, threading, webbrowser
import logging



UPLOAD_FOLDER = 'C:\Users\Sara\workspace\PdfSearchEngine\ui'
ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#converts a string into list of words
def token(string2):
    string = string2
    string = string.lstrip()
    string = string.rstrip()
    string = " ".join(string.split())
    start = 0
    i = 0
    token_list = []
    for x in range(0, len(string)):
        if " " == string[i:i+1][0]:
            token_list.append(string[start:i+1])
            #print string[start:i+1]
            start = i + 1
        i += 1
    token_list.append(string[start:i+1])
    return token_list

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            PdfToTextFile(filename)
            return redirect(url_for('read_uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/read_file', methods=['GET', 'POST'])
def read_uploaded_file():
    logging.info('in read_uploaded_file')
    filename = secure_filename(request.args.get('filename'))
    try:
        return redirect(url_for('search_in_file',filename=filename))
    except IOError:
        pass
    return "Unable to read file"

@app.route('/search_file', methods=['GET', 'POST'])
def search_in_file():
    logging.info('in search_in_file')
    if request.method == 'POST':
        filename = secure_filename(request.args.get('filename'))
        query = request.form['query']
        if not query:
            return '''
                <!doctype html>
                <title>Search in the File</title>
                <h1>Error!!!</h1>
                <form action="" method=post enctype=multipart/form-data>
                <p><input type=text name=query>
                <input type=hidden name=filename value='''+ filename +'''>
                <input type=submit value=Search>
                </form> '''
        list_of_words = token(query)
        result = search(filename,list_of_words)
        result = result.replace('\n', '<br>')
        str1 = ''.join(list_of_words)
        return '''
            <!doctype html>
            <title>Search in the File</title>
            <h1>Search in the File</h1>
            <form action="" method=post enctype=multipart/form-data>
            <p><input type=text name=query>
            <input type=hidden name=filename value='''+ filename +'''>
            <input type=submit value=Search>
            </form><br><br><h2>Search Results for: '''+ str1 + '''  </h2><br><br>'''+ result
    filename = secure_filename(request.args.get('filename'))
    return '''
    <!doctype html>
    <title>Search in the File</title>
    <h1>Search in the File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=text name=query>
      <input type=hidden name=filename value='''+ filename +'''>
         <input type=submit value=Search>
    </form>
    '''
        
def run_browser(port):
    # MacOS
    #chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    # Windows
    #chrome_path = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --window-size=500,500 --app=%s'
    # Linux
    # chrome_path = '/usr/bin/google-chrome %s'
    #port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    #url = "http://127.0.0.1:5002"
    chrome = webbrowser.get(r'C:\\Program\ Files\ (x86)\\Google\\Chrome\\Application\\chrome.exe --window-size=500,500 --app=%s')
    #threading.Timer(1.25, lambda: webbrowser.get(r'C:\\Program\ Files\ (x86)\\Google\\Chrome\\Application\\chrome.exe --window-size=500,500 --app=%s').open(url) ).start()
    chrome.open(url)

def run_app(port):
    app.run(port=port, debug=True)


if __name__ == '__main__':
    freeze_support()
    port = 5000 + random.randint(0, 999)
    a = Process(target=run_app, args=(port,))
    a.start()

    b = Process(target=run_browser, args=(port,))
    b.start()
