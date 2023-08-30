#!/usr/bin/python
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit,QWidget,QVBoxLayout
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPainter,QPen
from PyQt5.QtCore import Qt,QTimer

import os

import multiprocessing
# project_path = '/usr/local/OCR_ScreenShot'  #** for deployment
project_path = '.'  #'../OCR_ScreenShot'
sys.path.append(project_path)
# import predict_system
import time
from arg import Arg
def c(cmd_str):
    os.system(cmd_str)
def run_NN(img_path,queue,return_dict):
    start = time.time()
    print("import predict_system takings time")
    import predict_system3
    print("import system time ",time.time()-start)
    args = None
    text_sys = None
    
    while True:
        stuff = queue.get()
        if stuff['type'] == "run":
            print('run')
            predict_system3.main(text_sys,args.image_dir,return_dict=return_dict)
            return 'success'
        elif stuff['type'] == "init":
            mode = stuff['lang']
            args = Arg(project_path)
            args.image_dir=img_path
            #* didn't use cls for now
            if mode == 'jp':
                print("multi jp")
                # args.det_model_dir=f'{project_path}/model/Multilingual_PP-OCRv3_det_slim_infer'
                args.det_model_dir=f'{project_path}/model/Multilingual_PP-OCRv3_det_infer'
                args.rec_model_dir = f'{project_path}/model/japan_PP-OCRv3_rec_infer/'
                args.rec_char_dict_path = f'{project_path}/ppocr/utils/dict/japan_dict.txt'
            elif mode == 'ch':
                print("v4 ch")
                args.det_model_dir=f'{project_path}/model/ch_PP-OCRv4_det_infer'
                args.rec_model_dir=f'{project_path}/model/ch_PP-OCRv4_rec_infer/'
                args.rec_char_dict_path = f'{project_path}/ppocr/utils/ppocr_keys_v1.txt'
            elif mode == 'en':
                print("v4 en")
                args.det_model_dir=f'{project_path}/model/en_PP-OCRv3_det_slim_infer'
                args.rec_model_dir=f'{project_path}/model/en_PP-OCRv4_rec_infer/'
                args.rec_char_dict_path = f'{project_path}/ppocr/utils/en_dict.txt'
            elif mode == 'zh':
                print("v4 det v3 zh")
                args.det_model_dir=f'{project_path}/model/ch_PP-OCRv4_det_infer'
                args.rec_model_dir=f'{project_path}/model/chinese_cht_PP-OCRv3_rec_infer/'
                args.rec_char_dict_path = f'{project_path}/ppocr/utils/dict/chinese_cht_dict.txt'
            else:
                return 'fail'
            text_sys = predict_system3.init(args)
        else:
            print('dont run')

class TextWidget(QTextEdit,):
    # flameshot /src/tools/text/textwidget.cpp
    def __init__(self,window) -> None:
        super().__init__(window)
        self.setStyleSheet('''
                           background: transparent;
                           color:brown;
                           font:24px;''')
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setContextMenuPolicy(Qt.NoContextMenu)
def setWindowFlag(self):
    self.setWindowFlag(Qt.X11BypassWindowManagerHint,True)
    self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,True)  #make program always on top
    self.setWindowFlag(Qt.FramelessWindowHint,True)
    # self.setWindowFlag(QtCore.Qt.WindowSystemMenuHint,False) 
    #[keep windows in front](https://blog.csdn.net/yang1fei2/article/details/123768181)
    #[qt windows flag](https://blog.csdn.net/xuebing1995/article/details/96478891)
    #--------------------------
    self.setFocusPolicy(Qt.StrongFocus) #??
    # self.setFocusPolicy(Qt.StrongFocus)  #** flameshot/src/tools/pin/pinwidget.cpp
    # self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)  #??
    self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)  #background opacity
    self.setAttribute(Qt.WA_DeleteOnClose) #??
    self.setContextMenuPolicy(Qt.CustomContextMenu)  #??
    # self.setContentsMargins(0,0,100,100)  #??
def change_active_btn(self,lang,value):
    if lang == 'en':
        a = self.EnButton
    elif lang == 'ch':
        a = self.ChButton
    elif lang == 'jp':
        a = self.JpButton
    elif lang == 'zh':
        a = self.ZhButton
    else:
        a = self.EnButton
        print(f"errr  lang {lang}")
    a.setStyleSheet(value )
active_btn_value = '''
                    QPushButton{
                        background-color : lightblue;
                    }
                    QPushButton::pressed{
                        background-color : red;
                    }
                    '''
# Returns true if two rectangles(l1, r1)
# and (l2, r2) overlap
def do_overlap(left, right, top , bottom, 
               l2, r2,  t2,b2):
    #  https://www.geeksforgeeks.org/find-two-rectangles-overlap/
    

    if left > r2 or l2 > right:
     # l1.x       r2.x        l2.x
        # If one rectangle is on left side of other
        return False
    
    if top > b2 or t2 > bottom:
     # r1.y   l2.y  or r2.y    l1.y
        # If one rectangle is above other
        return False
    return True

def getlrtb(begin,end):
    left = min(begin.x(),end.x())
    right = max(begin.x(),end.x())
    top = min(begin.y(),end.y())
    bottom = max(begin.y(),end.y())       
    return left, right, top , bottom 
class MyWindow(QMainWindow):
    def __init__(self,screen_w,screen_h):
        super().__init__()
        self.img_path = '/tmp/screenshot.jpg' #'/tmp/screenshot.jpg'
        self.screen_w = screen_w;        self.screen_h = screen_h
        setWindowFlag(self)
        self.setFixedWidth(self.screen_w);    self.setFixedHeight(self.screen_h)
        QtWidgets.QShortcut(QtGui.QKeySequence('Esc',), self, self.closeEvent)
        
        self.initUI()
        #* timer
        self.timer = QTimer()    
        self.timer.timeout.connect(self.showWords);        self.timer.start(1000)
        #** flags
        self.is_draw = False;     
        self.select_screenshot = True
        self.already_return_NN = False
        self.enable_data_paint = False
        # self.selecting_text = False
        #** selection
        self.begin = QtCore.QPoint();     self.end = QtCore.QPoint()
        #** display img text widget (trigger at show word())
        self.lang = 'en' #en, jp, ch,zh
        self.f = open(f'{project_path}/config.txt','r+')
        self.lang = self.f.readline()
        self.f.seek(0)
        
        print("lang",self.lang)
        change_active_btn(self,self.lang, active_btn_value)
        self.screenShot_pos = (0,0,0,0)
        # https://stackoverflow.com/questions/10415028/how-to-get-the-return-value-of-a-function-passed-to-multiprocessing-process
        self.q = multiprocessing.Queue()
        manager = multiprocessing.Manager()
        self.return_dict= manager.dict()
        # self.return_dict['predict_system'] = predict_system
        self.haveoverlaplist = [] 
        print(f"runnn  -> self.lang  {self.lang}")
        if self.lang not in ('jp','en','ch','zh'):
            self.lang = 'en'
            print(f'error   lang  {self.lang} not define ')
        print("iiiiiiiiiiiiiiii")
        self.th = multiprocessing.Process(target=run_NN, args=(self.img_path,self.q,self.return_dict))
        self.th.daemon=True   #so run_nn will end when main program force exit
        self.th.start() 
        self.q.put({'type':"init",'lang':self.lang}) 
    def initUI(self):
        # ------Create the button------
        self.copybtn = QtWidgets.QPushButton(self,clicked=self.copySelectedToClipboard)
        self.copybtn.hide()
        
        self.closeButton = QtWidgets.QPushButton(self, clicked=self.closeEvent)
        b_w,b_h = 90,32;  b_x,b_y = (self.screen_w-b_w)//2, self.screen_h-3*b_h-4#self.screen_h*5//7
        self.closeButton.setGeometry(QtCore.QRect(b_x,b_y,b_w, b_h));  self.closeButton.setText("Finished")
        
        offset = b_w//2
        self.hint_label = QtWidgets.QLabel(self)
        self.hint_label.setText("Double click or press the Finished button to exit")
        self.hint_label.setGeometry(QtCore.QRect(b_x-b_w-offset,b_y-b_h,4*b_w, b_h))
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("background-color: white;")

        #**
        self.EnButton = QtWidgets.QPushButton(self, clicked = lambda: self.changelang_config('en'))
        self.EnButton.setGeometry(QtCore.QRect(b_x-b_w-offset,b_y-2*b_h,b_w, b_h));   self.EnButton.setText("en")
        #**
        self.ChButton = QtWidgets.QPushButton(self, clicked = lambda: self.changelang_config('ch'))
        self.ChButton.setGeometry(QtCore.QRect(b_x-offset,b_y-2*b_h,b_w, b_h)); self.ChButton.setText("ch")
        #**
        self.JpButton = QtWidgets.QPushButton(self, clicked = lambda: self.changelang_config('jp'))
        self.JpButton.setGeometry(QtCore.QRect(b_x+b_w-offset,b_y-2*b_h,b_w, b_h)); self.JpButton.setText("jp")
        #**
        self.ZhButton = QtWidgets.QPushButton(self, clicked = lambda: self.changelang_config('zh'))
        self.ZhButton.setGeometry(QtCore.QRect(b_x+2*b_w-offset,b_y-2*b_h,b_w, b_h)); self.ZhButton.setText("zh")
    def showWords(self):
        if len(self.return_dict.values()) == 0:  return
        if self.return_dict.values()[0]['finish'] == False:
            return
        if self.already_return_NN: return
        print("finish------")
        x,y,w,h = self.screenShot_pos  
        self.already_return_NN=True
    
        self.copyAllbtn = QtWidgets.QPushButton(self,clicked=self.copyAllToClipboard)
        self.copyAllbtn.setText("copy all")
        self.copyAllbtn.setGeometry(QtCore.QRect(x, y-50, 50, 30))
        self.copyAllbtn.show()
        # self.copyAllbtn.show()
        self.update()
        self.enable_data_paint = True
    def changelang_config(self,lang):
        if lang not in ('jp','en','ch','zh'):
            return print(f'error   lang  {self.lang} not define ')
        print(f'change lang to {lang}')
        self.f.write(lang)
        self.f.seek(0)
        former = self.lang
        self.lang = lang
        change_active_btn(self,self.lang,active_btn_value)
        change_active_btn(self,former,'')
        self.q.put({'type':"init",'lang':self.lang}) 
    def copyAllToClipboard(self):
        l = len(self.return_dict.values()[0]['boxes'])
        self.haveoverlaplist=[]
        for i in range(l):
            self.haveoverlaplist.append(i)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText('\n'.join(self.return_dict.values()[0]['txts']), mode=cb.Clipboard)
        self.update()
    def copySelectedToClipboard(self):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        # cb.setText(self.textWidget.toPlainText(), mode=cb.Clipboard)
        copy_txt = ''
        for idx in self.haveoverlaplist:
            copy_txt +=self.return_dict.values()[0]['txts'][idx]+'\n'
        cb.setText(copy_txt, mode=cb.Clipboard)
        self.update()
    def closeEvent(self, a0) -> None:
        print("exit")
        self.f.close()
        sys.exit()
    def mouseDoubleClickEvent(self, a0) -> None:
        print("double click")
        self.closeEvent(a0)
    def paintEvent(self, event=None):  #** black opacity background
        if self.select_screenshot:
            painter = QtGui.QPainter(self)
            painter.setOpacity(0.4)
            painter.setBrush(QtCore.Qt.black)  #** background color
            # painter.setPen(QPen(QtCore.Qt.black))   
            painter.setPen(Qt.NoPen)  #** disable border
            if self.is_draw == False:
                painter.drawRect(self.rect())
            else:
               left, right, top , bottom  = getlrtb(self.begin,self.end)
               painter.drawRect(QtCore.QRect(0,0,  self.screen_w,top))      #upper rect
               painter.drawRect(QtCore.QRect(0,bottom, self.screen_w,self.screen_h)) #bottom rect
               painter.drawRect(QtCore.QRect(0,top,  left,bottom-top))     #left rect
               painter.drawRect(QtCore.QRect(right,top,  self.screen_w,bottom-top))   #left rect
        elif self.already_return_NN == False:  #nn is still runing 
            painter = QtGui.QPainter(self)
            painter.setOpacity(0.4)
            painter.setBrush(QtCore.Qt.black) 
            x,y,w,h = self.screenShot_pos
            painter.drawRect(QtCore.QRect(x,y,w,h))
            #    
        elif  self.enable_data_paint:   #already return NN
            # self.enable_data_paint = False
            if len(self.return_dict.values()[0]['boxes']) == 0:
                return 
            painter = QtGui.QPainter(self)
            painter.setOpacity(0.3)
            x,y,w,h = self.screenShot_pos
            for idx, box in enumerate(self.return_dict.values()[0]['boxes']):
                box = box.astype(int).tolist()
                tl,tr,br,bl = box[0],box[1],box[2],box[3]
                if idx in self.haveoverlaplist:
                    painter.setBrush(QtGui.QColor(200,105,150)) 
                else:
                    painter.setBrush(QtGui.QColor(150,155,150)) 
                painter.drawRect(QtCore.QRect(x+tl[0],y+tl[1],br[0]-tl[0],br[1]-tl[1]))
                self.update()
            
    def mousePressEvent(self, event):
        if self.select_screenshot:
            self.is_draw=True
            self.closeButton.hide();self.EnButton.hide(); self.ChButton.hide(); self.JpButton.hide(); self.ZhButton.hide();self.hint_label.hide()
            self.begin = event.pos()
            self.end = event.pos()
            self.update()
        else: 
            # self.selecting_text = True
            self.begin = event.pos()
            self.end = event.pos()
            self.update()
            self.copybtn.hide()
    def mouseMoveEvent(self, event):
        if self.select_screenshot:
            self.end = event.pos()
            self.update()    
        else:
            self.end = event.pos()
            self.haveoverlaplist = [] 
            x,y,w,h = self.screenShot_pos
            for idx, box in enumerate(self.return_dict.values()[0]['boxes']):
                box = box.astype(int).tolist()
                tl,tr,br,bl = box[0],box[1],box[2],box[3]
                left, right, top , bottom  = getlrtb(self.begin,self.end)
                if do_overlap(left, right, top , bottom,x+tl[0],x+br[0],y+tl[1],y+br[1]):
                    self.haveoverlaplist.append(idx)
            self.update()
    def mouseReleaseEvent(self, event):
        if self.select_screenshot:
            self.closeButton.show(); self.hint_label.show()
            self.is_draw=False
            left, right, top , bottom  = getlrtb(self.begin,self.end)
            # print(left, right, top , bottom )
            self.saveScreenShot(x=left,y=top,w=right-left,h=bottom-top)
            self.begin = event.pos()
            self.end = event.pos()
            self.update()
            self.select_screenshot = False
            self.q.put({'type':"run"}) 
            # th.join()  #we dont wait now
        else:
            # self.selecting_text = False
            self.end = event.pos()
            
            self.copybtn.setText("copy")
            self.copybtn.setGeometry(QtCore.QRect(self.end.x(), self.end.y(), 50, 30))

            self.haveoverlaplist = [] 

            x,y,w,h = self.screenShot_pos
            for idx, box in enumerate(self.return_dict.values()[0]['boxes']):
                box = box.astype(int).tolist()
                tl,tr,br,bl = box[0],box[1],box[2],box[3]
                left, right, top , bottom  = getlrtb(self.begin,self.end)
                # print(left,right,top,bottom,do_overlap(left, right, top , bottom,x+tl[0],x+br[0],y+tl[1],y+br[1]))
                if do_overlap(left, right, top , bottom,x+tl[0],x+br[0],y+tl[1],y+br[1]):
                    self.haveoverlaplist.append(idx)
            if len(self.haveoverlaplist) > 0:
                self.copybtn.show()
            self.update()
    def saveScreenShot(self,x,y,w,h):
        self.screenShot_pos = (x,y,w,h)
        preview_screen =  QApplication.primaryScreen().grabWindow(0,x,y,w,h)
        #https://stackoverflow.com/questions/25056754/how-to-grab-a-desktop-screenshot-with-pyqt
        preview_screen.save(self.img_path, 'jpg')

def window():
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    screen_w, screen_h = size.width(),size.height()
    win = MyWindow(screen_w,screen_h)   # Create the main window
    # Run the application
    win.show()

    app.exec_()
window()