import numpy as np
#from math import cos,sin

def rotationMatrix44(angle_x, angle_y, angle_z):
    """Makes a rotation Matrix44 about 3 axis."""

    cx = np.cos(angle_x)
    sx = np.sin(angle_x)
    cy = np.cos(angle_y)
    sy = np.sin(angle_y)
    cz = np.cos(angle_z)
    sz = np.sin(angle_z)

    sxsy = sx*sy
    cxsy = cx*sy

    # http://web.archive.org/web/20041029003853/http:/www.j3d.org/matrix_faq/matrfaq_latest.html#Q35
    #A = cos(angle_x)
    #B = sin(angle_x)
    #C = cos(angle_y)
    #D = sin(angle_y)
    #E = cos(angle_z)
    #F = sin(angle_z)

#     |  CE      -CF       D   0 |
#M  = |  BDE+AF  -BDF+AE  -BC  0 |
#     | -ADE+BF   ADF+BE   AC  0 |
#     |  0        0        0   1 |

    M = np.array([[cy*cz,  sxsy*cz+cx*sz,  -cxsy*cz+sx*sz, 0.0],
                  [-cy*sz, -sxsy*sz+cx*cz, cxsy*sz+sx*cz,  0.0],
                  [sy,     -sx*cy,         cx*cy,          0.0],
                  [0.,     0.,             0.,             1.0]], 'f')
    return M

def translationMatrix44(x, y, z):
    """Makes a translation Matrix44."""

    M = np.array([[1.,       0.,       0.,       0.],
                  [0.,       1.,       0.,       0.],
                  [0.,       0.,       1.,       0.],
                  [float(x), float(y), float(z), 1.]], 'f')
    return M