#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import cv2
import gc

from multiprocessing import Process,Manager


# In[8]:


# Pretrained classes in the model
classNames = {0: 'background',
              1: 'person', 2: 'bicycle', 3: 'car', 4: 'motorcycle', 5: 'airplane', 6: 'bus',
              7: 'train', 8: 'truck', 9: 'boat', 10: 'traffic light', 11: 'fire hydrant',
              13: 'stop sign', 14: 'parking meter', 15: 'bench', 16: 'bird', 17: 'cat',
              18: 'dog', 19: 'horse', 20: 'sheep', 21: 'cow', 22: 'elephant', 23: 'bear',
              24: 'zebra', 25: 'giraffe', 27: 'backpack', 28: 'umbrella', 31: 'handbag',
              32: 'tie', 33: 'suitcase', 34: 'frisbee', 35: 'skis', 36: 'snowboard',
              37: 'sports ball', 38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
              41: 'skateboard', 42: 'surfboard', 43: 'tennis racket', 44: 'bottle',
              46: 'wine glass', 47: 'cup', 48: 'fork', 49: 'knife', 50: 'spoon',
              51: 'bowl', 52: 'banana', 53: 'apple', 54: 'sandwich', 55: 'orange',
              56: 'broccoli', 57: 'carrot', 58: 'hot dog', 59: 'pizza', 60: 'donut',
              61: 'cake', 62: 'chair', 63: 'couch', 64: 'potted plant', 65: 'bed',
              67: 'dining table', 70: 'toilet', 72: 'tv', 73: 'laptop', 74: 'mouse',
              75: 'remote', 76: 'keyboard', 77: 'cell phone', 78: 'microwave', 79: 'oven',
              80: 'toaster', 81: 'sink', 82: 'refrigerator', 84: 'book', 85: 'clock',
              86: 'vase', 87: 'scissors', 88: 'teddy bear', 89: 'hair drier', 90: 'toothbrush'}


def id_class_name(class_id, classes):
    for key, value in classes.items():
        if class_id == key:
            return value


# Loading model
model = cv2.dnn.readNetFromTensorflow('models/frozen_inference_graph.pb',
                                      'models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt')

def write(stack,cam,top:int) -> None:
    '''
    :param cam: camera
    :param stack: Manager.list
    :param top: 缓冲栈的容量
    :reture: None
    '''
    print('Process to write: %s' % os.getpid())
    cap = cv2.VideoCapture(cam)
    while True:
        _,img = cap.read()
        if _:
            stack.append(img)
            
            if len(stack) >= top:
                del stack[:]
                gc.collect()
                
def read(stack) -> None:
    print('Process to read: %s' % os.getpid())
    while True:
        if len(stack) != 0:
            value = stack.pop()
            image_height, image_width, _ = value.shape
            model.setInput(cv2.dnn.blobFromImage(value, size=(300, 300), swapRB=True))#image
            output = model.forward()
            # print(output[0,0,:,:].shape)


            for detection in output[0, 0, :, :]:
                confidence = detection[2]
                if confidence > .5:
                    class_id = detection[1]
                    class_name=id_class_name(class_id,classNames)
                    print(str(str(class_id) + " " + str(detection[2])  + " " + class_name))
                    #'''
                    box_x = detection[3] * image_width
                    box_y = detection[4] * image_height
                    box_width = detection[5] * image_width
                    box_height = detection[6] * image_height
                    if class_id == 1:
                        cv2.rectangle(value,(int(box_x), int(box_y)), (int(box_width), int(box_height)), (0, 255, 0), thickness=5)
                        cv2.putText(value,class_name ,(int(box_x), int(box_y-.005*image_height)),cv2.FONT_HERSHEY_PLAIN,(.003*image_width),(0, 255, 0),6)
                    elif class_id in (3,6,8):
                        cv2.rectangle(value, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (0, 0, 255), thickness=5)
                        cv2.putText(value,class_name ,(int(box_x), int(box_y-.005*image_height)),cv2.FONT_HERSHEY_PLAIN,(.003*image_width),(0, 0, 255),6)
                    elif class_id not in (1,2,6,8):
                        cv2.rectangle(value, (int(box_x), int(box_y)), (int(box_width), int(box_height)), (255, 0, 0), thickness=5)
                        cv2.putText(value,class_name ,(int(box_x), int(box_y-.005*image_height)),cv2.FONT_HERSHEY_PLAIN,(.003*image_width),(255, 0, 0),6)





            cv2.namedWindow('cam1',cv2.WINDOW_NORMAL)
            cv2.imshow('cam1', value)
            if cv2.waitKey(1) & 0xFF==ord('q'):
                break
            # cv2.imwrite("image_box_text.jpg",image)

        #cv2.waitKey(0)
        #cap.release()
        #cv2.destroyAllWindows()
        #'''
            #cv2.imshow('img',value)
            #key = cv2.waitKey(1) & 0xFF
            #if key == ord('q'):
                #break
                
                
if __name__ == '__main__':
    q = Manager().list()
    pw = Process(target=write,args=(q,"rtsp://admin:admin123@192.168.199.67:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif",100))
    pr = Process(target=read,args=(q,))
    
    pw.start()
    pr.start()
    
    pr.join()
    pw.terminate()


# In[ ]:




