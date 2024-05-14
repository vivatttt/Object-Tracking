import cv2

def filter_contours(contours, min_area, eps=0):
 
    rects = []
    for con in contours:
        con = cv2.approxPolyDP(con, eps, closed=True)
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
                