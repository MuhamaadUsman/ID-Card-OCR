from PIL import Image
from nic_recognizer import NICRecognizer
import numpy as np
import re, json
from datetime import date, datetime
import cv2 as cv
from Keypoint_detector import KeyPoint_Detector
from ImageAlignment import Alignment
from Enhancer import Enhancer
import easyocr

recognizrePath = r'models/AlexNet_classifier_final.pth'
Keypoint_model_path = r'models/ocr_keypoints_rcnn.pth'
enhancerPath = r'models/Enhancer.pth'
reader = easyocr.Reader(['en'], gpu=False)
card_dict = {"CNIC Front": 1, "CNIC Back": 2, "SNIC Front": 3, "SNIC Back": 4, "Non_CNIC": 0}
nic_recognizer = NICRecognizer(recognizrePath)
enhancer = Enhancer(enhancerPath)
key_point_decetor = KeyPoint_Detector(Keypoint_model_path)

with open('fieldSet.json') as f:
    field_set = json.load(f)

"""
Classifiy
adjust
TranslateImage
"""


class ProductBase:
    def __int__(self):
        # self.card_dict = {"CNIC": 1, "CNIC Back": 2, "SCNIC": 3, "SCNIC Back": 4, "Not CNIC": 0}
        # self.nic_recognizer = NICRecognizer(recognizrePath)
        # self.key_point_decetor = KeyPoint_Detector(Keypoint_model_path)
        print('-----> Init')

    # def classifier(self, file_path, files):
    #     print("here")
    #     f = os.path.join(file_path, files[0])
    #     if os.path.isfile(f):
    #         input_image = Image.open(f)
    #         nic_recognizer = NICRecognizer(recognizrePath)
    #         print("here")
    #         output = nic_recognizer.predict(input_image, 1)
    #         if (output[0][0] != 'output[0][0]'):
    #             rcnn_pred = self.key_point_decetor.getKeyPoints(input_image)
    #             keypoints = rcnn_pred[0]['keypoints'].detach().numpy()[0]
    #             bboxes = rcnn_pred[0]['boxes'][0].detach().numpy()
    #             input_image_array = np.array(input_image)
    #             warped = align(keypoints, input_image_array)
    #             color_coverted = cv.cvtColor(warped, cv.COLOR_BGR2RGB)
    #             pil_image = Image.fromarray(color_coverted).convert('RGB')
    #             enhanced_image = self.enhancer.enhance(pil_image)
    #             image_tensor = enhanced_image.data
    #             image_numpy = image_tensor[0].cpu().float().numpy()
    #             image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0
    #             image_numpy = image_numpy.astype(np.uint8)
    #             ocr_result = reader.readtext(image_numpy, detail=0, adjust_contrast=0.7, rotation_info=[90, 180, 270])
    #
    #         return ocr_result
    #
    # def api_classifier(self, files):
    #     final_result = pd.DataFrame(columns=['Doc_name', 'DOC_ID', 'Confidence', 'Code'])
    #     for i in files:
    #         im = Image.fromarray(files[i])
    #         result = self.nic_recognizer.predict(im, 1)
    #         card = self.card_dict[result[0][0]]
    #         number = result[0][1]
    #         number = str(round(number, 3) * 100) + '%'
    #         code = '00'
    #         out_list = [i, card, number, code]
    #         final_result.loc[len(final_result)] = out_list
    #         out_list.clear()
    #
    #     return final_result

    def __adjust_image__(self, image, labels):
        predictions = key_point_decetor.getKeyPoints(image)
        keypoints = predictions[0]['keypoints'].detach().numpy()[0][0:4][:,0:2]
        # bboxes = predictions[0]['boxes'][0].detach().numpy()
        cvImage = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
        cropped = Alignment(keypoints, cvImage, labels)
        return cropped

    def classify_images(self, data):
        output = []
        for d in data:
            result = nic_recognizer.classify(d['docValue'], 1)
            output.append({
                'doc_name': d['docName'],
                'doc_type': result[0][0],
                'error_code': '00'
            })
        return output

    def dates_parsing(self, dates):

        dates = [datetime.strptime(d, '%d%m%Y') for d in dates]
        dates.sort()
        dates = [d.strftime("%d-%m-%Y") for d in dates]

        # expiry_date = ''
        # issue_date = ''
        # birth_date = ''

        # if len(dates)==3:
            
        #     birth_date = dates[0]
        #     issue_date = dates[1]
        #     expiry_date = dates[2]

        # if len(dates)==2:

        #     todays_date = date.today()
        #     year = todays_date.year
        #     check = {dates[-1]: int(dates[-1][-4:]), dates[-2]: int(dates[-2][-4:])}
        #     prim_date = max(check, key=check.get)
        #     sec_date = min(check, key=check.get)
        #     chk_date = max(int(dates[-1][-4:]), int(dates[-2][-4:]))
            
        #     if year < chk_date: 
        #         expiry_date = prim_date
        #         if chk_date < year-10: birth_date = sec_date
        #         else: issue_date = sec_date
                    
        #     else:
        #         issue_date = prim_date
        #         birth_date = sec_date

        # if len(dates)==1:

        #     todays_date = date.today()
        #     year = todays_date.year
            
        #     if year < int(dates[0][-4:]):
        #         expiry_date = dates[0]
        #     elif int(dates[0][-4:]) < year-10:
        #         birth_date = dates[0]
        #     else: 
        #         issue_date = dates[0]
        
        return dates

    def __parsefields__(self, result, docType):
        if docType=='Non_CNIC':
            return {"raw": " ".join(result)}

        fields = field_set[docType]['fields']
        check_list = field_set[docType]['required']

        # dict = ['name', 'husband', 'father', 'gender', 'country', 'stay']
        # id = []
        # for idx, r_data in enumerate(result):
        #     if set(r_data.lower().split()) & set(dict):
        #         id.append(result[idx+1])

        # nic_r = r'^[0-9]{5}-[0-9]{7}-[0-9]$'
        dates = []
        p_dates = []
        for item in result:
            item = item.strip()
            digit = 0
            if (item.find('-')==-1) and (item.find('.')==-1) and (item.find('/')==-1) and (item.find(')')==-1) and (item.find('(')==-1):
                pass
            else:
                for idx, check in enumerate(item):
                    if check.isdigit():
                        digit += 1
                        index = idx
                if digit==13: fields['IDNo']=re.sub(r'[^0-9-]+', '',item[:16])
                if digit==8: dates.append(re.sub(r'[^0-9]+', '',item))
                if digit==9 or digit==10: dates.append(re.sub(r'[^0-9]+', '',item[:index-1]))
                
        p_dates = self.dates_parsing(dates)
        for k in ['DOB', 'DOI', 'DOE']:
            if k in fields.keys():
                try: 
                    fields[k] = p_dates[0]
                    p_dates.pop(0)
                except Exception as e:
                    print('Error : {} - in parsefields'.format(e))
            if len(p_dates) > 0:
                fields['other_dates'] = p_dates
        return fields

    def translateImage(self, data, enhancement=False):
        output = []
        for d in data:
            card_img = d['docValue']
            test_case = self.__adjust_image__(card_img, d['doc_type'])
            if enhancement:
                color_coverted = cv.cvtColor(test_case, cv.COLOR_BGR2RGB)
                cv_img = Image.fromarray(color_coverted).convert('RGB')
                test_case = enhancer.enhance(cv_img).data[0].detach().numpy()
                test_case = ((np.transpose(test_case, (1, 2, 0)) + 1) / 2.0 * 255.0).astype(np.uint8)

            result = reader.readtext(test_case, detail=0, adjust_contrast=0.7, min_size=80)
            refinedSet = self.__parsefields__(result, d['doc_type'])

            output.append({
                'doc_name': d['docName'],
                'doc_type': d['doc_type'],
                'result_set': refinedSet,
                'error_code': '00',
                'raw_data': result,
            })
        return output
