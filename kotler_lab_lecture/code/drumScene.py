import numpy as np
from manim import *
from drum import Drum
from manim.opengl import *
from manim.renderer.opengl_renderer import OpenGLRenderer
from pathlib import Path
from manim_editor import PresentationSectionType as pst
from copy import deepcopy

RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resources"
MAIN_PATH = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(MAIN_PATH))
from tools.animations import Count

FAST_RENDER = True
ROTATE_SCENE = False if FAST_RENDER else True
BEAUTY_PLANE = True
PRESENTATION_MODE = True
Z_FACTOR = 0
from spring import Spring


# TODO: next: c2p Accepts coordinates from the axes and returns a point with respect to the scene. so check all code doing that
# TODO:center axis in numper plane. maybe odd x and y ticks.
# TODO:Try to fix z_index problem with - https://www.reddit.com/r/manim/comments/tsx6ks/objects_jumping_in_front_of_each_other_in_3d_scene/i6dtd8x/
# config.renderer = "opengl"


class DrumScene(ThreeDScene):
    def __init__(self, **kwargs):
        self.cut_axes_at_radius = False
        self.get_basic_coords_config()

        if not isinstance(self, SpecialThreeDScene):
            super().__init__(**kwargs)
            return
        if config.renderer == "opengl":
            # Items associated with interaction
            self.mouse_point = OpenGLPoint()
            self.mouse_drag_point = OpenGLPoint()
            self.renderer = OpenGLRenderer()

        else:
            self.renderer = CairoRenderer(
                camera_class=self.camera_class,
                skip_animations=self.skip_animations,
            )

        low_quality_config = {
            "camera_config": {"should_apply_shading": False},
            "three_d_axes_config": dict(num_axis_pieces=1, **self.three_d_axes_config)}
        super().__init__(three_d_axes_config=self.three_d_axes_config, low_quality_config=low_quality_config, **kwargs)

    def get_basic_coords_config(self):
        epsilon = 0.01
        factor = 3 if FAST_RENDER else 3
        factor_range = factor * 1 if FAST_RENDER else factor * 4
        addition = 0.5 if BEAUTY_PLANE else 0
        self.basic_coords_config = {
            "x_range": (
                -round(config["frame_y_radius"] * factor_range) - addition - epsilon,
                round(config["frame_y_radius"] * factor_range) + addition + epsilon),
            "y_range": (
                -round(config["frame_y_radius"] * factor_range) - addition - epsilon,  # "frame_y_radius"=4
                round(config["frame_y_radius"] * factor_range) + addition + epsilon),  # "frame_height"=8
            "x_length": round(config["frame_height"] * factor), "y_length": round(config["frame_height"] * factor)}
        self.three_d_axes_config = dict(stroke_opacity=0.4, z_length=config.frame_height // 2 - 1,
                                        z_index=Z_FACTOR,
                                        z_range=[0, config["frame_height"] - 2], **self.basic_coords_config)

    def get_axes(self) -> ThreeDAxes:
        """Return a set of 3D axes.

        Returns
        -------
        :class:`.ThreeDAxes`
            A set of 3D axes.
        """
        axes = ThreeDAxes(**self.three_d_axes_config)
        return axes
        for axis in axes:
            if self.cut_axes_at_radius:
                p0 = axis.get_start()
                p1 = axis.number_to_point(-1)
                p2 = axis.number_to_point(1)
                p3 = axis.get_end()
                new_pieces = VGroup(Line(p0, p1), Line(p1, p2), Line(p2, p3))
                for piece in new_pieces:
                    piece.shade_in_3d = True
                new_pieces.match_style(axis.pieces)
                axis.pieces.submobjects = new_pieces.submobjects
            for tick in axis.get_tick_marks():
                tick.add(VectorizedPoint(1.5 * tick.get_center()))
        return axes

    def build_axes(self):
        self.axes = self.get_axes()
        self.x_axis, self.y_axis, self.z_axis = self.axes
        # self.axes = Dot()
        self.plane = NumberPlane(**self.basic_coords_config, faded_line_ratio=2 if BEAUTY_PLANE else 1).move_to(
            self.axes.c2p(0, 0, 0))
        self.plane.remove(self.plane.axes)
        self.plane.remove(self.plane.background_lines)
        self.plane.axes = VGroup(self.x_axis, self.y_axis)
        self.add(*self.plane.axes)
        self.plane._init_background_lines()

        # self.axes.move_to(self.plane.c2p(0, 0))
        # if BEAUTY_PLANE:
        #     self.plane.background_lines[26].set_opacity(0.4)
        #     self.plane.background_lines[0].set_opacity(0.4)
        #     self.plane.shift(UL * 0.5)
        #     self.plane.x_axis.set_opacity(0)
        #     self.plane.y_axis.set_opacity(0)

        self.space = (self.axes, self.plane)
        if not config.renderer == "opengl":
            # self.space[1].set_z_index(Z_FACTOR, family=True)
            # self.space[0].set_z_index(Z_FACTOR, family=True)
            # self.space[1].set_z_index_by_z_coordinate()
            # self.space[0].set_z_index_by_z_coordinate()
            return
        return

    def get_drum(self):
        R_factor = self.axes.x_length * 0.2
        return Drum(bessel_order=1, mode=2, axes=self.axes, R=R_factor,
                    d_0=R_factor * 0.3, amplitude=R_factor * 0.3 * 0.8, z_index=Z_FACTOR + 4, stroke_width=0.01)

    def move_camera_comp(self, **kwargs):
        if config.renderer == "opengl":
            if "zoom" in kwargs:
                del kwargs["zoom"]
        self.space[1].set_z_index_by_z_coordinate()
        self.space[0].set_z_index_by_z_coordinate()
        self.move_camera(**kwargs)

    def get_camera_position(self):
        if config.renderer == "opengl":
            return [75 * DEGREES, -30 * DEGREES, 0]
        return dict(phi=self.camera.get_phi(),
                    theta=self.camera.get_theta(),
                    zoom=self.camera.get_zoom())

    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL,
                        skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        # self.run_everest()
        self.build_axes()
        self.set_camera_orientation(phi=70 * DEGREES, theta=-30 * DEGREES)
        # if ROTATE_SCENE: self.begin_ambient_camera_rotation(rate=0.01)
        self.begin_ambient_camera_rotation(rate=0.001)

        drum = self.get_drum()
        if not config.renderer == "opengl":
            drum.set_z_index_by_z_coordinate()
            # drum.set_z_index(5, family=True)
        self.wait()
        self.my_next_section("Intro", pst.NORMAL)
        self.space[1].set_z_index_by_z_coordinate()
        self.space[0].set_z_index_by_z_coordinate()
        drum.set_z_index_by_z_coordinate()
        self.play(Create(self.space[0]), Create(self.space[1]))
        self.wait()
        self.axes_shift = 1.3 * IN
        # if config.renderer == "opengl":
        #     Group(self.space, drum).shift(1.5 * IN)
        # else:
        #     VGroup(self.space, drum).shift(1.5 * IN)

        # self.play(Create(self.space))

        self.wait()

        if config.renderer == "opengl":
            self.play(FadeIn(drum), run_time=3)
        else:
            self.play(DrawBorderThenFill(drum), run_time=3)
        self.show_capacitor(drum)
        return
        self.split_drums(drum)

        self.my_next_section("Finish drums scene", pst.NORMAL)
        self.play(Unwrite(drum), Unwrite(self.space[1]), Unwrite(self.space[0]))
        self.wait()

    def show_capacitor(self, drum):
        self.my_next_section("Capacitor description", pst.NORMAL)
        drum.save_state()
        # np.ndarray().data
        camera_start_pos = self.get_camera_position()
        capacitor = Circle(fill_opacity=1, z_index=Z_FACTOR).scale_to_fit_width(
            drum.width * 0.5).move_to(self.axes.get_center()).set_color([PURPLE, ORANGE])
        capacitor.next_to(self.axes.c2p(*(UR * capacitor.radius * 0.6).data), self.axes.c2p(*UR.data))
        self.my_next_section("Show capacitor", pst.SUB_NORMAL)
        self.space[1].set_z_index_by_z_coordinate()
        self.space[0].set_z_index_by_z_coordinate()
        drum.set_z_index_by_z_coordinate()
        self.move_camera_comp(phi=80 * DEGREES, theta=-30 * DEGREES)
        self.bring_to_front(drum)
        if config.renderer == "opengl":
            self.play(Create(capacitor))
        else:
            capacitor.set_z_index_by_z_coordinate()
            self.play(DrawBorderThenFill(capacitor))
        # print(drum.get_center()[2], capacitor.get_center()[2], self.plane.get_center()[2], self.axes.get_center()[2])
        # for a in drum:
        #     print(a.get_center()[2])
        drum.move_to(capacitor).shift(UP)
        capacitor.add(drum)
        # self.remove(drum)
        self.play(Create(ThreeDAxes().shift(LEFT * 1 + 2.5 * IN)))
        self.add(Arrow().shift(DOWN + OUT))
        self.add(Sphere())
        self.add(MathTex(r"wwwwwwwwwwww", color=RED).shift(UP + OUT).scale(5))
        self.move_camera_comp(phi=120 * DEGREES, theta=-30 * DEGREES,
                              anim=[DrawBorderThenFill(capacitor)])
        self.wait(3)
        self.bring_to_front(drum)
        self.my_next_section("Move capacitor", pst.SUB_NORMAL)
        # a = VGroup(drum, capacitor)
        # self.remove(a)
        # a.arrange()
        # self.play(Create(a))
        NumberPlane()
        self.move_camera_comp(phi=0 * DEGREES, theta=-30 * DEGREES,
                              added_anims=[drum.animate.shift(LEFT * capacitor.get_x() * 2)])
        self.play(capacitor.animate.shift(LEFT * capacitor.get_x() * 2))
        return
        self.play(capacitor.animate.move_to(RIGHT * capacitor.width / 2))
        # self.interactive_embed()
        self.my_next_section("Camera move", pst.SUB_SKIP)
        self.move_camera_comp(phi=75 * DEGREES, theta=-30 * DEGREES)
        self.my_next_section("Vibrate drum", pst.SUB_COMPLETE_LOOP)
        self.play(drum.vibrate(oscillates=1))
        self.wait(0.0001)
        self.my_next_section("Vibrate drum", pst.SUB_SKIP)
        self.play(drum.vibrate(oscillates=0.25))
        self.my_next_section("Finish", pst.SUB_SKIP)

        self.move_camera_comp(phi=80 * DEGREES, theta=-30 * DEGREES)
        self.bring_to_front(drum)
        self.play(Unwrite(capacitor))
        self.move_camera_comp(**camera_start_pos)
        self.play(drum.animate(run_time=2.5).restore())
        drum.t = drum.start_t = 0
        return

    def split_drums(self, drum):

        start_freq = 10
        shift_freq = 0.5
        right_freq = VGroup(MathTex("f="), DecimalNumber(start_freq, color=YELLOW),
                            MathTex(r"\left[MHz\right]")).arrange(RIGHT, buff=0.09)
        right_freq.scale(2.3).next_to(self.space[1].get_edge_center(UP), UP).rotate(50 * DEGREES, RIGHT).shift(
            OUT * 0.5)
        left_freq = deepcopy(right_freq)
        right_freq.shift(RIGHT * self.space[1].get_edge_center(RIGHT)[0] // 2)
        left_freq.shift(RIGHT * self.space[1].get_edge_center(LEFT)[0] // 2)
        right_drum = drum
        right_drum.save_state()
        # drum.amplitude = drum.amplitude * 2
        shift_drums = right_drum.R * 1.3
        orig_drum_width = right_drum.width
        orig_drum_center = shift_drums

        # self.get_axes()
        # drum.get_z_index_reference_point()

        def stretch_drums_updater(drum_mob):
            # drum_mob.shift(LEFT * np.sign(drum_mob.get_center()[0]) * (
            #         orig_drum_center - 0.005 * orig_drum_center * (1 - right_freq[1].get_value() / start_freq)))
            drum_mob.stretch_to_fit_width(
                orig_drum_width - 11 * orig_drum_width * (1 - right_freq[1].get_value() / start_freq))

        camera_start_pos = self.get_camera_position()

        self.bring_to_back(self.space[0])
        self.bring_to_back(self.space[1])
        self.bring_to_front(right_drum)
        # self.camera.use_z_index = False
        self.my_next_section("Polar trick", pst.SKIP)
        self.move_camera_comp(phi=50 * DEGREES, theta=-90 * DEGREES, zoom=0.6,
                              )
        self.my_next_section("Moving one drum", pst.SUB_COMPLETE_LOOP)
        self.play(drum.vibrate(oscillates=1))
        self.wait(0.00001)
        self.my_next_section("Vibrate drum", pst.SUB_SKIP)
        self.play(drum.vibrate(oscillates=0.25))

        left_drum = deepcopy(drum)
        self.add(left_drum)

        # self.my_next_section("Two drums add", pst.SUB_SKIP)
        self.play(right_drum.animate.shift(shift_drums * RIGHT), left_drum.animate.shift(shift_drums * LEFT))
        self.bring_to_front(right_drum)
        self.my_next_section("Rotate left drum", pst.SUB_NORMAL)
        self.play(left_drum.rotate_drum(90 * DEGREES))
        self.wait()
        self.my_next_section("Add freq", pst.SUB_NORMAL)
        self.play(Write(right_freq), Write(left_freq))

        right_drum.add_updater(stretch_drums_updater)
        left_drum.add_updater(stretch_drums_updater)

        self.my_next_section("Stretch drums", pst.SUB_NORMAL)
        self.play(Count(right_freq[1], right_freq[1].get_value(), right_freq[1].get_value() - shift_freq),
                  Count(left_freq[1], left_freq[1].get_value(), left_freq[1].get_value() + shift_freq),
                  run_time=4)
        # self.interactive_embed()
        self.my_next_section("Stretch vibrate", pst.SUB_COMPLETE_LOOP)
        self.play(left_drum.vibrate(1), right_drum.vibrate(1))
        self.wait(0.00001)
        self.my_next_section("Stretch end", pst.SUB_SKIP)
        # self.play(left_drum.vibrate(0.25), right_drum.vibrate(0.25))
        self.play(Unwrite(left_freq), Unwrite(right_freq))
        self.wait()
        self.play(AnimationGroup(Unwrite(left_drum), right_drum.animate(run_time=2.5).restore(), lag_ratio=0.8))
        drum.t = drum.start_t = 0
        self.move_camera_comp(**camera_start_pos,
                              )
        # self.play(Uncreate(left_drum), Uncreate(right_drum))
        # self.play(Uncreate(self.space))


class EverestScene(ZoomedScene):
    def __init__(self, **kwargs):
        ZoomedScene.__init__(
            self,
            zoom_factor=0.3,
            zoomed_display_height=1,
            zoomed_display_width=4,
            # image_frame_stroke_width=20,
            zoomed_camera_config={
                "default_frame_stroke_width": 3,
                "default_frame_stroke_color": YELLOW,  # TODO:change all rectangle yellow
            },
            **kwargs
        )

    def construct(self):
        dot = Dot().shift(UP * 2.3 + LEFT * 0.7)
        everest_svg = SVGMobject(str(RESOURCE_DIR / "everest.svg"), height=4).shift(UP * 0.32 + LEFT * 0.3)
        image = ImageMobject(str(RESOURCE_DIR / "everest.jpg"))
        image.height = 10
        frame_text = MathTex(r"bla", color=YELLOW, font_size=67)
        zoomed_camera_text = Tex(r"$\times10^{15}$", color=YELLOW, font_size=67)
        self.wait()

        self.next_section("Everest Image", pst.NORMAL)
        # self.add(image, dot)
        self.play(FadeIn(image))
        self.next_section("Everest svg", pst.NORMAL)
        # self.wait()
        self.play(FadeOut(image), DrawBorderThenFill(everest_svg), run_time=3)
        # self.wait()
        self.next_section("Zoom Frame", pst.SUB_NORMAL)
        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame
        zoomed_display_frame = zoomed_display.display_frame

        frame.move_to(dot)
        frame.set(stroke_color=WHITE)  # TODO:change to yellow if want correct frame color
        zoomed_display_frame.set(stroke_color=YELLOW)
        zoomed_display.shift(DOWN)
        self.next_section("Zoom In", pst.SUB_NORMAL)
        self.play(Create(frame))  # FadeIn(frame_text, shift=UP))
        self.activate_zooming()
        self.next_section("OutZoom", pst.SUB_NORMAL)
        self.play(self.get_zoomed_display_pop_out_animation())
        camera_text_updater = lambda zomCam: zomCam.next_to(zoomed_display_frame, UP)
        zoomed_camera_text.add_updater(camera_text_updater)
        # zoomed_camera_text.add_updater(lambda z: z.become(zoomed_camera_text.next_to(zoomed_display_frame, UP)))
        self.play(Write(zoomed_camera_text, shift=UP))
        # self.wait()
        # Scale in        x   y  z
        scale_factor = [0.5, 1.5, 0]
        self.play(
            frame.animate.scale(scale_factor),
            zoomed_display.animate.scale(scale_factor),
            # FadeOut(zoomed_camera_text),
            # FadeOut(frame_text)
        )
        self.wait()
        self.next_section("Scale camera", pst.SUB_SKIP)
        zoomed_camera_text.remove_updater(camera_text_updater)
        self.play(ScaleInPlace(zoomed_display, 2), FadeOut(zoomed_camera_text, shift=DOWN))
        # self.wait()

        self.everest_orig_height = everest_svg.height

        mountain_run_time = 5

        def oscilate_everest(everest, alpha):
            everest.stretch_to_fit_height(
                self.everest_orig_height + 0.15 * np.sin(alpha * 2 * PI), about_edge=DOWN)

        oscilate_animation = UpdateFromAlphaFunc(everest_svg, oscilate_everest)
        self.next_section("Move Mountain", pst.SUB_COMPLETE_LOOP)
        self.play(oscilate_animation, run_time=mountain_run_time, rate_func=linear)
        self.wait(0.001)
        self.next_section("Finish", pst.SUB_NORMAL)
        self.play(self.get_zoomed_display_pop_out_animation(), rate_func=lambda t: smooth(1 - t))
        self.play(Uncreate(zoomed_display_frame), FadeOut(frame))
        self.play(Unwrite(everest_svg))
        # self.play()
        self.wait()


class HistoryBrief(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        self.play_kotler_win()
        self.wait(3)

    def play_kotler_win(self):
        winners_svg = SVGMobject(str(RESOURCE_DIR / "winners.svg"), width=4, stroke_color=WHITE)
        self.play(Write(winners_svg))
        kotler_face = ImageMobject(str(RESOURCE_DIR / "kotler_face.png")).to_edge(winners_svg.get_top()).scale(1.5)
        self.play(FadeIn(kotler_face))


class SpringScene(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.omega = 3
        self.spring_len = 6
        self.arrows_dist = DOWN * 0.36
        self.arrows_buff = 0.1

    def construct(self):
        self.create_spring_system()
        self.system.stretch_to_fit_height(self.system.height * 0.5)
        self.play_spring_intro()
        self.play_capacitor_addition()
        self.play_electric_coupling()
        self.wait(3)

    def play_spring_intro(self):
        self.play(AnimationGroup(Create(self.wall), Create(self.spring), DrawBorderThenFill(self.mass), lag_ratio=1))

        d0_line = Line(self.mass.get_top(), self.mass.get_top() + UP * 0.7, stroke_width=10).shift(UP * 0.2)
        self.d0_line = d0_line
        d0_tex = MathTex("d_{0}").next_to(d0_line, UP)
        move_arrow = Arrow(d0_line.get_center(), d0_line.get_center() + RIGHT * 1, stroke_width=7).next_to(d0_line,
                                                                                                           buff=0)

        omega = MathTex("\Omega_{mech}").next_to(self.spring, DOWN, buff=0.7)
        self.omega_mech_tex = omega
        move_arrow.scale(1e-1 * 2, about_edge=LEFT)
        move_arrow.set_stroke(width=7)
        self.system += omega
        self.system += d0_line
        self.system += d0_tex
        self.system += move_arrow

        self.play(AnimationGroup(self.spring.oscillate(1.5), Write(omega), lag_ratio=0.5))
        self.play(Create(d0_line))
        self.play(Write(d0_tex))
        self.spring.omega = self.spring.omega * 2.2
        self.play(self.spring.oscillate(0.25))
        self.play(move_arrow.animate().scale_to_fit_width(
            self.spring.amplitude * 1, about_edge=LEFT).set_stroke(width=7))
        x_tex = MathTex("x").next_to(move_arrow, UP, buff=0.2)
        self.system += x_tex
        self.play(FadeIn(x_tex, shift=UP))

    def play_capacitor_addition(self):
        tmp_capacitor = Rectangle(width=self.mass.width * 0.3, color=LIGHT_BROWN, fill_opacity=0, stroke_opacity=0)
        tmp_capacitor.move_to(
            np.array([self.d0_line.get_x(), self.mass.get_y(), 0]) + LEFT * 1.4 * (
                np.abs(self.d0_line.get_x() - self.wall.get_left()[0])))
        self.group_optomechanic_system = VGroup(self.system, tmp_capacitor)
        self.add(tmp_capacitor)
        self.play(self.group_optomechanic_system.animate.center())

        self.group_optomechanic_system.remove(tmp_capacitor)
        self.remove(tmp_capacitor)
        self.capacitor = tmp_capacitor.copy()
        self.capacitor.set_fill(opacity=0.9)
        self.capacitor.set_stroke(opacity=1)
        self.play(DrawBorderThenFill(self.capacitor))
        self.group_optomechanic_system += self.capacitor
        self.wait()

    def play_electric_coupling(self):
        self.play(self.group_optomechanic_system.animate.to_edge(UP))
        lc_circuit = SVGMobject(str(RESOURCE_DIR / "LC_circuit.svg"),
                                width=np.abs(self.capacitor.get_x() - self.mass.get_x()),
                                color=WHITE, stroke_color=WHITE)
        lc_circuit.move_to(
            np.array([(self.capacitor.get_x() + self.mass.get_x()) / 2,
                      self.mass.get_bottom()[1] - lc_circuit.height / 2, 0]))
        self.play(DrawBorderThenFill(lc_circuit), self.omega_mech_tex.animate.next_to(self.spring, UP, buff=0.7))

        self.electric_field = self.get_electric_field()
        self.play(Create(self.electric_field))
        self.set_electric_field_animation()
        self.wait()
        self.play(Uncreate(lc_circuit))
        self.wait()

        self.const_arrows = True
        self.force_e = self.get_e_force()
        eq1 = MathTex("F_{E}", "=", "Q", "E").next_to(self.group_optomechanic_system.get_bottom(), DOWN,
                                                      buff=1).set_color_by_tex("F_{E}", BLUE)
        eq2 = MathTex("F_{E}", "=", "Q", r"\frac{V}{d}").move_to(eq1).set_color_by_tex("F_{E}", BLUE)
        eq3 = MathTex("F_{E}", "=", "Q", r"\frac{V}{d_{0}+x}", substrings_to_isolate="x").move_to(
            eq2).set_color_by_tex(
            "F_{E}", BLUE)
        eq4 = MathTex("F_{E}", "=", "Q", r"\frac{V}{x}", substrings_to_isolate="x").move_to(
            eq3).set_color_by_tex("F_{E}", BLUE)
        self.play(Write(eq1))
        self.wait(0.5)
        self.play(Create(self.force_e))
        self.wait()
        self.play(TransformMatchingTex(eq1, eq2))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq2, eq3))
        self.wait(0.5)
        self.play(TransformMatchingTex(eq3, eq4))

        eq_mech = MathTex("F_{mech}", "=", "-kx").next_to(eq1.get_bottom(), DOWN, buff=0.8).set_color_by_tex(
            "F_{mech}", GREEN)
        self.mech_force = self.get_mech_force()
        self.play(Write(eq_mech), Create(self.mech_force))
        self.wait()
        self.mech_force.add_updater(
            lambda force_mech_arrow: force_mech_arrow.put_start_and_end_on(*self.get_mech_force_size()))
        self.force_e.add_updater(
            lambda force_arrow: force_arrow.put_start_and_end_on(*self.get_e_force_size()))
        self.play(self.spring.oscillate(0.2))
        self.wait()

        self.const_arrows = False
        self.mech_force.suspend_updating()
        self.force_e.suspend_updating()
        self.play(self.mech_force.animate.put_start_and_end_on(*self.get_mech_force_size()))
        self.play(self.force_e.animate.put_start_and_end_on(*self.get_e_force_size()))
        self.wait()

        self.mech_force.resume_updating()
        self.force_e.resume_updating()
        self.play(self.spring.oscillate(0.5))

        # self.play(self.spring.oscillate(0.5))

        # self.play(self.spring.oscillate(3))

    def get_e_force_size(self):
        self.e_addition_size = 1
        size_arr = self.d0_line.get_x() - self.mass.get_x()
        left_side = self.mass.get_bottom() + self.arrows_dist + self.arrows_buff * LEFT * np.sign(size_arr)
        right_side = left_side + (self.e_addition_size + (self.spring.amplitude - np.abs(size_arr))) ** 0.7 * np.sign(
            size_arr) * LEFT if not self.const_arrows else left_side + self.e_addition_size * RIGHT
        return left_side, right_side

    def get_mech_force_size(self):
        size_arr = self.d0_line.get_x() - self.mass.get_x()
        left_side = self.mass.get_bottom() + self.arrows_dist + self.arrows_buff * RIGHT * np.sign(size_arr)
        right_side = left_side + size_arr * RIGHT if not self.const_arrows else left_side + self.spring.amplitude * LEFT
        return left_side, right_side

    def get_mech_force(self) -> Arrow:
        return Arrow(*self.get_mech_force_size(), stroke_width=12, stroke_color=GREEN, buff=0.1)

    def get_e_force(self) -> Arrow:
        return Arrow(*self.get_e_force_size(), stroke_width=12, stroke_color=BLUE, buff=0.1)

    def set_electric_field_animation(self):
        self.electric_field.add_updater(lambda field: field.become(self.get_electric_field()))

    def create_spring_system(self):
        self.spring = Spring(self.spring_len / 2 * LEFT, length=self.spring_len, stroke_width=5)
        self.spring.set_color(YELLOW)
        self.wall = self.draw_wall(self.spring.right_spring)
        self.mass = Rectangle(height=self.wall.height, width=1, fill_color=BLUE, stroke_color=BLUE,
                              fill_opacity=0.6).next_to(self.spring.get_start(), LEFT, buff=0)
        self.mass.add_updater(lambda mob: mob.next_to(self.spring.get_start(), LEFT, buff=0))
        # center = (self.mass.get_left()[0] - self.wall.get_right()[0])
        self.system = VGroup(self.spring, self.wall, self.mass).center()

    def get_electric_field(self):
        size = np.sin(self.spring.t) * 2
        color = BLUE if size <= 0 else RED
        y_additions = np.array([0.3, -0.5])
        x_additions = np.array([0.4, -1])
        field_x_range = np.array([self.capacitor.get_right()[0], self.mass.get_left()[0]])
        field_y_range = np.array([self.mass.get_bottom()[1], self.mass.get_top()[1]])
        return ArrowVectorField(lambda pos: LEFT * size, color=color,
                                x_range=(field_x_range + x_additions).tolist(),
                                y_range=(field_y_range + y_additions).tolist())

    def draw_wall(self, pivot_mobject: Mobject, wall_len=2):
        color = WHITE
        wall = VGroup(
            DashedLine(
                start=wall_len * LEFT * 0.95,
                end=(wall_len) * RIGHT * 0.95,
                dashed_ratio=1.3,
                dash_length=0.6,
                color=GREY, stroke_width=8
            ).shift(pivot_mobject.get_start()[1] * UP)
        )
        [i.rotate(PI / 4, about_point=i.get_start()) for i in wall[0].submobjects]
        wall.add(
            Line(wall_len * LEFT, wall_len * RIGHT, color=color, stroke_width=18).align_to(wall, DOWN))

        return wall.rotate(-PI / 2).next_to(pivot_mobject.get_right(), RIGHT, buff=0)


class g0Scene(Scene):
    def construct(self):
        ax = Axes(x_range=(0, 10), y_range=[0, 1, 0.1], x_length=round(config.frame_width) - 5,
                  y_length=round(config.frame_height) / 2 - 2,
                  y_axis_config={"numbers_to_include": np.arange(0, 1 + 0.1, 0.5)})
        ax += ax.get_y_axis_label(MathTex(r"\frac{E_{mech}}{E_{elec}}"), edge=LEFT, direction=LEFT * 2, buff=2)
        ax += ax.get_x_axis_label(MathTex("t"), edge=DOWN, direction=DOWN)

        g0_tracker = ValueTracker(3)
        tau_tracker = ValueTracker(3)
        exp_func = lambda x: np.exp(-x / tau_tracker.get_value())

        energy_func = lambda t: (np.sin(g0_tracker.get_value() * t) + 1) * exp_func(t) / 2

        energy_graph = always_redraw(lambda: ax.plot(energy_func, color=BLUE))

        def get_exp_plot():
            tmp = ax.plot(exp_func, color=YELLOW)
            b = DashedVMobject(tmp, num_dashes=16, fill_opacity=0.7, stroke_opacity=0.5)
            return b

        exp_graph = always_redraw(lambda: ax.plot(exp_func, color=YELLOW))
        exp_graph_dash = always_redraw(get_exp_plot)

        # line = always_redraw(
        #     lambda: ax.get_vertical_line(ax.c2p(tau_tracker.get_value(), exp_func(tau_tracker.get_value())),
        #                                  line_config={"dashed_ratio": 0.85}))
        # dot = always_redraw(lambda: Dot(ax.c2p(tau_tracker.get_value(), 0)))
        # tau = MathTex(r"\tau")
        # tau.add_updater(lambda tex: tex.to_edge(dot.get_bottom(), DOWN, buff=0))
        ax += always_redraw(
            lambda: ax.get_T_label(x_val=tau_tracker.get_value(), graph=exp_graph, label=MathTex(r"\tau", color=YELLOW),
                                   line_func=DashedLine, label_color=YELLOW, line_color=WHITE))
        self.add(ax, energy_graph, exp_graph_dash)
        self.wait()

        g0_init = g0_tracker.get_value()
        tau_init = tau_tracker.get_value()

        g0_digit = DecimalNumber(10, unit=r" [mH]").set_color(GREEN).scale(0.7)
        g0_tex = MathTex("g_{0}=", color=GREEN).next_to(g0_digit.get_left(), LEFT, buff=0.5).set_y(
            g0_digit.get_center()[1] - 0.05)
        g0_tex_group = VGroup(g0_tex, g0_digit).to_edge(UR)

        tau_digit = DecimalNumber(10, unit=r" [s]").set_color(YELLOW).scale(0.7)
        tau_tex = MathTex(r"\tau=", color=YELLOW).next_to(tau_digit.get_left(), LEFT, buff=0.5).set_y(
            tau_digit.get_center()[1] - 0.05)
        tau_tex_group = VGroup(tau_tex, tau_digit).next_to(g0_tex_group.get_bottom(), DOWN)

        self.add(g0_tex_group, tau_tex_group)
        # self.play(tau_tracker.animate(run_time=6).set_value(tau_init + 6))
        # self.play(tau_tracker.animate(run_time=6).set_value(tau_init + 4))
        # self.wait()

        # self.play(tau_tracker.animate(run_time=6).set_value(tau_init))
        self.play(g0_tracker.animate(run_time=6).set_value(g0_init * 2), Count(g0_digit, 10, 11))

        # dot = Dot(point)


with tempconfig({"quality": "low_quality", "preview": True, "media_dir": MAIN_PATH / "media",
                 "save_sections": True, "disable_caching": False
                 }):
    scene = g0Scene()
    scene.render()
