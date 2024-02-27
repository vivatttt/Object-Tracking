import cv2 
import os
from pathlib import Path
import numpy as np



def r_resize(shot, percent):
    height = shot.shape[0] * percent // 100
    width = shot.shape[1] * percent // 100

    return cv2.resize(shot, (width, height))


def filter_contours(contours, min_area):
 
    rects = []
    for con in contours:
        area = cv2.contourArea(con)
        if area > min_area:
            rects.append(cv2.boundingRect(con))
    
    if not rects:
        return []
    i = 0
    # прямоугольник полностью находится внутри другого
    while i < len(rects):
        j = 0
        while j < len(rects):
            
            x1, y1, w1, h1 = rects[i]
            x2, y2, w2, h2 = rects[j]
            if (x1 < x2 and x2 + w2 < x1 + w1) and (y1 < y2 and y2 + h2 < y1 + h1):
              
                del rects[j]
                if j <= i:
                    i -= 1
            else:
                j += 1
        i += 1
    
    if len(rects) < 2:
        return rects
    
    # прямоугольник частично находится внутри другого

    # i = 0
    # while i < len(rects):
    #     j = 0
    #     
    #     while j < len(rects):

    #         if i == j:
    #             j += 1
    #             continue

    #         x1, y1, w1, h1 = rects[i]
    #         x5, y5, w2, h2 = rects[j]

    #         x2, y2 = x1, y1 + h1
    #         x3, y3 = x1 + w1, y1
    #         x4, y4 = x1 + w1, y1 + h1

    #         x6, y6 = x5, y5 + h2
    #         x7, y7 = x5 + w2, y5
    #         x8, y8 = x5 + w2, y5 + h2

    #         first_rect = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    #         second_rect = [(x5, y5), (x6, y6), (x7, y7), (x8, y8)]

    #         # 1 .-----. 3  5 .-----. 7
    #         #   |     |      |     |
    #         #   |     |      |     |
    #         # 2 ._____. 4  6 ._____ 8

    #         # если хотя бы одна точка находится в области другого прямоугольника, они пересекаются
    #         flag = 0
    #         for (x, y) in first_rect:
    #             if x5 <= x and x <= x5 + w2 and y5 <= y and y <= y5 + h2:
    #                 flag = 1
    #                 break
    #         for (x, y) in second_rect:
    #             if x1 <= x and x <= x1 + w1 and y1 <= y and y <= y1 + h1:
    #                 flag = 1
    #                 break
    #         if flag:
    #             x = min(x1, x5)
    #             y = min(y1, y5)
    #             w = max(x1 + w1, x5 + w2) - min(x1, x5)
    #             h = max(y1 + h1, y5 + h2) - min(y1, y5)
    #             if j <= i:
    #                 i -= 1
    #             del rects[j]
    #             rects[i] = (x, y, w, h)
    #             j = 0
                                            
    #         else:
    #             j += 1
    #     i += 1
    

    merges = 1 # кол-во сделанных замен
               # это нужно, так как иногда смердженные прямоугольники пересекаются с другими, те мы должны объединять их до тех пор пока кол-во замен не станет равным нулю
               # вместо того, чтобы удалять элементы на ходу, будем добавлять нули на место одного из квадратов, которые склеили
    while merges != 0:
        merges = 0
        for i in range(len(rects)):
            for j in range(len(rects)):
                if rects[i] == 0:
                    break
                if rects[j] != 0 and i != j:
                    
                    
                    x1, y1, w1, h1 = rects[i]
                    x5, y5, w2, h2 = rects[j]

                    x2, y2 = x1, y1 + h1
                    x3, y3 = x1 + w1, y1
                    x4, y4 = x1 + w1, y1 + h1

                    x6, y6 = x5, y5 + h2
                    x7, y7 = x5 + w2, y5
                    x8, y8 = x5 + w2, y5 + h2

                    first_rect = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
                    second_rect = [(x5, y5), (x6, y6), (x7, y7), (x8, y8)]

                    # 1 .-----. 3  5 .-----. 7
                    #   |     |      |     |
                    #   |     |      |     |
                    # 2 ._____. 4  6 ._____ 8

                    # если хотя бы одна точка находится в области другого прямоугольника, они пересекаются
                    
                    flag = 0
                    for (x, y) in first_rect:
                        if x5 <= x and x <= x5 + w2 and y5 <= y and y <= y5 + h2:
                            flag = 1
                            break
                    for (x, y) in second_rect:
                        if x1 <= x and x <= x1 + w1 and y1 <= y and y <= y1 + h1:
                            flag = 1
                            break
                    if flag:
                        x = min(x1, x5)
                        y = min(y1, y5)
                        w = max(x1 + w1, x5 + w2) - min(x1, x5)
                        h = max(y1 + h1, y5 + h2) - min(y1, y5)
            
                        rects[i] = (x, y, w, h)
                        rects[j] = 0
                        merges += 1
    # удаляем нули из полученного массива                                         
    d = 0
    while d != len(rects):
        if not rects[d]:
            del rects[d]
        else:
            d += 1

    return rects
                

def main():
    video_name = 'traffic5.mp4'
    percent = 100

    dirname = os.path.dirname(__file__)
    video = os.path.join(dirname, str(Path('videos', video_name)))
  
    cap = cv2.VideoCapture(video)
    object_detector = cv2.createBackgroundSubtractorMOG2()
    
    ret, frame = cap.read()

    # cap.set(3, 640)
    # cap.set(4, 480)


    r = cv2.selectROI("select the area", r_resize(frame, percent))
    r = list(map(lambda el: int(el * 100 // percent), r))
    cv2.destroyWindow("select the area")  
  
    while True:
        
        ret, frame = cap.read()

        if not ret:
            break

        frame_copy = frame.copy()

        cropped = frame[int(r[1]):int(r[1])+int(r[3]),int(r[0]):int(r[0])+int(r[2])]

        


        cropped_copy = cropped.copy()

        mask = object_detector.apply(cropped)
        cv2.imshow("mask", r_resize(mask, percent))
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY) # функция, убирающая все серые области

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
       
        cv2.imshow("mask1", r_resize(mask, percent))
        contours, hir = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        eps = 10
        # for i, con in enumerate(contours):
        #     if hir[0][i][3] == -1:
        #         cv2.drawContours(frame_copy, [con], -1, (0, 255, 0), 2)
        # cv2.imshow("default contours", r_resize(frame_copy, percent))
        
        for con in contours:
            #approx = cv2.approxPolyDP(con, eps, closed=True)
            cv2.drawContours(cropped_copy, [con], -1, (0, 255, 0), 2)
        cv2.imshow("approx contours", r_resize(cropped_copy, percent))


        # for con in contours:
        #     #approx = cv2.approxPolyDP(con, eps, closed=True)
        #     approx = con
        #     area = cv2.contourArea(approx)
        #     if area > 1000:
        #         x, y, w, h = cv2.boundingRect(approx)
        #         cv2.rectangle(cropped, (x, y), (x + w, y + h), (0, 0, 255), 3)
        # cv2.imshow("default video", r_resize(frame, percent))


        rects = filter_contours(contours, min_area=1000)
        for rect in rects:
            x, y, w, h = rect
            cv2.rectangle(cropped, (x, y), (x + w, y + h), (255, 0, 255), 3)

        
        cv2.imshow("filtered video", r_resize(frame, percent))

        if (cv2.waitKey(30) & 0xFF == ord('q')):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()