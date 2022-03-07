import cv2
import numpy as np
import glob
import os
from numpy import mat


def camera_calibration(imgs_path_in, imgs_path_out):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Get corner point position of the chessboard
    objp = np.zeros((6*7, 3), np.float32)
    objp[:, :2] = np.mgrid[0:7, 0:6].T.reshape(-1,2)

    obj_points = []  # for 3D points coordinates
    img_points = []  # for 2D points coordinates

    images = glob.glob(os.path.join(imgs_path_in, '*.jpg'))
    i = 0
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        size = gray.shape[::-1]
        ret, corners = cv2.findChessboardCorners(gray, (7, 6), None)

        if ret:
            obj_points.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
            if [corners2]:
                img_points.append(corners2)
            else:
                img_points.append(corners)

            cv2.drawChessboardCorners(img, (7, 6), corners, ret)
            i += 1
            cv2.imwrite(os.path.join(imgs_path_out, 'conimg'+str(i)+'.jpg'), img)
            cv2.waitKey(4000)

    print(len(img_points))
    cv2.destroyAllWindows()

    # Camera Calibration
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, size, None, None)

    print("ret:", ret)
    print("mtx:\n", mtx)  # Intrinsic matrix of the camera
    print("dist:\n", dist)  # Distortion cofficients = (k_1,k_2,p_1,p_2,k_3) of the camera
    print("rvecs:\n", rvecs)  # Rotation matrix
    print("tvecs:\n", tvecs)  # Translation vector

    print("-----------------------------------------------------")

    img = cv2.imread(images[2])
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    print (newcameramtx)
    print("------------------Use undistort function-------------------")
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
    x, y, w, h = roi
    dst1 = dst[y:y+h, x:x+w]
    cv2.imwrite('calibresult.jpg', dst1)
    print("dst shape:", dst1.shape)

    return mtx, dist


# From 2D to 3D coordinates
def get_world_coordinate(img_coordinate, R_mtx, tvec, mtx):
    img_coordinate = list(img_coordinate) + [1]
    s = (mat(R_mtx).I * tvec)[2] / (mat(R_mtx).I * mat(mtx).I * mat(img_coordinate).T)[2]
    wcpoint = mat(R_mtx).I * (s[0, 0] * mat(mtx).I * mat(img_coordinate).T - tvec)
    return wcpoint.flatten().getA()[0]


def get_img_coordinate(world_coordinate, rvec, tvec, mtx, dist):
    img_coordinate, jacob = cv2.projectPoints(world_coordinate, rvec, tvec, mtx, dist)
    return img_coordinate


if __name__ == "__main__":
    # Get camera intrinsic parameters from camera calibration
    mtx, dist = camera_calibration(imgs_path_in=r'images_for_calibration\calibration_imgs_in',
                                   imgs_path_out=r'images_for_calibration\calibration_imgs_out')

    # Get rvec and tvec from SolvePnP
    world_coordinates = np.array([
        [0, 0, 0],  # Left bottom corner marker
        [570, 0, 0],  # right bottom corner marker
        [570, 715, 0],  # right top corner marker
        [0, 715, 0],  # left top corner marker
    ]).astype(np.float32)

    img_coordinates = np.array([
        [383, 663],  # Left bottom corner marker
        [860, 658],  # right bottom corner marker
        [770, 561],  # right top corner marker
        [495, 565]  # left top corner marker
    ]).astype(np.float32)

    ret, rvec, tvec = cv2.solvePnP(world_coordinates, img_coordinates, mtx, dist)

    # Convert rotation vector to rotation matrix
    R_mtx, jacob = cv2.Rodrigues(rvec)

    # Get flag world coordinates from image coordinates
    # 646 is the pixel of the width of the object
    # 546 is the pixel of the height of the obect
    # the origin of the image coordinate system is top left corner of the image
    flag_img_coordinate = (646, 546)
    flag_world_coordinate_estimated = get_world_coordinate(flag_img_coordinate, R_mtx, tvec, mtx)

    # Get flag image coordinates from world coordinates
    # 300 is the x axis of the object in mm
    # 975 is the y axis of the object in mm
    # the origin of the world coordinate system is definded by the user
    flag_world_coordinate = np.array([300, 975, 0], dtype=np.float32)
    flag_img_coordinate_estimated = get_img_coordinate(flag_world_coordinate, rvec, tvec, mtx, dist)

    # Test the error of the conversion
    print("------------------------------------------")
    print("Flag real world coordinate: ", flag_world_coordinate)
    print("Flag estimated world coordinate: ", flag_world_coordinate_estimated)
    print("Mismatch: ", abs(flag_world_coordinate-flag_world_coordinate_estimated))
    print("------------------------------------------")
    print("Flag real image coordinate: ", flag_img_coordinate)
    print("Flag estimated image coordinate: ", flag_img_coordinate_estimated)
    print("Mismatch: ", abs(flag_img_coordinate-flag_img_coordinate_estimated))
