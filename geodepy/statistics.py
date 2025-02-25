#!/usr/bin/env python3

from math import radians, sin, cos, sqrt, atan2, degrees
import numpy as np


def rotation_matrix(lat, lon):
    """Returns the 3x3 rotation matrix for a given latitude and longitude
    (given in decimal degrees)
    See Section 4.2.3 of the DynaNet User's Guide v3.3
    """
    (rlat, rlon) = (radians(lat), radians(lon))
    rot_matrix = np.array(
        [[-sin(rlon), -sin(rlat) * cos(rlon), cos(rlat) * cos(rlon)],
         [cos(rlon), -sin(rlat) * sin(rlon), cos(rlat) * sin(rlon)],
         [0.0, cos(rlat), sin(rlat)]]
    )
    return rot_matrix


def vcv_cart2local(vcv_cart, lat, lon):
    """Transform a 3x3 VCV from the Cartesian to the local reference frame. If
    only a column vector of variances is supplied (3x1) then the full VCV is
    padded out with zeros for the transformation. In these cases, only the
    column vector of variances (3x1) is returned.

    See Section 4.4.1 of the DynaNet User's Guide v3.3
    """
    if vcv_cart.shape[0] == 3:
        if vcv_cart.shape[1] == 1:
            vcv_cart = np.array([[vcv_cart[0,0], 0.0, 0.0],
                                 [0.0, vcv_cart[1,0], 0.0],
                                 [0.0, 0.0, vcv_cart[2,0]]])
        elif vcv_cart.shape[1] == 3:
            pass
        else:
            sys.exit('Matrix must be either 3x1 or 3x3')
    else:
         sys.exit('Matrix must be either 3x1 or 3x3')
    rot_matrix = rotation_matrix(lat, lon)
    vcv_local = rot_matrix.transpose() @ vcv_cart @ rot_matrix
    return vcv_local


def vcv_local2cart(vcv_local, lat, lon):
    """Transform a 3x3 VCV from the local to the Cartesian reference frame. If
    only a column vector of variances is supplied (3x1) then the full VCV is
    padded out with zeros for the transformation. In these cases, only the
    column vector of variances (3x1) is returned.

    See Section 4.4.1 of the DynaNet User's Guide v3.3
    """
    if vcv_local.shape[0] == 3:
        if vcv_local.shape[1] == 1:
            vcv_local = np.array([[vcv_local[0, 0], 0.0, 0.0],
                                 [0.0, vcv_local[1, 0], 0.0],
                                 [0.0, 0.0, vcv_local[2, 0]]])
        elif vcv_local.shape[1] == 3:
            pass
        else:
            sys.exit('Matrix must be either 3x1 or 3x3')
    else:
        sys.exit('Matrix must be either 3x1 or 3x3')
    rot_matrix = rotation_matrix(lat, lon)
    vcv_cart = rot_matrix @ vcv_local @ rot_matrix.transpose()
    return vcv_cart


def error_ellipse(vcv):
    """Calculate the semi-major axis, semi-minor axis, and the orientation of
    the error ellipse calculated from a 3x3 VCV
    See Section 7.3.3.1 of the DynaNet User's Guide v3.3
    """
    z = sqrt((vcv[0, 0] - vcv[1, 1])**2 + 4 * vcv[0, 1]**2)
    a = sqrt(0.5 * (vcv[0, 0] + vcv[1, 1] + z))
    b = sqrt(0.5 * (vcv[0, 0] + vcv[1, 1] - z))
    orientation = 90 - degrees(0.5 * atan2((2 * vcv[0, 1]),
                                           (vcv[0, 0] - vcv[1, 1])))

    return a, b, orientation


def circ_hz_pu(a, b):
    """Calculate the circularised horizontal PU form the semi-major and
    semi-minor axes
    """
    q0 = 1.960790
    q1 = 0.004071
    q2 = 0.114276
    q3 = 0.371625
    c = b / a
    k = q0 + q1 * c + q2 * c**2 + q3 * c**3
    r = a * k

    return r


def k_val95(dof):
    """
    Returns the Coverage Factor k for a given 1 sigma (68.27%) Standard
    Deviation to allow conversion to a 95% Standard Deviation. This
    uses a simplified table of k values rounded to 5 decimal places
    for Degrees of Freedom (DOF) in the range 1 to 120. For DOF above
    120, returns k value of 1.96 and for DOF below 1, returns k value
    for DOF = 1. Coverage Factor produced using following scipy stats
    code: stats.t.ppf(1-0.025,dof)
    :param dof: Degrees of Freedom (Number of Measurements Minus 1)
    :return: Coverage Factor k
    """
    if not isinstance(dof, int):
        raise TypeError('Degrees of Freedom must be Int')
    if dof < 1:
        return ttable_p95[0]
    elif dof > 120:
        return 1.96
    else:
        return ttable_p95[dof - 1]


ttable_p95 = ([12.7062, 4.30265, 3.18245, 2.77645, 2.57058, 2.44691,
              2.36462, 2.30600, 2.26216, 2.22814, 2.20099, 2.17881,
              2.16037, 2.14479, 2.13145, 2.11991, 2.10982, 2.10092,
              2.09302, 2.08596, 2.07961, 2.07387, 2.06866, 2.06390,
              2.05954, 2.05553, 2.05183, 2.04841, 2.04523, 2.04227,
              2.03951, 2.03693, 2.03452, 2.03224, 2.03011, 2.02809,
              2.02619, 2.02439, 2.02269, 2.02108, 2.01954, 2.01808,
              2.01669, 2.01537, 2.01410, 2.01290, 2.01174, 2.01063,
              2.00958, 2.00856, 2.00758, 2.00665, 2.00575, 2.00488,
              2.00404, 2.00324, 2.00247, 2.00172, 2.00100, 2.00030,
              1.99962, 1.99897, 1.99834, 1.99773, 1.99714, 1.99656,
              1.99601, 1.99547, 1.99495, 1.99444, 1.99394, 1.99346,
              1.99300, 1.99254, 1.99210, 1.99167, 1.99125, 1.99085,
              1.99045, 1.99006, 1.98969, 1.98932, 1.98896, 1.98861,
              1.98827, 1.98793, 1.98761, 1.98729, 1.98698, 1.98667,
              1.98638, 1.98609, 1.98580, 1.98552, 1.98525, 1.98498,
              1.98472, 1.98447, 1.98422, 1.98397, 1.98373, 1.98350,
              1.98326, 1.98304, 1.98282, 1.98260, 1.98238, 1.98217,
              1.98197, 1.98177, 1.98157, 1.98137, 1.98118, 1.98099,
              1.98081, 1.98063, 1.98045, 1.98027, 1.98010, 1.97993])
