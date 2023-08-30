# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

import cv2
import copy
import time
import predict_det
import predict_rec
from utility import get_rotate_crop_image
import paddle
paddle.disable_signal_handler()  #*  disable some weird setting of

class TextSystem(object):
    def __init__(self, args):
        start = time.time()
        self.text_detector = predict_det.TextDetector(args)
        print("init_time",time.time()-start)
        start = time.time()
        self.text_recognizer = predict_rec.TextRecognizer(args)
        print("init_time",time.time()-start)
        self.drop_score = 0.5
        self.args = args
        self.crop_image_res_index = 0
        
    def __call__(self, img):
        ori_im = img.copy()
        print("---detecting boxes---")
        dt_boxes, elapse = self.text_detector(img)
        if dt_boxes is None:
            print("no dt_boxes found, elapsed : {}".format(elapse))
            return None, None
        print(f"dt_boxes num : {len(dt_boxes)}, elapsed : {elapse}")
        img_crop_list = []  #list of croped image for recognition
        dt_boxes = sorted_boxes(dt_boxes)
        # print(dt_boxes,".....")  list([4,2],[4,2],...)
        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            # print(tmp_box,"ttt")  #shape(4,2)
            img_crop = get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)

        print("----recogizing text----")
        rec_text, elapse = self.text_recognizer(img_crop_list)
        print(f"rec_res num  : {len(rec_text)}, elapsed : {elapse}")
        filter_boxes, filter_rec_res = [], []
        for box, rec_result in zip(dt_boxes, rec_text):
            text, score = rec_result[0], rec_result[1]
            if score >= self.drop_score:
                # print(rec_result)   ('text',acc)
                filter_boxes.append(box)
                filter_rec_res.append(rec_result)
        return filter_boxes, filter_rec_res

import time
def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:  dt_boxes(array):detected text boxes with shape [4, 2]
    return: sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        for j in range(i, -1, -1):
            if abs(_boxes[j + 1][0][1] - _boxes[j][0][1]) < 10 and \
                    (_boxes[j + 1][0][0] < _boxes[j][0][0]):
                tmp = _boxes[j]
                _boxes[j] = _boxes[j + 1]
                _boxes[j + 1] = tmp
            else:
                break
    return _boxes

def init(args):
    text_sys = TextSystem(args) 
    return text_sys
def main(text_sys,image_file,return_dict):
    start = time.time()
    #['/tmp/screenshot.jpg']
    print("-----------dasfjkosfj")
    # text_sys = TextSystem(args)   #??  bottle neck
    print("-------------")
    _st = time.time()
    # for idx, image_file in enumerate(image_file_list):
    img = cv2.imread(image_file)
    
    dt_boxes, rec_res = text_sys(img)
    
    boxes = dt_boxes
    txts = [rec_res[i][0] for i in range(len(rec_res))] 
    print('len text and boxes',len(txts),len(boxes))
    print("The predict total time is {}".format(time.time() - _st))

    return_dict['test']={'finish':True,'txts':txts,'boxes':boxes}
    print(f"delay time {time.time()-start}--------------------------")  #3.2

def main_local(mode='en'):# 'en', 'jp', 'ch'
    project_path = "."
    args = Arg(project_path=project_path)
    args.image_dir = f"./assets/{mode}_test.png"
    if mode == 'jp':
        print("multi jp")
        # args.det_model_dir=f'{project_path}/model/Multilingual_PP-OCRv3_det_slim_infer'
        # args.det_model_dir=f'{project_path}/model/ch_PP-OCRv3_det_infer'
        args.det_model_dir=f'{project_path}/model/Multilingual_PP-OCRv3_det_infer'
        args.rec_model_dir = f'{project_path}/model/japan_PP-OCRv3_rec_infer/'
        args.rec_char_dict_path = f'{project_path}/ppocr/utils/dict/japan_dict.txt'
    elif mode == 'ch':
        print("v4 ch")
        args.det_model_dir=f'{project_path}/model/ch_PP-OCRv3_det_infer'
        args.rec_model_dir=f'{project_path}/model/ch_PP-OCRv4_rec_infer/'
        args.rec_char_dict_path = f'{project_path}/ppocr/utils/ppocr_keys_v1.txt'
    elif mode == 'en':
        print("v4 en")
        args.det_model_dir=f'{project_path}/model/en_PP-OCRv3_det_slim_infer'
        args.rec_model_dir=f'{project_path}/model/en_PP-OCRv4_rec_infer/'
        args.rec_char_dict_path = f'{project_path}/ppocr/utils/en_dict.txt'
    elif mode == 'zh':
        print("v4 det v3 zh")
        args.det_model_dir=f'{project_path}/model/ch_PP-OCRv3_det_infer'
        args.rec_model_dir=f'{project_path}/model/chinese_cht_PP-OCRv3_rec_infer/'
        args.rec_char_dict_path = f'{project_path}/ppocr/utils/dict/chinese_cht_dict.txt'
    else:
        raise Exception('error...') 
    return_dict = {}
    text_sys = init(args)
    main(text_sys,args.image_dir,return_dict=return_dict)
    txts = return_dict['test']['txts']
    print(f"-----detected text in {args.image_dir}------")
    for txt in txts:
        print(txt)
    print("------------------------")
    # print(return_dict['test']['boxes'])
if __name__ == "__main__":
    from arg import Arg
    import fire
    fire.Fire(main_local)