from copy import deepcopy
from manim.renderer.opengl_renderer import OpenGLRenderer
from manim.opengl import *
from manim import *
from drum import Drum
from manim_editor import PresentationSectionType as pst

MAIN_PATH = Path(__file__).resolve().parent.parent
RESOURCE_DIR = MAIN_PATH / "resources"
sys.path.append(str(MAIN_PATH))
from tools.animations import Count, ShiftAndRotateAlongPath, get_path_pending

PRESENTATION_MODE = False
FAST_RENDER = PRESENTATION_MODE
BEAUTY_PLANE = FAST_RENDER
Z_FACTOR = 0


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
        self.wait(0.1)

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
                "default_frame_stroke_color": YELLOW,
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
        frame.set(stroke_color=WHITE)
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


class SimulationRoad(Scene):
    def construct(self):
        tip_head = Dot(color=BLUE, fill_opacity=1).scale(2).set_z_index(2)
        tip_head = Triangle(color=BLUE, fill_opacity=1).scale(0.2).set_z_index(2)
        TracedPath(tip_head.get_center(), color=YELLOW)
        hell_road = SVGMobject(str(RESOURCE_DIR / "turture_road.svg"), background_stroke_width=20, stroke_width=20,
                               width=12)
        for path_road in hell_road:
            path_road.set_stroke(width=10)
        main_road = hell_road[0]
        main_road.set_z_index(1)
        hell_road = hell_road[1:]

        start_angle = get_path_pending(main_road[0], 0)
        tip_head.move_to(main_road[0].get_start())
        tip_head.rotate(start_angle).rotate(PI)

        self.add(main_road)
        self.wait()
        self.play(ShowPassingFlash(
            main_road.copy().set_color(BLUE), run_time=4, time_width=1))
        self.play(ShiftAndRotateAlongPath(tip_head, main_road[0], run_time=8))
        self.wait(0.1)

        # self.play(MoveAlongPath(tip_head, main_road[0]),
        # run_time = 12)
        self.wait()
        self.play(Write(hell_road))
        self.wait()
