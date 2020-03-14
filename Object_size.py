from scipy.spatial import distance as dis
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
def midpoint(ptA,ptB):
    return ((ptA[0]+ptB[0])*0.5, (ptA[1]+ptB[1]*0.5))

# contruct the argument parse and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-i","--image", required= True,
                help= "path to the input image")
ap.add_argument("-w","--width", type= float, required=True,
                help="width of the left-most object in the image in inches")
args = vars(ap.parse_args())
# load image, convert it to grayscale, and blur it slightly

image = cv2.imread(args["image"])
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray,(7,7),0)

# perform edge detection, then perform a dilation + erosion to close gaps in between object edges

edged = cv2.Canny(gray,50,100)
cv2.imshow("view1",edged)
edged = cv2.dilate(edged,None,iterations=1)
edged = cv2.erode(edged,None,iterations=1)
cv2.imshow("view",edged)

# find contours in the edge map

cnts = cv2.findContours(edged.copy(),cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# sort the contours from left to right and initialize the pixel per metric calibration variable

(cnts,_) = contours.sort_contours(cnts)
pixelsPerMetric = None

# loop over the contours individually

for c in cnts:
    # if the contour is not sufficiently range , ignore it
    if cv2.contourArea(c)<100:
        continue
    # compute the rotaed bounding box of the contours
    orig = image.copy()
    box = cv2.minAreaRect(c)
    box = cv2.boxPoints(box)
    box = np.array(box, dtype = "int")
    print(box)
    # order the points in the contour such that they apper
    # in top-left, top-right, bottom-right, bottom-left order,
    # then draw the outline of the rotated bounding box

    box = perspective.order_points(box)
    cv2.drawContours(orig,[box.astype("int")], -1,(0,255,0),2)
    #loop over the original points and draw them

    for(x,y) in box:
        cv2.circle(orig,(int(x),int(y)),3,(0,100,255),-1)

    # unpack the ordered bouding box, then compute the midpoint
    # between the top-left and top-right coordinates, followed by
    # the midpoint between bottom-left and bottom-right

    (tl,tr,br,bl) = box
    (tltrX,tltrY) = midpoint(tl,tr)
    (blbrX,blbrY) = midpoint(bl,br)

    (tlblX,tlblY) = midpoint(tl,bl)
    (trbrX,trbrY) = midpoint(tr,br)

    # draw the midpoint in the image

    cv2.circle(orig,(int(tltrX),int(tltrY)),5,(255,0,0),-1)
    cv2.circle(orig,(int(blbrX),int(blbrY)),5,(255,0,0),-1)
    cv2.circle(orig,(int(tlblX),int(tlblY)),5,(255,0,0),-1)
    cv2.circle(orig,(int(trbrX),int(trbrY)),5,(255,0,0),-1)

    # draw the lines between the midpoints

    cv2.line(orig,(int(tltrX),int(tltrY)),(int(blbrX),int(blbrY)),(255,0,255),2)
    cv2.line(orig,(int(tlblX),int(tlblY)),(int(trbrX),int(trbrY)),(255,0,255),2)

    # compute the Euclidean distance between the midpoints

    dA = dis.euclidean((tltrX,tltrY),(blbrX,blbrY))
    dB = dis.euclidean((tlblX,tlblY),(trbrX,trbrY))

    # if the pixels per metric has not been initialized, then compute
    # it as the ratio of pizels to supplied metric (in this case, inches)

    if pixelsPerMetric is None:
        pixelsPerMetric = dB / args["width"]

    #compute the size of the object

    dimA = dA / pixelsPerMetric
    dimB = dB / pixelsPerMetric

    # draw the object sizes on the image

    cv2.putText(orig,"{:.1f}in".format(dimA),(int(tltrX-15),int(tltrY-10)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
    cv2.putText(orig,"{:.1f}in".format(dimB),(int(trbrX+15),int(trbrY)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
    # show the image

    cv2.imshow("image",orig)
    cv2.waitKey(0)
