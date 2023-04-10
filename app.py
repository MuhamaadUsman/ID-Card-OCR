try:
    import os, imghdr, base64, json, logging
    from io import BytesIO
    from PIL import Image
    from flask import Flask, request, redirect, render_template, send_file, make_response, url_for, jsonify
    from flask_restful import Resource, Api
    from apispec import APISpec
    from marshmallow import Schema, fields
    from apispec.ext.marshmallow import MarshmallowPlugin
    from flask_apispec.extension import FlaskApiSpec
    from flask_apispec.views import MethodResource
    from flask_apispec import marshal_with, doc, use_kwargs
    from werkzeug.utils import secure_filename
    from wtforms import StringField, DecimalField

    from Enhancer import ResnetGenerator, ResnetBlock
    import ProductBase as pb
except Exception as e:
    print("__init__ Modules are Missing {}".format(e))
    exit()


"""
API calls

classify: Classify an image into 5 categories [CNIC front, ...]
translateImage: performs OCR and translate image into text (must provide image type defined in above categories)
classifyAndTranslate: classify image nad then perform OCR on it
simpleTranslate: performs OCR without image enhancements
classifyAndSimpleTranslate: Classify image and performs OCR without enhancements
"""

app = Flask(__name__)

productBase = pb.ProductBase()
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
ALLOWED_EXTENSIONS = ['.jfif', '.png', '.jpeg', '.jpg','.JPG']
IMAGE_TYPES = ['tiff', 'jpeg', 'png']
logging.basicConfig(filename='dev.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


app.secret_key = "secret key"


def allowed_file(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg'))

path = os.getcwd()

UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def add_header(resp):
    resp.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    resp.headers['Content-Security-Policy'] = "default-src 'self';"
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers['Cache-Control'] = 'public, max-age=0'
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'SAMEORIGIN'
    resp.headers['X-XSS-Protection'] = '1; mode=block'

    return resp

# @app.route("/", methods=['POST', 'GET'])
# def welcomeScreen():
#     resp = make_response(render_template('welcome.html', name='Hello'))
#     resp = add_header(resp)
#     return resp


@app.route("/", methods=['POST', 'GET'])
def uploadImage():
    resp = make_response(render_template("base.html"))
    resp = add_header(resp)
    return resp


@app.route("/Results", methods=['POST'])
def results():
    if request.method == 'POST':
        docName = ''
        docValue =''
        doc_type = ''
        incorrect_ext = []
        correct_ext = []
        files = request.files.getlist('files[]')

        if 'files[]' not in request.files:
            return redirect(request.url)

        else:
            for file in files:
                filename = secure_filename(file.filename)
                docName = filename
                if file and allowed_file(file.filename):
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.isfile(f):
                        docValue = Image.open(f)
                    doc_type = ''
                    correct_ext.append({
                        'docName': docName,
                        'docValue': docValue,
                        'doc_type': doc_type
                    })
                else:
                    incorrect_ext.append({'doc_name': docName, 'error_code': '01', 'doc_type': '-1'})

        cc = productBase.classify_images(correct_ext)
        for d, cls in zip(correct_ext, cc):
            d['doc_type'] = cls['doc_type']
        o_output = productBase.translateImage(correct_ext, True)
        # o_output = productBase.translateImage(correct_ext)
        o_output.extend(incorrect_ext)
        output = {
            'Image': o_output[0]['doc_name'],
            'card': o_output[0]['doc_name'],
            'OCR results': o_output[0]['result_set']
        }
        resp = make_response(render_template("output.html", results=output))
        resp = add_header(resp)
        return resp


# @app.route("/Download", methods=['GET'])
# def Download():
#     # To save excel file in datetime format
#     datestring = datetime.strftime(datetime.now(), ' %d_%m_%Y')
#     df = pd.DataFrame(o_output)
#
#     # For dataframe
#     excel_output = BytesIO()
#     writer = pd.ExcelWriter(excel_output, engine='xlsxwriter')
#     df.to_excel(writer, sheet_name='results_' + datestring, index=False)
#
#     writer.close()
#
#     excel_output.seek(0)
#     Excel_output_filename = 'Results' + ' ' + datestring + '.xlsx'
#     return send_file(excel_output, download_name=Excel_output_filename, as_attachment=True)

def __raw_data_processing__(req_data):
    data = req_data['Data']
    incorrect_ext = []
    correct_ext = []
    for d in data:
        docName = d['doc_name']
        docValue = d['doc_value']
        try:
            doc_type = d['doc_type']
        except:
            doc_type = d['doc_type'] = ''
        image_decode = base64.b64decode(docValue)
        ext = imghdr.what(None, h=image_decode)
        if ext not in IMAGE_TYPES:
            incorrect_ext.append({'doc_name': docName, 'error_code': '01', 'doc_type': '-1'})
        else:
            img = Image.open(BytesIO(image_decode))
            correct_ext.append({
                'docName': docName,
                'docValue': img,
                'doc_type': doc_type
            })
    return incorrect_ext, correct_ext

@app.route('/Classify', methods=['POST'])
def classify():
    productBase = pb.ProductBase()
    req_data_raw = request.get_json()['user_photo']
    req_data = json.loads(req_data_raw)
    incorrect_ext, correct_ext = __raw_data_processing__(req_data)
    outPut = productBase.classify_images(correct_ext)
    outPut.extend(incorrect_ext)
    response_dict = {
        'RRN': req_data['RRN'],
        'responce_code': '00',
        'responce_discription': 'Success',
        'Data': outPut
    }

    resp = json.dumps(response_dict)

    return resp, 200

@app.route('/translateImage', methods=['POST'])
def translateImage():
    productBase = pb.ProductBase()
    req_data_raw = request.get_json()['user_photo']
    req_data = json.loads(req_data_raw)
    incorrect_ext, correct_ext = __raw_data_processing__(req_data)
    output = productBase.translateImage(correct_ext, True)
    output.extend(incorrect_ext)
    response_dict = {
        'RRN': req_data['RRN'],
        'responce_code': '00',
        'responce_discription': 'Success',
        'Data': output
    }

    resp = json.dumps(response_dict)
    return resp, 200

@app.route('/classifyAndTranslate', methods=['POST'])
def classifyAndTranslate():
    productBase = pb.ProductBase()
    req_data_raw = request.get_json()['user_photo']
    req_data = json.loads(req_data_raw)
    incorrect_ext, correct_ext = __raw_data_processing__(req_data)
    print((incorrect_ext))
    cc = productBase.classify_images(correct_ext)
    for d, cls in zip(correct_ext, cc):
        d['doc_type'] = cls['doc_type']
    output = productBase.translateImage(correct_ext, True)
    print(output)
    output.extend(incorrect_ext)
    response_dict = {
        'RRN': req_data['RRN'],
        'responce_code': '00',
        'responce_discription': 'Success',
        'Data': output
    }

    resp = json.dumps(response_dict)

    return resp, 200

# @app.route('/simpleTranslate', methods=['POST'])
def simpleTranslate():
    productBase = pb.ProductBase()
    req_data_raw = request.get_json()['user_photo']
    req_data = json.loads(req_data_raw)
    incorrect_ext, correct_ext = __raw_data_processing__(req_data)
    output = productBase.translateImage(correct_ext)
    output.extend(incorrect_ext)
    response_dict = {
        'RRN': req_data['RRN'],
        'responce_code': '00',
        'responce_discription': 'Success',
        'Data': output
    }

    resp = json.dumps(response_dict)
    # might need to add headers
    return resp


@app.route('/classifyAndSimpleTranslate', methods=['POST'])
def classifyAndSimpleTranslate():
    productBase = pb.ProductBase()
    req_data_raw = request.get_json()['user_photo']
    req_data = json.loads(req_data_raw)
    incorrect_ext, correct_ext = __raw_data_processing__(req_data)
    cc = productBase.classify_images(correct_ext)
    for d, cls in zip(correct_ext, cc):
        d['doc_type'] = cls['doc_type']
    output = productBase.translateImage(correct_ext)
    print(output)
    output.extend(incorrect_ext)
    response_dict = {
        'RRN': req_data['RRN'],
        'responce_code': '00',
        'responce_discription': 'Success',
        'Data': output
    }
    resp = json.dumps(response_dict)
    return resp, 200


if __name__ == "__main__":
    app.run()
