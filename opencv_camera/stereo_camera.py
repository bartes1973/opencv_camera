import cv2
import numpy as np


class Stereo2PointCloud:
    def __init__(self, baseline, focalLength, h, w):
        self.baseline = baseline
        self.f = focalLength
        self.w = w
        self.h = h

    def to_pc(self, imgL, imgR):
        ch = 3 # channels
        window_size = 5 # SADWindowSize
        min_disp = 16*0
        num_disp = 16*4-min_disp
#         stereo = cv2.StereoBM_create(numDisparities=96, blockSize=5)
#         stereo = cv2.StereoSGBM_create(0,64,21)
        stereo = cv2.StereoSGBM_create(
            minDisparity = min_disp,
            numDisparities = num_disp,
            blockSize = 16,          # 3-11
            P1 = 8*ch*window_size**2,
            P2 = 32*ch*window_size**2,
            disp12MaxDiff = 1,
            uniquenessRatio = 10,    # 5-15
            speckleWindowSize = 100, # 50-200
            speckleRange = 32         # 1-2
        )

        disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0
#         disp = stereo.compute(imgR, imgL).astype(np.float32) / 16.0 # <<<<<<<<
        dm = (disp-min_disp)/num_disp

        print(f">> Computed disparity, {disp.shape} pts")
        print(f">> Disparity max: {disp.max()}, min: {disp.min()}")
        return disp, dm

    def reproject(self, img, disp):
        if len(img.shape) == 2:
            colors = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            colors = img

        t = self.baseline
        f = self.f
        Q = np.float32([[1, 0, 0, -0.5*w],
                        [0, 1, 0, -0.5*h],
                        [0, 0, 0,      f],
                        [0, 0,-1/t,    0]])
        print(Q)

        points = cv2.reprojectImageTo3D(disp, Q)
#         mask = disp > disp.min()  # find pts with min depth
#         mask = disp > 1

        points = points.reshape(-1, 3)
        colors = colors.reshape(-1, 3)
        disp = disp.reshape(-1)

        print(colors.shape, points.shape, disp.shape)

        mask = (
            (disp > disp.min()) &
            np.all(~np.isnan(points), axis=1) &
            np.all(~np.isinf(points), axis=1)
        )

        out_points = points[mask] # remove pts with no depth
        out_colors = colors[mask] # remove pts with no depth

        print(f'>> Generated 3d point cloud, {out_points.shape}')
        print(f">> out_points {out_points.max()}, {out_points.min()}")

        return out_points, out_colors
