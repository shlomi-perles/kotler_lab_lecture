from manim import *
from manim.opengl import *
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
from scipy.special import jv, jn_zeros
from copy import deepcopy

j_zeros = [jn_zeros(m, 20) for m in range(6)]
# DRUM_COLOR = '#B22222	'
DRUM_COLOR = BLUE
OPACITY = 1
# RESOLUTION = [37, 37]


RESOLUTION = [12,12]


def get_bessels_zeroes(m, n):
    return j_zeros[m][n - 1]


class Drum(Surface, metaclass=ConvertToOpenGL):
    def __init__(self, bessel_order, mode, axes, starting_time=0, R=1, boundary_theta=TAU, d_0=0, amplitude=1,
                 resolution=RESOLUTION,
                 checkerboard_colors=[BLUE, BLUE], fill_color=DRUM_COLOR, fill_opacity=OPACITY, stroke_color=BLUE,
                 rotate_angle=0,
                 stroke_opacity=OPACITY, shade_in_3d=True, stroke_width=1,
                 **kwargs):

        self.bessel_order = bessel_order
        self.mode = mode
        self.axes = axes
        self.t = self.start_t = starting_time
        self.R = R
        self.boundary_theta = boundary_theta
        self.amplitude = amplitude
        self.resolution = resolution
        self.stroke_width = stroke_width
        self.d_0 = d_0
        self.bessel2axes = lambda u, v: self.axes.c2p(*self.surface_func(u, v))
        self.rotate_angle = rotate_angle
        self.rotate_axis = Z_AXIS
        self.super_init_dict = dict(u_range=[0, R], v_range=[0, self.boundary_theta],
                                    resolution=self.resolution,
                                    checkerboard_colors=checkerboard_colors, fill_color=fill_color,
                                    fill_opacity=fill_opacity,
                                    stroke_color=stroke_color, stroke_opacity=stroke_opacity,
                                    shade_in_3d=shade_in_3d, stroke_width=stroke_width)
        self.super_init_dict.update(kwargs)

        super().__init__(self.bessel2axes, **self.super_init_dict)
        self.rotate(self.rotate_angle, self.rotate_axis)
        self.opacity_all = 1

    def rotate_drum(self, angle: float, axis: np.ndarray = Z_AXIS, **kwargs):
        self.rotate_angle = angle
        self.rotate_axis = axis
        return self.animate.rotate(self.rotate_angle, axis, **kwargs)

    def surface_func(self, r, theta):
        return np.array([r * np.cos(theta), r * np.sin(theta), self.u_mn(r, theta, self.t)])

    def u_mn(self, r, theta, t=0):
        bessel_zero = get_bessels_zeroes(self.bessel_order, self.mode)
        A = C = D = self.amplitude

        theta_sol = C * np.cos(self.bessel_order * theta + PI / 4) + D * np.sin(self.bessel_order * theta + PI / 4)
        r_sol = jv(self.bessel_order, bessel_zero * r / self.R)
        t_sol = A * np.sin(t)

        return theta_sol * r_sol * t_sol + self.d_0

    def update_drum(self, drum, alpha):
        drum.set_opacity(0)
        if config.renderer == "opengl":
            tmp_loc = np.array([drum.get_x(), drum.get_y(), drum.get_z()])
        else:
            tmp_loc = drum.get_critical_point(ORIGIN)
        tmp_heigh, tmp_width = drum.height, drum.width
        self.t = self.oscillates * TAU * alpha + self.start_t
        super().__init__(self.bessel2axes, **self.super_init_dict)
        if self.rotate_axis is Z_AXIS:
            self.rotate(self.rotate_angle, self.axes.z_normal)
        else:
            self.rotate(self.rotate_angle, self.rotate_axis)
        self.move_to(tmp_loc).stretch_to_fit_height(tmp_heigh).stretch_to_fit_width(tmp_width)
        self.set_opacity(self.opacity_all)
        self.set_stroke(width=self.stroke_width, family=self.stroke_width)
        self.set_stroke(opacity=self.stroke_width, background=True)

    def vibrate(self, oscillates=1):
        self.oscillates = oscillates
        self.start_t = self.t
        return UpdateFromAlphaFunc(self, self.update_drum, rate_func=linear, run_time=3 * oscillates)
