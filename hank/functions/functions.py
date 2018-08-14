import cv2
import numpy as np
import pandas as pd




def Inhence_and_threshod(img):


    # Contrast Limited Adaptive Histogram Equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(14, 14))
    cl = clahe.apply(img)

    # lowpass filter
    gaussian = cv2.GaussianBlur(cl, (5, 5), 1)

    # THRESH
    __, th = cv2.threshold(cl, 0, 255, cv2.THRESH_BINARY++ cv2.THRESH_OTSU)

    return th




def inner_fill(th):
    # 接滿
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 1))
    mor = cv2.dilate(th, kernel)


    # floodfill external's area
    image1, contours, hierarchy = cv2.findContours(
        mor, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(mor, contours, -1, (255, 255, 255), thickness=cv2.FILLED)

    # erode
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mor = cv2.erode(mor, kernel)

    #opening
    mor = cv2.morphologyEx(mor, cv2.MORPH_OPEN, kernel)



    return mor



def draw(contours,img_color):


    # bone ROI
    for i in range(0, len(contours)):


        area = cv2.contourArea(contours[i])
        x, y, w, h = cv2.boundingRect(contours[i])
        aspect_ratio = float(w) / h
        rect_area = w * h
        extent = float(area) / rect_area


        #delete error area
        if area>120:
           cv2.drawContours(img_color, [contours[i]], -1, (0, 0, 255), 1)



    #  bone number
    # find 4 end points  and
    centroid_x = []
    centroid_y = []
    num_roi = 0  # the num of effective bone's 4 end points
    df = pd.DataFrame()
    for cnt in contours:
        #area and approx
        area = cv2.contourArea(cnt)
        approx = cv2.approxPolyDP(cnt, 8, True)
        # centroid
        M = cv2.moments(cnt)
        if M['m00']==0 :
            continue
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        centroid_x = np.append(centroid_x, cx)
        centroid_y = np.append(centroid_y, cy)


        # get data  for pd
        if area>120 and np.shape(approx)[0]==4:
         cv2.putText(img_color, str(num_roi+1), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
         num_roi += 1

         #get all the contours's points
         mask=np.zeros(img_color.shape,np.uint8)
         cv2.drawContours(mask,[cnt],0,255,thickness=cv2.FILLED)
         contourPoints=np.transpose(np.nonzero(mask))
         y = np.reshape(contourPoints[:, 0], (len(contourPoints[:, 0]), 1))
         x = np.reshape(contourPoints[:, 1], (len(contourPoints[:, 1]), 1))
         index = np.full(x.shape, num_roi)

         pixelpoints = np.hstack((index,x,y))
         df_points = pd.DataFrame(pixelpoints,columns=['index','x', 'y'])
         df=df.append(df_points)

         # get all the end points
         for i in range(np.shape(approx)[0]):
             cv2.circle(img_color, (approx[i][0][0], approx[i][0][1]), 1, [0, 255, 0], 2)



    print("找到%d個有效椎骨的座標"%num_roi)
    print(df)
    df.to_csv("coordinate_forAllContours_points.csv")




