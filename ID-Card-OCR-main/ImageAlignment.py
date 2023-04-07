import numpy as np
import cv2 as cv
import imutils
import math

try:
    import pickle
    with open("models/align_ref.rf", "rb") as infile:
        ref_data = pickle.load(infile)
except Exception as e:
    print('Error : {}'.format(e))


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

rectify = np.vectorize(lambda x: max(0, x))

def align(keypoints, image):
    keypoints = keypoints.astype(int)
    keypoints = rectify(keypoints)
    segemnts_2d = keypoints[:, :2]
    warped = four_point_transform(image, segemnts_2d)

    return warped

def homography_matrix(image, template, maxFeatures=3000, keepPercent=0.2, debug=False):

    orb = cv.ORB_create(maxFeatures)
    (kpsA, descsA) = orb.detectAndCompute(image, None)
    (kpsB, descsB) = orb.detectAndCompute(template, None)

    method = cv.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
    matcher = cv.DescriptorMatcher_create(method)
    matches = matcher.match(descsA, descsB, None)
    
    matches = sorted(matches, key=lambda x: x.distance)

    keep = int(len(matches) * keepPercent)
    matches = matches[:keep]

    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")

    for (i, m) in enumerate(matches):

        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt
        
    (H, mask) = cv.findHomography(ptsA, ptsB, method=cv.RANSAC)
    
#     # Use the homography matrix to align the images
    (h, w) = template.shape[:2]
    angle = math.atan2(H[1,0], H[0,0])
    
    return angle


def Alignment(keypoints, image, labels):

    if labels == 'Non_CNIC': return image

    else:

        template_in = ref_data[labels]

        cropped_image = align(keypoints, image)

        angle_out = homography_matrix(cropped_image,template_in)

        degree = angle_out*(180/(22/7))
        sin_deg = np.sign(degree)

        image = cropped_image.copy()
        rotated = image

        height, width, _ = image.shape

        lower_bound_pos = 60 
        lower_bound_neg = -60
        upper_bound_pos = 130
        if labels=='SNIC Front' or labels=='SNIC Back': upper_bound_neg = -130
        if labels=='CNIC Front' or labels=='CNIC Back': upper_bound_neg = -160
        rev_upper_bound_neg = degree

        counter = 0 

        while((height>width) and counter<3):

            if (degree>lower_bound_pos and degree<upper_bound_pos) or (degree<lower_bound_neg and rev_upper_bound_neg>upper_bound_neg):
                
                if labels in ['SNIC Front', 'SNIC Back']:
                    if sin_deg==1:
                        rotated = imutils.rotate_bound(image, 90)
                    elif sin_deg==-1:
                        rotated = imutils.rotate_bound(image, -90)
                if labels=='CNIC Front':
                    if sin_deg==1 or degree<-150:
                        rotated = imutils.rotate_bound(image, 90)
                    elif sin_deg==-1 and degree>-120:
                        rotated = imutils.rotate_bound(image, -90)
                if labels=='CNIC Back':
                    if sin_deg==1:
                        rotated = imutils.rotate_bound(image, 90)
                    elif sin_deg==-1 and (degree>-120 or degree<-150):
                        rotated = imutils.rotate_bound(image, -90)

            height, width, _ = rotated.shape

            rev_upper_bound_neg = upper_bound_neg + 20 
            counter += 1

        return rotated

