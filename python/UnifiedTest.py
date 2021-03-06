import numpy as np
import math
import random
import RayTracer2
import surface
import matplotlib.pyplot as plt
import sys

# Check retroreflection in UnifiedReflectorModel with a retroreflecting panel covered in a hemisphere (for collecting
# distribution). Fire light straight down onto the center of the panel and observe distribution on hemisphere.


def main():
    surface_list = []

    # hemisphere
    hemi = surface.surface()
    hemi.description = '10cm radius hemisphere, in positive z'
    hemi.shape = 'sphere'
    hemi.param_list = [np.array([0, 0, 0]), 10]
    hemi.inbounds_function = lambda p: np.reshape((p[:, 2, :] >= 0) * (p[:, 2, :] <= 10), (p.shape[0], -1))
    hemi.n_outside = np.inf
    hemi.n_inside = 1.5
    hemi.surface_type = 'normal'
    hemi.absorption = 1
    surface_list.append(hemi)

    # panel
    panel = surface.surface()
    panel.description = 'retroreflecting panel cut to 10cm radius disk on xy-plane'
    panel.shape = 'plane'
    panel.param_list = [np.array([0, 0, 0]), np.array([0, 0, 1])]
    panel.inbounds_function = lambda p: np.reshape((p[:, 0] ** 2 + p[:, 1] ** 2) < 100, (p.shape[0], -1))
    panel.n_outside = 1.5
    panel.n_inside = np.inf
    panel.surface_type = 'unified'
    panel.unifiedparams = [0, 0, 0, 0, 0]
    panel.absorption = 0
    surface_list.append(panel)

    # construct light rays
    # start them along z-axis, pointing down
    x = 0
    y = 0
    z = 5

    n = 10000  # number of rays

    ray_startpoints = np.empty((n, 3))
    ray_startpoints[..., 0] = x
    ray_startpoints[..., 1] = y
    ray_startpoints[..., 2] = z

    # rays = initial [forward direction (3), s1 polarization axis (3), s0, s1, s2, s3]
    # Let s0 be 1 and rays be unpolarized (other Stokes parameters = 0 + no polarization axis)
    test_rays = np.zeros((n, 10))
    test_rays[..., 3] = 1
    test_rays[..., 6] = 1

    test_rays[:, 0] = 0
    test_rays[:, 1] = 0
    test_rays[:, 2] = -1

    #print(test_rays)

    [ray_interfaces, absorption_table, raytable] = RayTracer2.RayTracer2(ray_startpoints, test_rays, surface_list)

    # print("Points of intersection:")
    # print(ray_interfaces[1].intersection_point)
    # print(ray_interfaces[1].intersection_point.shape)

    # calculate spherical coordinates
    x_int = ray_interfaces[1].intersection_point[:, 0]
    y_int = ray_interfaces[1].intersection_point[:, 1]
    z_int = ray_interfaces[1].intersection_point[:, 2]

    theta = np.arctan((np.sqrt(x_int**2 + y_int**2) / z_int)) # 0 < theta < pi/2
    phi = np.arctan(y_int / x_int) # 0 < phi < 2pi PROBLEM HERE: ARCTAN ONLY FROM -pi/2 --> pi/2
    phi[np.isnan(phi)] = 0

    points = np.concatenate((phi[:,np.newaxis], np.cos(theta)[:,np.newaxis]), axis=1)
    counts = np.equal(points, np.matlib.repmat(np.array([0, 1]), points.shape[0], 1))
    print("# of Rays Perfectly Reflected: " + str(int(np.sum(counts)/2)))

    fig, ax = plt.subplots()
    ax.scatter(phi, np.cos(theta))

    plt.xlim(0, 2 * math.pi)
    plt.ylim(0, 1)

    ax.set_ylabel("cos\u03B8") # theta
    ax.set_xlabel("\u03C6") # phi
    ax.grid(True)

    plt.show()

    # # plot
    # x_data = np.arange(.2, 10, .2)
    # width = 0.05
    # labels = np.arange(.2, 10, .2).round(decimals=1) # fix x-labels
    #
    # fig, ax = plt.subplots()
    #
    # ax.bar(x_data, absorbed_bot, width, label='absorbed bottom')
    # ax.bar(x_data, absorbed_top, width, bottom=absorbed_bot, label='absorbed top')
    # plt.xticks(np.arange(.2, 10, .2), labels, size='small', rotation='vertical')
    #
    # ax.set_ylabel('# of rays absorbed')
    # ax.set_xlabel('z-start')
    # ax.set_title('# of rays absorbed at caps by starting height')
    # ax.legend()
    #
    # plt.show()



if __name__ == "__main__":
    main()

