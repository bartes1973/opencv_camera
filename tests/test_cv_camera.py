
from opencv_camera import CameraCalibration
from opencv_camera import Markers
from opencv_camera import FlipBook
from opencv_camera import UnDistort
from opencv_camera import SaveVideo
from glob import glob
import opencv_camera
import slurm
import cv2
import pathlib
from slurm.files import rm

def get():
    imgs = []
    search = 'cal_images/*.jpg'
    base = pathlib.Path(__file__).parent.absolute()
    path = f"{base}/{search}"
    cal = glob(path)
    for i in cal:
        im = cv2.imread(i,0)
        imgs.append(im)

    print(f">> Found {len(imgs)} images")
    return imgs

def test_info():
    print("")
    print(f">> opencv_camera version: {opencv_camera.__version__}")
    print(f">> cv2 version: {cv2.__version__}")
    print(f">> slurm version: {slurm.__version__}")

    assert True


"""
https://kushalvyas.github.io/calib.html
Opencv cv2.calibrateCamera() function Camera Matrix:
[
    [532.79536563, 0, 342.4582516],
    [0, 532.91928339, 233.90060514],
    [0, 0, 1]
]
"""
def test_checkerboard_calibrate():
    print("")
    imgs = get()

    cal = CameraCalibration(Markers.checkerboard, marker_size=(9, 6))
    data = cal.calibrate(imgs)
    assert (data['rms'] - 0.5882563398961391) < 1e-6

    print("camera matrix\n",data["cameraMatrix"],"\n")
    print("distortion coeff:",data["distCoeffs"],"\n")
    print("rms error:",data["rms"],"\n")

    # fb = FlipBook(cal.save_cal_imgs)
    # fb.run()
    #
    # cimgs=[]
    # d = UnDistort(data["distCoeffs"], data["cameraMatrix"])
    # for i in imgs:
    #     im = d.undistort(i)
    #     cimgs.append(im)
    #
    # fb = FlipBook(cimgs)
    # fb.run()

def test_save():
    print("")
    imgs = get()
    h,w = imgs[0].shape[:2]
    mpeg = SaveVideo()
    mpeg.open("single.mp4",w,h,fps=1)
    for i in imgs:
        mpeg.write(i)
    mpeg.close()

    mpeg.write_list(imgs,fps=1, fname="batch.mp4")

    rm("batch.mp4")
    rm("single.mp4")

    assert True
