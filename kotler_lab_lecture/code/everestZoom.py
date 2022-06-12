from manim import *
from manim_editor import PresentationSectionType as pst
from pathlib import Path

CUR_PATH = Path(__file__).resolve().parent


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
        everest_svg = SVGMobject(str(CUR_PATH / "everest.svg"), height=4).shift(UP * 0.32 + LEFT * 0.3)
        image = ImageMobject(str(CUR_PATH / "everest.jpg"))
        image.height = 10
        frame_text = MathTex(r"bla", color=YELLOW, font_size=67)
        zoomed_camera_text = Tex(r"$\times10^{15}$", color=YELLOW, font_size=67)

        self.add(image, dot)
        # self.wait()
        self.next_section("Mountain", pst.NORMAL)
        self.play(FadeOut(image), DrawBorderThenFill(everest_svg), run_time=3)
        # self.wait()
        self.next_section("Mountain", pst.NORMAL)
        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame
        zoomed_display_frame = zoomed_display.display_frame

        frame.move_to(dot)
        frame.set_stroke_color(WHITE)  # TODO:change to yellow if want correct frame color
        zoomed_display_frame.set_stroke_color(YELLOW)
        zoomed_display.shift(DOWN)
        self.wait()
        self.next_section("Zoom", pst.NORMAL)
        self.play(Create(frame))  # FadeIn(frame_text, shift=UP))
        self.activate_zooming()
        self.next_section("OutZoom", pst.NORMAL)
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
        # self.wait()
        self.next_section("Scale camera", pst.NORMAL)
        zoomed_camera_text.remove_updater(camera_text_updater)
        self.play(ScaleInPlace(zoomed_display, 2), FadeOut(zoomed_camera_text, shift=DOWN))
        # self.wait()

        self.everest_orig_height = everest_svg.height

        mountain_run_time = 5

        def oscilate_everest(everest, alpha):
            everest.stretch_to_fit_height(
                self.everest_orig_height + 0.15 * np.sin(alpha * 2 * PI), about_edge=DOWN)

        oscilate_animation = UpdateFromAlphaFunc(everest_svg, oscilate_everest)
        self.next_section("Move Mountain", pst.COMPLETE_LOOP)
        self.play(oscilate_animation, run_time=mountain_run_time, rate_func=linear)
        self.next_section("Finish", pst.NORMAL)
        self.play(self.get_zoomed_display_pop_out_animation(), rate_func=lambda t: smooth(1 - t))
        self.play(Uncreate(zoomed_display_frame), FadeOut(frame))
        # self.play()
        Ellipse()
        self.wait()
