from manim import *


class Spring(VGroup):
    def __init__(self, start=ORIGIN, length=2, bumps=6, bump_height=1.5, **kwargs):
        super().__init__(**kwargs)
        self.length = length
        self.empty = 0.13
        self.step = 0.07
        self.bump_height = bump_height
        # super().__init__(color=BLACK)
        vertices = np.array(
            [
                [0, 0, 0],
                [self.empty, 0, 0],
                [self.empty + self.step, self.bump_height, 0],
                *[
                    [
                        self.empty + self.step + self.step * 2 * i,
                        self.bump_height * (1 - (i % 2) * 2),
                        0,
                    ]
                    for i in range(1, bumps)
                ],
                [self.empty + self.step * 2 * bumps, 0, 0],
                [self.empty * 2 + self.step * 2 * bumps, 0, 0],
            ]
        )
        vertices = vertices * [self.length /
                               (1 + 0.2 * bumps), 1, 0] + np.array(start)

        self.start_new_path(np.array(start))
        self.add_points_as_corners(np.array([*(np.array(vertex) for vertex in vertices)]))
        self.left_spring = Dot(color=RED).move_to(self.get_start())
        self.right_spring = Dot(color=RED).move_to(self.get_end())
        self.orig_width = self.width
        self.t = 0
        self.omega = 4
        self.amplitude = 1.75
        self.orig_angle = 0
        # self.add(self.left_spring)
        # self.add(self.right_spring)

    def oscillate(self, oscillates_num=1, amplitude=None, about_edge=RIGHT, new_oscillate=True):
        if amplitude is not None:
            self.amplitude = amplitude
        self.oscillate_about_edge = about_edge
        if about_edge is OUT:
            self.stretch_func = self.stretch_to_fit_depth
            if new_oscillate: self.orig_width = self.depth
        else:
            self.stretch_func = self.stretch_to_fit_width

        self.oscillates_num = oscillates_num
        self.start_t = self.t
        return UpdateFromAlphaFunc(self, self.update_spring, rate_func=linear, run_time=self.omega * oscillates_num)

    def update_spring(self, mob, alpha):
        self.t = self.oscillates_num * TAU * alpha + self.start_t
        self.stretch_func(
            self.orig_width + self.amplitude * np.sin(self.t), about_edge=self.oscillate_about_edge)


class OscillateMobject(VGroup):
    def __init__(self, oscillate_mobject, omega=4, amplitude=None, t=0, **kwargs):
        super().__init__(**kwargs)
        self.oscillate_mobject = oscillate_mobject
        self.add(oscillate_mobject)
        self.t = t
        self.omega = omega
        if amplitude is None:
            self.amplitude = oscillate_mobject.width * 1.5

    def oscillate(self, oscillates_num=1, amplitude=None, oscillate_direction=UP, new_reference_point=True):
        if new_reference_point:
            self.reference_point = self.oscillate_mobject.get_center()
        if amplitude is not None:
            self.amplitude = amplitude
        self.oscilate_direction = oscillate_direction
        self.oscillates_num = oscillates_num
        self.start_t = self.t
        return UpdateFromAlphaFunc(self, self.update_oscillate_mobject, rate_func=linear,
                                   run_time=self.omega * oscillates_num)

    def update_oscillate_mobject(self, mob, alpha):
        self.t = self.oscillates_num * TAU * alpha + self.start_t
        self.oscillate_mobject.move_to(self.reference_point + self.amplitude * np.sin(self.t) * self.oscilate_direction)
