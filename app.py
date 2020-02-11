
from flask import Flask, make_response,render_template
from flask import render_template, request, redirect,send_from_directory
from werkzeug.utils import secure_filename
import json
import re
import os

app = Flask(__name__)

def transform(text_file_contents):
    config = text_file_contents
    parentkey= [*config]
    Parent = config[parentkey[0]]
    childkeys= [*Parent[0]]
    ChildID =childkeys[0]
    ChildName =childkeys[1]

    final=[]
    for x in Parent:
        mod = {}

        syno = x[ChildName].split()  
        distNameSyno=[]
        temp = ''
        for i in range(len(syno)):
            temp = temp + syno[i] +' '
            distNameSyno.append(temp.rstrip())
        #m = {"canonicalForm":"distID","list":["distName"]}
        mod["canonicalForm"] =  x[ChildID]
        mod["list"] = distNameSyno
        final.append(mod)       
        
    # remove duplicate synonyms
    synoGenerated=[]
    for a in final:
        mod= {}
        newsyno= []
        temp= a["list"]
        for j in range(len(a["list"])):
            t = temp[j].upper()

            count= 0
            for b in final:
                for k in range(len(b["list"])):
                    if b["list"][k].upper()==t:
                        count= count + 1    

            if count == 1 :
                #remove tariling characters
                if re.search(r"\d+.\d+",t):
                    t=re.sub(r"(?<!\d)\.(?!\d)"," ",t)
                else:
                    t=re.sub(r"[.]"," ",t)    
                t= re.sub(r',$','',t)
                t= re.sub(r'\&$','',t)
                t= re.sub(r' AND$','',t)
                t=t.rstrip()
                #-----
                newsyno.append(t)
                #adding "and" versions for &
                if re.search(r" \& ",t):
                    newsyno.append(re.sub(r'\&',"AND",t))
                #adding "&" versions for " and "    
                if re.search(r" AND ",t):
                    newsyno.append(re.sub(r" AND "," & ",t))
                #removing []
                if re.search(r'[[]',t):
                    if re.search(r'[]]',t):
                        t1 = re.sub(r'[[]','',t)
                        t1 = re.sub(r'[]]','',t1)
                        newsyno.append(t1)
                #replacing [] with ()
                if re.search(r'[[]',t):
                    if re.search(r'[]]',t):
                        t2 = re.sub(r'[[]','(',t)
                        t2 = re.sub(r'[]]',')',t2)
                        newsyno.append(t2)
        #filling null with the original values(this creates duplicates)
        if newsyno == []:
            for x in Parent:
                if x[ChildID] == a["canonicalForm"]:
                    newsyno.append(x[ChildName])
        #m = {"canonicalForm":"distID","list":["distName"]}
        
        mod["canonicalForm"] =  a["canonicalForm"]
        mod["list"] = newsyno
        synoGenerated.append(mod)
        
    return synoGenerated


@app.route('/')
def form():
    return """
        <html>
            <body>
                <h1>Synonyms generator for LUIS Intents</h1>


                <form action="/transform" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file" />
                    <input type="submit" />
                </form>
            </body>
        </html>
    """

@app.route('/transform', methods=["POST"])
def transform_view():
    request_file = request.files['data_file']
    myfile = request_file.read()
    if not request_file:
        return "No file"

    file_contents = json.loads(myfile, encoding='utf-8-sig')
    result = transform(file_contents)

    outputfile ="result_"+ request_file.filename
    outputattchment = "attachment; filename=" + outputfile
    resultres = json.dumps(result,indent=4, sort_keys=True)
    response = make_response(resultres)
    response.headers['my-custom-header'] = 'my-custom-status-0'
    response.headers["Content-Disposition"] = outputattchment
    return response


if __name__ == "__main__":
    app.run(debug=True)    