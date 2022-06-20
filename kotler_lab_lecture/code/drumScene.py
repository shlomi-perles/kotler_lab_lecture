from copy import deepcopy
from manim.renderer.opengl_renderer import OpenGLRenderer
from manim.opengl import *
from manim import *
from drum import Drum
from manim_editor import PresentationSectionType as pst
from itertools import cycle

MAIN_PATH = Path(__file__).resolve().parent.parent
RESOURCE_DIR = MAIN_PATH / "resources"
sys.path.append(str(MAIN_PATH))
from spring import Spring, OscillateMobject

PRESENTATION_MODE = False
BEAUTY_PLANE = True
Z_FACTOR = 0


def draw_wall(pivot_mobject: Mobject, wall_len=2):
    color = WHITE
    wall = VGroup(
        DashedLine(start=wall_len * LEFT * 0.95, end=(wall_len) * RIGHT * 0.95, dashed_ratio=1.3, dash_length=0.6,
            color=GREY, stroke_width=8).shift(pivot_mobject.get_start()[1] * UP))
    [i.rotate(PI / 4, about_point=i.get_start()) for i in wall[0].submobjects]
    wall.add(Line(wall_len * LEFT, wall_len * RIGHT, color=color, stroke_width=18).align_to(wall, DOWN))

    return wall.rotate(-PI / 2).next_to(pivot_mobject.get_right(), RIGHT, buff=0)


def get_electric_field_capac(capacitor, mass):
    size = np.sin(-0.2) * 2
    color = BLUE if size <= 0 else RED
    y_additions = np.array([0.3, -0.5])
    x_additions = np.array([0.4, -1])
    field_x_range = np.array([capacitor.get_right()[0], mass.get_left()[0]])
    field_y_range = np.array([mass.get_bottom()[1], mass.get_top()[1]])
    return ArrowVectorField(lambda pos: LEFT * size, color=color, x_range=(field_x_range + x_additions).tolist(),
                            y_range=(field_y_range + y_additions).tolist())


def get_spring_system():
    spring_len = 6
    spring = Spring(spring_len / 2 * LEFT, length=spring_len, stroke_width=5)
    spring.set_color(YELLOW)
    wall = draw_wall(spring.right_spring)
    # VGroup(wall, spring).to_edge(RIGHT)
    mass = Rectangle(height=wall.height, width=1, fill_color=BLUE, stroke_color=BLUE, fill_opacity=0.6).next_to(
        spring.get_start(), LEFT, buff=0)
    capacitor = Rectangle(height=mass.height, width=mass.width * 0.3, color=LIGHT_BROWN, fill_opacity=0.9,
                          stroke_opacity=1)
    capacitor.move_to(
        np.array([mass.get_x(), mass.get_y(), 0]) + LEFT * 1.4 * (np.abs(mass.get_x() - wall.get_left()[0])))
    electric_field = get_electric_field_capac(capacitor, mass)
    omega_mech_tex = MathTex(r"\Omega_{mech}").next_to(spring.get_top(), UP, buff=1.4).scale(1.5)
    omega_lc_tex = MathTex(r"\omega_{LC}").next_to(electric_field.get_top(), UP).scale(1.5).match_y(omega_mech_tex)
    return VGroup(spring, wall, mass, capacitor, electric_field, omega_mech_tex, omega_lc_tex)


class IntroSummary(ThreeDScene):
    def __init__(self, start_point=0, **kwargs):
        super().__init__(**kwargs)
        self.start_point = start_point
        self.parts_num = 3
        self.current_part = 0

    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def play_strating_point(self):
        self.start = True
        self.my_next_section("Lecture Summary")
        self.wait()
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Write(self.starting_mobjects))

    # def end_strating_point(self):
    #     self.start = True
    #     self.my_next_section("Lecture Summary")
    #     self.my_next_section(typ=pst.SUB_NORMAL)
    #     self.play(FadeOut(progress_bar), FadeOut(part_1_img, part_2_image, part_3_img),
    #               Unwrite(part_1_sub), Unwrite(part_2_sub), Unwrite(part_3_sub))
    #     self.wait(0.5)

    def construct(self):
        self.start = False
        progress_bar = self.make_progress_bar().to_edge(DOWN, buff=config["frame_height"] * 0.2)
        self.starting_mobjects = VGroup()
        self.starting_mobjects += progress_bar

        part_1_title = Tex("Theory", " of Quantum Mechanical Coupling")
        part_1_sub = Tex("Theory")
        part_1_img = SVGMobject(str(RESOURCE_DIR / "coupling_drums.svg"))
        self.next_part(part_1_title, part_1_sub, image=part_1_img, first=True)

        part_2_title = VGroup(Tex("Our ", "Project", ":"), Tex("Simulate MEMS Resonators")).arrange(DOWN)
        part_2_sub = Tex("Project")
        part_2_image = self.get_drum()
        self.next_part(part_2_title, part_2_sub, drum=True, image=part_2_image, include_end=False)
        self.wait(0.1)
        if self.start: self.my_next_section("Vibrating Membrene  Intro", pst.SUB_COMPLETE_LOOP)
        if self.start:
            self.play(part_2_image.vibrate(1))
            self.wait(0.001)
            self.my_next_section("Vibrating end Intro", pst.SUB_SKIP)
            self.play(part_2_image.vibrate(0.25))
        self.end_part(part_2_title, part_2_sub, part_2_image)

        # part_3_title = VGroup(
        #     Tex("Outline", ":"),
        #     Tex("What next?")).arrange(DOWN)
        part_3_title = Tex("What next?")
        part_3_sub = part_3_title
        part_3_img = ImageMobject(str(RESOURCE_DIR / "drums_photo.png"))
        self.next_part(part_3_title, part_3_sub, image=part_3_img)
        self.my_next_section("End Intro", pst.SUB_NORMAL)
        self.play(FadeOut(progress_bar), FadeOut(part_1_img, part_2_image, part_3_img), Unwrite(part_1_sub),
                  Unwrite(part_2_sub), Unwrite(part_3_sub))
        self.wait(0.5)

    def next_part(self, title, sub_title: Tex, drum=False, image=None, include_end=True, first=False):
        if self.current_part == self.start_point:
            self.play_strating_point()

        if not first:
            if self.start:
                self.play(self.moving_dot.animate.move_to(self.dots[self.current_part]), run_time=2, rate_func=linear)
                self.wait(0.1)
            else:
                self.moving_dot.move_to(self.dots[self.current_part])

        sub_title.next_to(self.dots[self.current_part], DOWN)
        if not self.start: self.starting_mobjects += sub_title
        if image:
            title.to_edge(UP)
        if self.start: self.play(Write(title))
        if image:
            if not drum:
                image.scale_to_fit_height(0.5 * (title.get_bottom()[1] - self.dots.get_top()[1]))
                image.set_y(self.dots.get_top()[1] + (title.get_bottom()[1] - self.dots.get_top()[1]) / 2)
            else:
                image = self.drum_scailing(image, title)

            if not isinstance(image, VMobject):
                if self.start: self.play(FadeIn(image))
            else:
                if self.start: self.play(DrawBorderThenFill(image))

            if not self.start:
                self.starting_mobjects += image

        if include_end:
            self.end_part(title, sub_title, image)

    def end_part(self, title, sub_title: Tex, image=None):
        if self.start: self.next_section(pst.SUB_NORMAL)
        if image:
            if self.start:
                self.play(TransformMatchingTex(title, sub_title),
                          image.animate.match_width(sub_title).next_to(self.dots[self.current_part], UP))
            else:
                image.match_width(sub_title).next_to(self.dots[self.current_part], UP)
        else:
            self.play(TransformMatchingTex(title, sub_title))
        self.current_part += 1

    def get_drum(self):
        axes = ThreeDAxes()
        R_factor = axes.x_length * 0.2
        reso = [37, 37] if PRESENTATION_MODE else [3, 3]
        drum = Drum(bessel_order=1, mode=2, axes=axes, R=R_factor * 2, d_0=0, amplitude=R_factor * 0.7 * 0.8,
                    z_index=Z_FACTOR + 4, stroke_width=1, stroke_color=BLUE_A, resolution=reso)
        return drum

    def drum_scailing(self, drum, title):
        system = VGroup(drum, drum.axes)
        system.rotate(105, LEFT)
        system.scale_to_fit_height(1.2 * (title.get_bottom()[1] - self.dots.get_top()[1]))
        system.center()
        drum.opacity_all = 0
        drum.set_opacity(0)
        self.play(drum.vibrate(0.001))
        self.remove(drum)
        drum.opacity_all = 1
        drum.set_opacity(1)
        return drum

    def make_progress_bar(self, scale_bar=2):  # only setting up the mobjects
        dots = VGroup(*[Dot(z_index=3) for _ in range(self.parts_num)], z_index=0)
        dots.arrange(buff=(config["frame_width"] * 0.6) / (scale_bar * (self.parts_num - 1))).scale(
            scale_bar).set_color(BLUE)
        dots[0].set_color(ORANGE)
        dots[-1].set_color(ORANGE)
        moving_dot = Dot(color=ORANGE, z_index=4).scale(2.5)
        moving_dot.move_to(dots[0])
        path = Line(dots[0], dots[1], stroke_width=10, z_index=2, color=ORANGE)
        background_line = Line(dots[0], dots[-1], stroke_width=10, z_index=0, color=GREY, fill_opacity=0.5)
        path.add_updater(lambda x: x.become(Line(dots[0], moving_dot, stroke_width=10, z_index=2, color=ORANGE)))
        self.dots = dots
        self.moving_dot = moving_dot
        return VGroup(dots, moving_dot, path, background_line)


class IntroSummary2(IntroSummary):
    def __init__(self, **kwargs):
        super().__init__(start_point=1, **kwargs)


class IntroSummary3(IntroSummary):
    def __init__(self, **kwargs):
        super().__init__(start_point=2, **kwargs)


class HistoryBrief(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        self.mob_remove_at_end = VGroup()
        self.images_remove_at_end = Group()
        self.build_scene()
        self.play_bohr_phase()
        self.play_cleland_phase()
        self.play_kotler_phase()
        self.my_next_section("End Quantum's Orders", pst.SUB_NORMAL)
        self.play(FadeOut(self.images_remove_at_end), Unwrite(self.mob_remove_at_end))
        self.wait(0.1)

    def build_scene(self):
        self.main_title = Text("Quantum's Phenomenons & Orders of Magnitude: Main History Phases").scale_to_fit_width(
            config.frame_width * 0.9)
        self.mob_remove_at_end += self.main_title
        self.play(Write(self.main_title))
        self.my_next_section("Quantum's Orders")
        self.play(self.main_title.animate.scale(0.95).to_edge(UP))
        self.tick_scale = 2.5
        start = -12
        end = -4
        self.num_to_idx = {num: idx for idx, num in enumerate(range(start, end + 1))}
        self.scailing_line = NumberLine(scaling=LogBase(), x_range=[start, end, 1], length=config.frame_width * 0.75,
                                        # include_tip=True,
                                        numbers_with_elongated_ticks=list(self.num_to_idx.keys()),
                                        numbers_to_include=list(self.num_to_idx.keys())).to_edge(DOWN, buff=0.7)
        self.mob_remove_at_end += self.scailing_line
        self.play(Create(self.scailing_line))

    def next_part(self, title, order, enlarge_tip=True):
        self.cur_title = title.scale_to_fit_width(config.frame_width * 0.9)
        title.center()
        self.play(Write(title))
        self.play(title.animate.next_to(self.main_title, DOWN).scale_to_fit_width(self.main_title.width * 0.8))
        tick = self.scailing_line.get_tick_marks()[self.num_to_idx[order]]
        label = self.scailing_line.labels[self.num_to_idx[order]]
        tick_scale = self.tick_scale if enlarge_tip else 1
        self.play(tick.animate.set_color(YELLOW).scale(tick_scale), label.animate.set_color(YELLOW))
        return tick, label

    def end_part(self, title, sub_title: Tex, tick, label, image):
        self.next_section(pst.SUB_NORMAL)
        scale_tick = tick.copy().scale(1 / self.tick_scale)
        sub_title.scale(0.5).next_to(scale_tick, UP, buff=0.2)

        if image:
            self.play(TransformMatchingTex(title, sub_title),
                      image.animate.scale_to_fit_height(sub_title.height * 3.3).next_to(tick, UP),
                      tick.animate.scale(1 / self.tick_scale), label.animate.set_color(WHITE))
        else:
            self.play(TransformMatchingTex(title, sub_title))

    def play_bohr_phase(self):
        title = Tex("1900 - 1913:  ", "Ultraviolet catastrophe and Bohr's Model").set_color_by_tex("1900 - 1913:  ",
                                                                                                   YELLOW)
        sub_title = Tex("Quantization")
        self.mob_remove_at_end += sub_title
        tick, label = self.next_part(title, -10)
        self.create_bohr_orbits()
        self.mob_remove_at_end += self.bohr_model
        self.my_next_section("Bohr's phase", pst.SUB_NORMAL)
        self.play_bohr_orbits()
        self.end_part(title, sub_title, tick, label, self.bohr_model)

    def play_cleland_phase(self):
        title = Tex("1978:  ", "David J. Wineland - Superposition in trapped ions").set_color_by_tex("1978:  ", YELLOW)
        sub_title = Tex("Superposition")
        self.mob_remove_at_end += sub_title
        tick, label = self.next_part(title, -8)
        self.create_ion()
        self.images_remove_at_end.add(self.ion)
        self.my_next_section("End ion", pst.SUB_NORMAL)

        # self.play_two_slits()
        self.end_part(title, sub_title, tick, label, self.ion)
        self.cleland = ImageMobject(str(RESOURCE_DIR / "cleland.png")).match_height(self.ion).match_width(
            self.ion).next_to(self.scailing_line.get_tick_marks()[self.num_to_idx[-5]], UP)
        self.images_remove_at_end.add(self.cleland)

        cleland = Tex("2010:  ", "Andrew N. "
                                 "Cleland").set_color_by_tex("2010:  ", YELLOW).center()
        sub_title2 = sub_title.copy()
        self.mob_remove_at_end += sub_title2
        self.play(Write(cleland))
        self.add(sub_title2)
        self.play(FadeIn(self.cleland),
                  sub_title2.animate.next_to(self.scailing_line.get_tick_marks()[self.num_to_idx[-5]], UP, buff=0))

        self.my_next_section("End cleland", pst.SUB_NORMAL)
        self.play(Unwrite(cleland))
        self.s = sub_title

    def play_kotler_phase(self):
        title = Tex("2021:  ", "Macroscopic entanglement of mechanical devices").set_color_by_tex("2021:  ", YELLOW)
        self.mob_remove_at_end += title
        sub_title = Tex("Entanglement")
        tick, label = self.next_part(title, -5, False)
        self.create_kotler_image()
        self.play(FadeIn(self.drums_photo), run_time=0.5)
        self.play(Write(self.kotler_image[0]))
        self.play(FadeIn(self.kotler_image[
                             1]))  # self.play(FadeOut(self.cleland), Uncreate(self.s))  # self.end_part(title,
        # sub_title, tick, label, self.kotler_image)

    def create_ion(self):
        ion = ImageMobject(str(RESOURCE_DIR / "ion.png"))
        image_size = self.cur_title.get_bottom()[1] - self.scailing_line.get_top()[1]
        self.ion = ion.scale_to_fit_height(image_size * 0.8).set_y(self.cur_title.get_bottom()[1] - image_size / 2)
        self.play(FadeIn(self.ion))

    def create_bohr_orbits(self):
        levels = [self.balmer(x) for x in range(2, 6)]
        core = Dot().set_color(RED).center()
        orbits = VGroup(
            *[Circle(radius=lev, arc_center=core.get_center(), color=BLUE, stroke_width=DEFAULT_STROKE_WIDTH * 0.7) for
              lev in levels])
        n_labels = VGroup(
            *[MathTex(f"n={n + 1}").scale(0.56).next_to(orbits[n].get_top(), UP) for n in range(len(levels))])
        orbit_particle = core.copy().scale(2.7).set_color(GREEN).move_to(orbits[1].get_right())

        self.orbit_particle = orbit_particle
        self.orbits_order = cycle([1, 3, 0, 2])
        self.orbits = orbits
        image_size = self.cur_title.get_bottom()[1] - self.scailing_line.get_top()[1]
        self.bohr_model = VGroup(core, orbits, n_labels, orbit_particle).scale_to_fit_height(image_size * 0.8).set_y(
            self.cur_title.get_bottom()[1] - image_size / 2)

        self.play(FadeIn(core), run_time=0.3)
        self.play(FadeIn(orbits), lag_ratio=0.9, run_time=1)
        self.play(FadeIn(n_labels), lag_ratio=0.9, run_time=1.2)
        self.play(GrowFromCenter(orbit_particle))

    def play_bohr_orbits(self):
        orbit_particle = self.orbit_particle
        for _ in range(len(self.orbits)):
            n_orbit = next(self.orbits_order)
            if n_orbit != 1:
                orbit_particle.move_to(self.orbits[n_orbit].get_right())
                self.play(GrowFromCenter(orbit_particle))
            self.play(MoveAlongPath(orbit_particle, self.orbits[n_orbit]), time_rate=linear, run_time=2)

    def create_kotler_image(self):
        image_size = self.cur_title.get_bottom()[1] - self.ion.get_top()[1]
        self.drums_photo = ImageMobject(str(RESOURCE_DIR / "drums_photo.png")).scale_to_fit_height(
            image_size * 0.8).set_y(self.cur_title.get_bottom()[1] - image_size / 2)
        self.images_remove_at_end.add(self.drums_photo)
        winners_svg = SVGMobject(str(RESOURCE_DIR / "winners.svg"), width=4, stroke_color=WHITE)
        kotler_face = ImageMobject(str(RESOURCE_DIR / "kotler_face.png")).to_edge(winners_svg.get_top()).scale(1.5)
        self.kotler_image = Group(winners_svg, kotler_face).scale_to_fit_height(image_size * 0.7).next_to(
            self.drums_photo, RIGHT)
        self.images_remove_at_end.add(self.kotler_image)

    @staticmethod
    def balmer(n):
        Z = 1
        a_0 = 1
        scale_fac = 0.13
        return scale_fac * n ** 2 / Z * a_0


class SpringScene(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.omega = 3
        self.spring_len = 6
        self.arrows_dist = DOWN * 0.36
        self.arrows_buff = 0.1

    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        self.my_next_section("Spring Scene")
        self.create_spring_system()
        self.system.stretch_to_fit_height(self.system.height * 0.5)
        self.play_spring_intro()
        self.play_capacitor_addition()
        self.play_electric_coupling()
        self.play_g0()
        self.play(self.group_optomechanic_system.animate.center().scale_to_fit_width(config.frame_width * 0.8))
        self.new_sys = get_spring_system().center().scale_to_fit_width(config.frame_width * 0.8)
        self.play(Uncreate(self.force_e), Uncreate(self.mech_force))
        self.play(TransformMatchingShapes(self.group_optomechanic_system, self.new_sys))
        self.wait(0.1)

    def play_spring_intro(self):
        self.shift_d0_info = VGroup()
        self.play(AnimationGroup(Create(self.wall), Create(self.spring), DrawBorderThenFill(self.mass), lag_ratio=1))

        d0_line = Line(self.mass.get_top(), self.mass.get_top() + UP * 0.7, stroke_width=10).shift(UP * 0.2)
        self.shift_d0_info += d0_line
        self.d0_line = d0_line
        d0_tex = MathTex("d_{0}").next_to(d0_line, UP)
        move_arrow = Arrow(d0_line.get_center(), d0_line.get_center() + RIGHT * 1, stroke_width=7).next_to(d0_line,
                                                                                                           buff=0)
        self.shift_d0_info += move_arrow
        self.shift_d0_info += d0_tex

        omega = MathTex("\Omega_{mech}").next_to(self.spring, DOWN, buff=0.7)
        self.omega_mech_tex = omega
        move_arrow.scale(1e-1 * 2, about_edge=LEFT)
        move_arrow.set_stroke(width=7)
        self.system += omega
        self.system += d0_line
        self.system += d0_tex
        self.system += move_arrow
        self.my_next_section('oscillate start', pst.SUB_NORMAL)
        self.play(AnimationGroup(self.spring.oscillate(1.5), Write(omega), lag_ratio=0.2))
        self.wait(0.1)
        self.my_next_section('oscillate middle', pst.SUB_COMPLETE_LOOP)
        self.play(self.spring.oscillate(1))
        self.wait(0.001)
        self.my_next_section('Shift right', pst.SUB_SKIP)
        self.play(Create(d0_line))
        self.play(Write(d0_tex))
        self.spring.omega = self.spring.omega * 2.2
        self.play(self.spring.oscillate(0.25))
        self.play(
            move_arrow.animate().scale_to_fit_width(self.spring.amplitude * 1, about_edge=LEFT).set_stroke(width=7))
        x_tex = MathTex("x").next_to(move_arrow, UP, buff=0.2)
        self.shift_d0_info += x_tex
        self.system += x_tex
        self.play(FadeIn(x_tex, shift=UP))
        self.my_next_section('Shift End', pst.SUB_NORMAL)

    def play_capacitor_addition(self):
        tmp_capacitor = Rectangle(width=self.mass.width * 0.3, color=LIGHT_BROWN, fill_opacity=0, stroke_opacity=0)
        tmp_capacitor.move_to(np.array([self.d0_line.get_x(), self.mass.get_y(), 0]) + LEFT * 1.4 * (
            np.abs(self.d0_line.get_x() - self.wall.get_left()[0])))
        self.group_optomechanic_system = VGroup(self.system, tmp_capacitor)
        self.add(tmp_capacitor)
        self.play(self.group_optomechanic_system.animate.center())
        self.group_optomechanic_system.remove(tmp_capacitor)
        self.remove(tmp_capacitor)
        self.capacitor = tmp_capacitor.copy()
        self.capacitor.set_fill(opacity=0.9)
        self.capacitor.set_stroke(opacity=1)
        self.group_optomechanic_system = VGroup(self.system, self.capacitor)

        self.play(DrawBorderThenFill(self.capacitor))
        self.my_next_section(type=pst.SUB_NORMAL)

    def play_electric_coupling(self):
        self.play(self.group_optomechanic_system.animate.to_edge(UP))
        lc_circuit = SVGMobject(str(RESOURCE_DIR / "LC_circuit.svg"),
                                width=np.abs(self.capacitor.get_x() - self.mass.get_x()), color=WHITE,
                                stroke_color=WHITE)
        lc_circuit.move_to(np.array(
            [(self.capacitor.get_x() + self.mass.get_x()) / 2, self.mass.get_bottom()[1] - lc_circuit.height / 2, 0]))
        self.electric_field = self.get_electric_field()

        self.play(DrawBorderThenFill(lc_circuit), self.omega_mech_tex.animate.next_to(self.spring, UP, buff=0.7))
        self.play(Create(self.electric_field))
        self.group_optomechanic_system += self.electric_field
        self.omega_lc_tex = MathTex("\omega_{LC}").next_to(self.electric_field, UP, buff=0.7).match_y(
            self.omega_mech_tex)
        self.play(Write(self.omega_lc_tex))
        self.system += self.omega_lc_tex
        self.my_next_section(type=pst.SUB_NORMAL)

        self.set_electric_field_animation()
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Uncreate(lc_circuit))
        self.wait(0.5)
        self.my_next_section(type=pst.SUB_NORMAL)

        self.const_arrows = True
        self.force_e = self.get_e_force()
        eq1 = MathTex("F_{E}", "=", "Q", "E").next_to(self.group_optomechanic_system.get_bottom(), DOWN,
                                                      buff=1).set_color_by_tex("F_{E}", BLUE)
        eq2 = MathTex("F_{E}", "=", "Q", r"\frac{V}{d}").move_to(eq1).set_color_by_tex("F_{E}", BLUE)
        eq3 = MathTex("F_{E}", "=", "Q", r"\frac{V}{d_{0}+x}", substrings_to_isolate="x").move_to(eq2).set_color_by_tex(
            "F_{E}", BLUE)
        eq4 = MathTex("F_{E}", "=", "Q", r"\frac{V}{x}", substrings_to_isolate="x").move_to(eq3).set_color_by_tex(
            "F_{E}", BLUE)
        self.play(Write(eq1))
        self.wait(0.5)
        self.play(Create(self.force_e))
        self.group_optomechanic_system += self.force_e
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(TransformMatchingTex(eq1, eq2))
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(TransformMatchingTex(eq2, eq3))
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(TransformMatchingTex(eq3, eq4))
        self.my_next_section(type=pst.SUB_NORMAL)

        eq_mech = MathTex("F_{mech}", "=", "-kx").next_to(eq1.get_bottom(), DOWN, buff=0.8).set_color_by_tex("F_{mech}",
            GREEN)
        self.mech_force = self.get_mech_force()
        self.play(Write(eq_mech), Create(self.mech_force))
        self.group_optomechanic_system += self.mech_force
        self.mech_force.add_updater(
            lambda force_mech_arrow: force_mech_arrow.put_start_and_end_on(*self.get_mech_force_size()))
        self.force_e.add_updater(lambda force_arrow: force_arrow.put_start_and_end_on(*self.get_e_force_size()))
        self.my_next_section(type=pst.SUB_NORMAL)
        tmp_oscillate = 0.2
        self.play(self.spring.oscillate(tmp_oscillate))
        self.my_next_section(type=pst.SUB_NORMAL)

        self.const_arrows = False
        self.mech_force.suspend_updating()
        self.force_e.suspend_updating()
        self.play(self.mech_force.animate.put_start_and_end_on(*self.get_mech_force_size()))
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(self.force_e.animate.put_start_and_end_on(*self.get_e_force_size()))
        self.my_next_section(type=pst.SUB_NORMAL)

        self.mech_force.resume_updating()
        self.force_e.resume_updating()
        self.play(self.spring.oscillate(1 - tmp_oscillate))
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Unwrite(eq4), Unwrite(eq_mech))

    def play_g0(self):
        for mob_d_0 in self.shift_d0_info:
            self.system.remove(mob_d_0)
        self.play(FadeOut(self.shift_d0_info))
        self.play(self.group_optomechanic_system.animate.to_edge(DOWN, buff=0.1))
        self.my_next_section("g0 Scene", type=pst.SUB_SKIP)
        title_go = Tex("What is $g_{0}$?").scale_to_fit_width(config.frame_width * 0.8).next_to(
            self.group_optomechanic_system, UP, buff=1.4)
        self.play(Write(title_go))
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Unwrite(title_go))

        ax = Axes(x_range=(0, 10), y_range=[0, 1, 0.1], x_length=round(config.frame_width) - 5,
                  y_length=round(config.frame_height - self.group_optomechanic_system.height) * 0.6,
                  y_axis_config={"numbers_to_include": np.arange(0, 1 + 0.1, 0.5)})
        ax += ax.get_y_axis_label(MathTex(r"\frac{E_{mech}}{E_{elec}}"), edge=LEFT, direction=LEFT * 2, buff=2)
        ax += ax.get_x_axis_label(MathTex("t"), edge=DOWN, direction=DOWN)
        ax.center().next_to(self.group_optomechanic_system, UP)

        g0_tracker = ValueTracker(3)
        tau_tracker = ValueTracker(3)
        exp_func = lambda x: np.exp(-x / tau_tracker.get_value())

        energy_func = lambda t: (np.sin(g0_tracker.get_value() * t) + 1) * exp_func(t) / 2

        energy_graph = always_redraw(lambda: ax.plot(energy_func, color=BLUE, z_index=2))

        def get_exp_plot():
            tmp = ax.plot(exp_func, color=YELLOW)
            b = DashedVMobject(tmp, num_dashes=16, fill_opacity=0.7, stroke_opacity=0.5, background_stroke_opacity=0.5)
            return b

        exp_graph = always_redraw(lambda: ax.plot(exp_func, color=YELLOW))
        exp_graph_dash = always_redraw(get_exp_plot)

        ax += always_redraw(
            lambda: ax.get_T_label(x_val=tau_tracker.get_value(), graph=exp_graph, label=MathTex(r"\tau", color=YELLOW),
                                   line_func=DashedLine, label_color=YELLOW, line_color=WHITE))
        self.play(Create(ax), Create(exp_graph_dash), Create(energy_graph))

        g0_digit = DecimalNumber(g0_tracker.get_value() / 7 * 210, unit="[Hz]")
        g0_tex = MathTex("g_{0}=", color=GREEN).scale(1.2)
        g0_tex_group = VGroup(g0_tex, g0_digit).arrange(RIGHT).to_edge(UR, buff=0.4)
        tau_tex = MathTex(r"\tau=", color=YELLOW).scale(1.2)
        tau_digit = DecimalNumber(tau_tracker.get_value() / 7 * 10, unit="[ms]")

        g0_digit.add_updater(lambda d: d.set_value(g0_tracker.get_value() / 7 * 210))
        tau_digit.add_updater(lambda d: d.set_value(tau_tracker.get_value() / 7 * 10))

        tau_tex_group = VGroup(tau_tex, tau_digit).arrange(RIGHT).next_to(g0_tex_group, DOWN)
        self.play(Write(g0_tex_group), Write(tau_tex_group))
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)

        one_calc_graph = ax.plot(energy_func, color=RED, z_index=4,
                                 x_range=[0, 4.5 * g0_tracker.get_value() / (2 * PI)])
        self.play(Create(one_calc_graph))
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Uncreate(one_calc_graph))
        self.my_next_section(type=pst.SUB_NORMAL)

        g0_init = g0_tracker.get_value()
        tau_init = tau_tracker.get_value()
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(tau_tracker.animate.set_value(tau_init + 6), run_time=6)
        self.play(tau_tracker.animate.set_value(tau_init + 4), run_time=6)
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)

        self.play(g0_tracker.animate.set_value(g0_init + 4), run_time=6)
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Unwrite(g0_tex_group), Unwrite(tau_tex_group))
        self.play(Uncreate(ax), Uncreate(exp_graph_dash), Uncreate(energy_graph))

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
        self.system = VGroup(self.spring, self.wall, self.mass).center()

    def get_electric_field(self):
        size = np.sin(self.spring.t) * 2
        color = BLUE if size <= 0 else RED
        y_additions = np.array([0.3, -0.5])
        x_additions = np.array([0.4, -1])
        field_x_range = np.array([self.capacitor.get_right()[0], self.mass.get_left()[0]])
        field_y_range = np.array([self.mass.get_bottom()[1], self.mass.get_top()[1]])
        return ArrowVectorField(lambda pos: LEFT * size, color=color, x_range=(field_x_range + x_additions).tolist(),
                                y_range=(field_y_range + y_additions).tolist())

    def draw_wall(self, pivot_mobject: Mobject, wall_len=2):
        color = WHITE
        wall = VGroup(
            DashedLine(start=wall_len * LEFT * 0.95, end=(wall_len) * RIGHT * 0.95, dashed_ratio=1.3, dash_length=0.6,
                color=GREY, stroke_width=8).shift(pivot_mobject.get_start()[1] * UP))
        [i.rotate(PI / 4, about_point=i.get_start()) for i in wall[0].submobjects]
        wall.add(Line(wall_len * LEFT, wall_len * RIGHT, color=color, stroke_width=18).align_to(wall, DOWN))

        return wall.rotate(-PI / 2).next_to(pivot_mobject.get_right(), RIGHT, buff=0)


class TheoryToPracti(ThreeDScene):
    def __init__(self, **kwargs):
        self.cut_axes_at_radius = False
        self.reso = [37, 37] if PRESENTATION_MODE else [3, 3]
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
            self.renderer = CairoRenderer(camera_class=self.camera_class, skip_animations=self.skip_animations, )

        low_quality_config = {"camera_config": {"should_apply_shading": False},
            "three_d_axes_config": dict(num_axis_pieces=1, **self.three_d_axes_config)}
        super().__init__(three_d_axes_config=self.three_d_axes_config, low_quality_config=low_quality_config, **kwargs)

    def get_basic_coords_config(self):
        epsilon = 0.01
        factor = 2
        factor_range = factor * 1
        factor_range = factor * 2
        addition = 0.5 if BEAUTY_PLANE else 0
        self.basic_coords_config = {"x_range": (-round(config["frame_y_radius"] * factor_range) - addition - epsilon,
                                                round(config["frame_y_radius"] * factor_range) + addition + epsilon),
            "y_range": (-round(config["frame_y_radius"] * factor_range) - addition - epsilon,  # "frame_y_radius"=4
                        round(config["frame_y_radius"] * factor_range) + addition + epsilon),  # "frame_height"=8
            "x_length": round(config["frame_height"] * factor), "y_length": round(config["frame_height"] * factor)}
        self.three_d_axes_config = dict(stroke_opacity=0.4,
                                        axis_config=dict(stroke_width=2, include_ticks=False, include_tip=False,
                                                         line_to_number_buff=SMALL_BUFF, label_direction=DR,
                                                         font_size=24), **self.basic_coords_config)

    def get_axes(self) -> ThreeDAxes:
        """Return a set of 3D axes.

        Returns
        -------
        :class:`.ThreeDAxes`
            A set of 3D axes.
        """
        axes = ThreeDAxes(**self.three_d_axes_config)
        return axes

    def build_axes(self):
        self.axes = self.get_axes()
        self.plane = NumberPlane(**self.basic_coords_config, faded_line_ratio=2 if BEAUTY_PLANE else 1)
        self.axes.move_to(self.plane.c2p(0, 0, 0)).set_opacity(0)

        for line in self.plane.background_lines:
            line.set_z_index_by_z_coordinate()
        for line in self.plane.faded_lines:
            line.set_z_index_by_z_coordinate()
        self.plane.set_z_index_by_z_coordinate()
        self.plane[0].set_z_index_by_z_coordinate()
        self.plane[1].set_z_index_by_z_coordinate()
        self.x_axis, self.y_axis = self.plane.axes
        self.space = VGroup(self.axes, self.plane)

    def get_drum(self):
        self.plane.z_normal = Z_AXIS
        R_factor = self.plane.p2c([self.drum_2d.height / 2, 0, 0])[0]
        drum = Drum(bessel_order=1, mode=2, axes=self.axes, R=R_factor,
                    d_0=self.axes.p2c(self.drum_2d.get_left() - self.drum_2d.depth / 2 * OUT)[2],
                    amplitude=R_factor * 0.3 * 0.8, z_index=Z_FACTOR + 4, stroke_width=1, stroke_color=BLUE_A,
                    resolution=self.reso, sheen_factor=0.5, sheen_direction=self.axes.c2p(*(DOWN * 4)))
        return drum

    def move_camera_comp(self, **kwargs):
        if config.renderer == "opengl":
            if "zoom" in kwargs:
                del kwargs["zoom"]
        self.space.set_z_index_by_z_coordinate()
        self.space[1].set_z_index_by_z_coordinate()
        self.space[0].set_z_index_by_z_coordinate()
        self.move_camera(**kwargs)

    def get_camera_position(self):
        if config.renderer == "opengl":
            return [75 * DEGREES, -30 * DEGREES, 0]
        return dict(phi=self.camera.get_phi(), theta=self.camera.get_theta(), zoom=self.camera.get_zoom())

    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        self.my_next_section("3D Drums", type=pst.SKIP)
        self.zoom = 2
        self.set_camera_orientation(phi=90 * DEGREES, theta=180 * DEGREES, gamma=-90 * DEGREES, zoom=self.zoom)

        self.build_axes()
        self.draw_spring_system()
        self.spring_system_2d.move_to(self.plane.c2p(0, 0, 0))
        self.space.move_to(self.capacitor_2d.get_left()).set_z(
            self.capacitor_2d.get_center()[2] - self.capacitor_2d.depth / 2)
        self.capacitor_3d.move_to(self.plane.c2p(0, 0, 0))
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)

        self.add(self.space)
        self.move_camera_comp(phi=90 * DEGREES, theta=210 * DEGREES, gamma=0,
                              frame_center=self.plane.get_center() + OUT * 2.8, zoom=1)
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(FadeOut(self.field), self.spring_system_2d[0].oscillate(1, about_edge=OUT))
        self.play(self.spring_system_2d[0].oscillate(0.25, about_edge=OUT, amplitude=2.2, new_oscillate=False))

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(*[FadeOut(mob) for mob in self.spring_system_2d if
                    mob not in {self.capacitor_2d, self.drum_2d, self.field}])
        self.renderer.camera.light_source.move_to((6 * DOWN - 7 * LEFT + 7 * OUT) * 4)
        drum = self.get_drum()
        self.drum = drum
        self.move_camera_comp(phi=81 * DEGREES, theta=222 * DEGREES,
                              frame_center=self.drum.get_center() + self.axes.c2p(
                                  *(self.drum.d_0 * OUT)) * 0.12 + LEFT * 0.34, zoom=4.1)
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(ReplacementTransform(self.drum_2d, self.drum),
                  ReplacementTransform(self.capacitor_2d, self.capacitor_3d))
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_NORMAL)
        new_d_0 = drum.R * 0.17
        self.play(drum.animate.set_z(self.axes.c2p(*(new_d_0 * OUT))[2]))
        drum.d_0 = new_d_0
        self.wait(0.4)
        self.my_next_section(type=pst.SUB_COMPLETE_LOOP)
        self.play(drum.vibrate(1))
        self.wait(0.001)
        self.my_next_section("Vibrate drum", pst.SUB_SKIP)
        self.play(drum.vibrate(0.25))
        self.play(Unwrite(drum))
        self.play(Unwrite(self.capacitor_3d), Unwrite(self.space))
        self.wait(0.1)

    def draw_spring_system(self):
        self.spring_system_2d = get_spring_system().center().scale_to_fit_width(config.frame_width * 0.8).scale(
            1 / self.zoom).rotate(PI / 2, DOWN)
        drum_2d = self.spring_system_2d[2]
        capacitor_2d = self.spring_system_2d[3].set_opacity(1)
        self.field = self.spring_system_2d[4]

        drum_3d = Circle(radius=drum_2d.height / 2, color=drum_2d.get_fill_color(), fill_opacity=1).rotate(PI / 2, UP)
        drum_2d.add_updater(lambda mob1: mob1.next_to(self.spring_system_2d[0].get_start(), IN, buff=0))
        drum_3d.add_updater(lambda mob2: mob2.next_to(self.spring_system_2d[0].get_start(), IN, buff=0))
        capacitor_3d = Circle(radius=capacitor_2d.height / 2, color=capacitor_2d.get_fill_color(),
                              fill_opacity=1).move_to(capacitor_2d.get_left())
        self.drum_3d = drum_3d
        self.drum_2d = drum_2d
        self.capacitor_3d = capacitor_3d
        self.capacitor_2d = capacitor_2d
        self.play(Create(self.spring_system_2d))


class FirstSimuTry(ThreeDScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parts_num = 3
        self.current_part = 0

    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.wait(0.3)
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def get_dt_lines(self, start, end, numbers, color):
        len_line = end[0] - start[0]
        len_line += len_line / numbers
        dt_lines = VGroup(
            DashedLine(start=start, end=start + RIGHT * len_line, dashed_ratio=1, dash_length=(len_line / numbers),
                color=color, stroke_width=5))
        [i.rotate(PI / 2, about_point=i.get_start()) for i in dt_lines[0].submobjects]
        return dt_lines

    def construct(self):
        # infinity_time = Tex(r"Numeric run time $=\ \infty$").scale(1.4)
        # self.play(Write(infinity_time))
        # self.play(infinity_time.animate.to_edge(UP))
        self.remove_at_end = VGroup()
        self.my_next_section("Numeric run time")
        self.play_freq_graphs()
        self.play(Unwrite(self.remove_at_end))
        self.wait(0.5)

    def get_system_recap(self):
        system = get_spring_system()
        remind_square = Square(color=YELLOW).match_width(system, stretch=True).match_height(system, stretch=True).scale(
            1.2).move_to(system.get_center())
        return VGroup(system, remind_square)

    def play_freq_graphs(self):
        system = self.get_system_recap().center().scale_to_fit_height(config.frame_height * 0.45).shift(DOWN * 0.5)
        self.remove_at_end += system
        reminder = Text("Reminder").next_to(system.get_top(), UP)
        self.play(FadeIn(system), Write(reminder))

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(FadeOut(reminder, shift=DOWN))

        ax = Axes(x_range=(0, 10), y_range=[-1, 1], x_length=round(config.frame_width) - 2,
                  y_length=round(config.frame_height) * 0.75, tips=False).to_edge(LEFT, buff=0.2)
        ax += ax.get_x_axis_label(MathTex("t"), edge=DOWN, direction=DOWN)

        omega_mech = 0.7
        omega_lc = omega_mech * 4
        omega_mech_func = lambda t: np.sin(omega_mech * t)
        omega_lc_func = lambda t: 0.3 * np.sin(omega_lc * t)

        omega_mech_graph = ax.plot(omega_mech_func, color=GREEN, z_index=2)
        omega_lc_graph = ax.plot(omega_lc_func, color=BLUE, z_index=2)

        dt_omega_mech = self.get_dt_lines(ax.c2p(0, 0), ax.c2p(2 * PI / omega_mech, 0), 6, GREEN_B)
        dt_omega_mech.stretch_to_fit_height(dt_omega_mech.height * 0.3, about_edge=DOWN)
        dt_omega_lc = self.get_dt_lines(ax.c2p(0, 0), ax.c2p(2 * PI / omega_lc, 0), 6, BLUE_B).stretch_to_fit_height(
            dt_omega_mech.height, about_edge=DOWN)
        dt_omega_lc_full = self.get_dt_lines(ax.c2p(0, 0), ax.c2p(2 * PI / omega_mech, 0), 6 * omega_lc / omega_mech,
                                             BLUE_B).stretch_to_fit_height(dt_omega_mech.height, about_edge=DOWN)

        top_graph = ax.plot(lambda x: 0.9)
        t = ValueTracker(0)
        time_marker = ax.get_T_label(x_val=t.get_value(), graph=top_graph, line_func=DashedLine, label_color=YELLOW,
                                     line_color=YELLOW)

        omega_lc_label = MathTex(r"\omega_{LC}").next_to(omega_mech_graph, UL)
        omega_lc_label = VGroup(omega_lc_label, Line(color=BLUE).scale(0.4)).arrange(RIGHT).to_edge(DR, buff=1.2)
        omega_mech_label = MathTex(r"\Omega_{mech}").next_to(omega_mech_graph, UR)
        omega_mech_label = VGroup(omega_mech_label, Line(color=GREEN).scale(0.4)).arrange(RIGHT).next_to(omega_lc_label,
            UP)
        max_mech_point = ax.c2p(PI / (omega_mech * 2), omega_mech_func(omega_mech * 2))

        self.play(
            system.animate.set_x(max_mech_point[0]).set_y((system.height * 0.8 - config.frame_height) / 2).scale(0.7))

        self.play(Create(ax))
        self.remove_at_end += ax
        self.play(Create(omega_mech_graph), Write(omega_mech_label))
        self.remove_at_end += omega_mech_graph
        self.remove_at_end += omega_mech_label

        self.play(Create(time_marker))
        self.remove_at_end += time_marker
        self.play(t.animate.set_value(2 * PI / omega_mech))

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Create(dt_omega_mech))

        dt_brace_1, dt1text = self.get_dt_braces(dt_omega_mech)
        dt_brace_2, dt2text = self.get_dt_braces(dt_omega_lc)

        self.play(Write(dt_brace_1), Write(dt1text))

        self.my_next_section(type=pst.SUB_NORMAL)
        for mob in dt_omega_mech[0].submobjects:
            self.play(time_marker.animate.match_x(mob))
            self.wait(0.2)

        self.play(time_marker.animate.set_x(ax.get_origin()[0]))

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Create(omega_lc_graph), Write(omega_lc_label))
        self.remove_at_end += omega_lc_graph
        self.remove_at_end += omega_lc_label

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Create(dt_omega_lc))

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(TransformMatchingTex(dt1text, dt2text), ReplacementTransform(dt_brace_1, dt_brace_2))
        self.remove_at_end += dt_brace_2
        self.remove_at_end += dt2text

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(FadeOut(dt_omega_lc), FadeOut(dt_omega_mech))
        self.play(Create(dt_omega_lc_full))
        self.my_next_section(type=pst.SUB_NORMAL)
        self.remove_at_end += dt_omega_lc_full

    def get_dt_braces(self, dt_line):
        line = Line(dt_line[0].submobjects[0].get_start(), dt_line[0].submobjects[1].get_start())
        dt_brace = Brace(line, color=YELLOW)
        b1text = dt_brace.get_tex("dt")
        b1text.set_color(YELLOW)
        return dt_brace, b1text


class ComsolEigenmodes(Scene):
    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        title = Text("COMSOL Eigenmodes").scale_to_fit_width(config.frame_width * 0.8).to_edge(UP)
        small_image_size = config.frame_height * 0.2
        large_image_size = config.frame_height * 0.8
        images_eigen = Group(*[ImageMobject(str(RESOURCE_DIR / f"simulation_mode_{x}.png")) for x in range(1, 3)])
        images_eigen_side = Group(
            *[ImageMobject(str(RESOURCE_DIR / f"simulation_mode_{x}_d.png")) for x in range(1, 4)])
        images_eigen_arrange = Group(*[im.copy().scale_to_fit_height(small_image_size) for im in images_eigen]).arrange(
            RIGHT).next_to(title, DOWN, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * 0.5)
        images_eigen_side_arrange = Group(
            *[im.copy().scale_to_fit_height(small_image_size) for im in images_eigen_side]).arrange(RIGHT).next_to(
            images_eigen_arrange, DOWN, buff=0)
        self.my_next_section("COMSOL Eigenmodes")
        title.center()
        self.play(Write(title))
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(title.animate.to_edge(UP))

        large_image_y = -(images_eigen_side_arrange.get_bottom()[1] + config.frame_height / 2) / 2
        for idx, image in enumerate(images_eigen):
            image.scale_to_fit_height(large_image_size).set_y(large_image_y)
            self.play(FadeIn(image))
            self.my_next_section(type=pst.SUB_NORMAL)
            self.play(ReplacementTransform(image, images_eigen_arrange[idx]))

        for idx, image in enumerate(images_eigen_side):
            image.scale_to_fit_height(large_image_size).set_y(large_image_y)
            self.play(FadeIn(image))
            self.my_next_section(type=pst.SUB_NORMAL)
            self.play(ReplacementTransform(image, images_eigen_side_arrange[idx]))

        self.play(Group(images_eigen_side_arrange, images_eigen_arrange).animate.scale_to_fit_height(
            0.9 * (config.frame_height - title.height)).set_y(
            title.get_bottom()[1] - (config.frame_height - title.height) / 2))
        self.my_next_section(type=pst.SUB_NORMAL)


class DissipationDilution(Scene):
    def my_next_section(self, name: str = "unnamed", type: str = pst.NORMAL, skip_animations: bool = False):
        if PRESENTATION_MODE:
            self.next_section(name, type, skip_animations)
        else:
            self.wait()

    def construct(self):
        self.create_system()
        self.my_next_section("Dissipation Dilution")
        self.play(DrawBorderThenFill(self.system))
        self.mass = OscillateMobject(self.mass)
        self.play_parallel_shift()
        self.play_vertical_shift()
        self.play(Unwrite(self.system))
        self.wait(0.1)

    def play_parallel_shift(self):
        self.wait(0.1)
        self.my_next_section(type=pst.SUB_COMPLETE_LOOP)
        self.play(self.mass.oscillate(1, oscillate_direction=RIGHT))
        self.wait(0.001)
        self.my_next_section(type=pst.SUB_SKIP)
        self.play(self.mass.oscillate(0.25, oscillate_direction=RIGHT, new_reference_point=False))

        x_shift_brace, x_label = self.get_and_brace(self.mass.reference_point, self.mass.get_center(), r"\Delta x",
                                                    shift_size=(self.mass.width / 2 + 0.2) * DOWN)
        y_for_l_0 = x_shift_brace.get_bottom()[1]

        l_0_brace, l_0_label = self.get_and_brace(np.array([self.left_side[1].get_right()[0], y_for_l_0, 0]),
                                                  np.array([x_shift_brace.get_left()[0], y_for_l_0, 0]), "l_0")
        delt_x_brace, delta_x_label = self.get_and_brace(
            np.array([self.mass.reference_point[0], self.mass.get_top()[1], 0]),
            np.array([self.mass.get_center()[0], self.mass.get_top()[1], 0]), r"\Delta x", brace_color=RED, direc=UP)
        labels = VGroup(x_label, l_0_label, delta_x_label)
        braces = VGroup(x_shift_brace, l_0_brace, delt_x_brace)
        self.play(Write(labels), Write(braces))
        self.wait(0.2)
        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Unwrite(labels), Unwrite(braces))
        self.play(self.mass.oscillate(0.25, oscillate_direction=RIGHT, new_reference_point=False))
        self.wait(0.2)
        self.my_next_section(type=pst.SUB_NORMAL)

    def play_vertical_shift(self):
        self.play(self.mass.oscillate(0.75))
        y_shift_brace, y_label = self.get_and_brace(
            np.array([self.left_side[1].get_bottom()[1], self.mass.get_bottom()[1], 0]),
            np.array([self.mass.get_bottom()[1], self.mass.get_bottom()[1], 0]), r"\Delta y")
        y_shift_brace.rotate(PI / 2).set_x(self.mass.get_right()[0] + 0.3).set_y(self.left_side[1].get_bottom()[1] + (
                self.mass.get_bottom()[1] - self.left_side[1].get_bottom()[1]) / 2 - 0.3)
        y_for_l_0 = y_shift_brace.get_bottom()[1]

        l_0_brace, l_0_label = self.get_and_brace(np.array([self.left_side[1].get_right()[0], y_for_l_0, 0]),
                                                  np.array([self.mass.get_center()[0], y_for_l_0, 0]), "l_0")
        delt_x_brace, delta_x_label = self.get_and_brace(self.left_side[0].get_start(), self.left_side[0].get_center(),
                                                         r"\Delta x", brace_color=RED, direc=UP)
        VGroup(delt_x_brace, delta_x_label).rotate(self.left_side[0].orig_angle + PI).shift(UP * 0.2, LEFT * 0.2)
        labels = VGroup(y_label, l_0_label, delta_x_label)
        braces = VGroup(y_shift_brace, l_0_brace, delt_x_brace)
        self.play(Write(labels), Write(braces))
        aprox_tex = MathTex(r"\Delta x \approx\frac{\Delta y^{2}}{2l_{0}}", color=RED).scale(1.5).to_edge(DOWN,
                                                                                                          buff=0.3)
        self.play(Write(aprox_tex))

        self.my_next_section(type=pst.SUB_NORMAL)
        self.play(Unwrite(labels), Unwrite(braces), Unwrite(aprox_tex))
        self.play(self.mass.oscillate(0.25, new_reference_point=False))

    def get_and_brace(self, start, end, text, brace_color=WHITE, shift_size=0 * RIGHT, direc=DOWN):
        ret_brace = BraceBetweenPoints(start, end, color=brace_color, direction=direc)
        b1text = ret_brace.get_tex(text).set_color(brace_color)
        VGroup(b1text, ret_brace).shift(shift_size)
        return ret_brace, b1text

    def create_system(self):
        spring_len = 6
        right_spring = Spring(spring_len / 2 * LEFT, length=spring_len, stroke_width=5)
        right_spring.set_color(YELLOW)
        right_wall = draw_wall(right_spring.right_spring)
        self.right_side = right_side = VGroup(right_spring, right_wall)

        mass = Rectangle(height=right_wall.height, width=1, fill_color=BLUE, stroke_color=BLUE,
                         fill_opacity=0.6).next_to(right_spring.get_start(), LEFT, buff=0)
        # self.mass = OscillateMobject(mass)
        self.mass = mass
        system = VGroup(mass, right_spring, right_wall)

        left_spring = right_spring.copy()
        left_wall = right_wall.copy()
        left_spring.orig_angle = angle_between_vectors(left_wall.get_right(), mass.get_left())
        right_spring.orig_angle = angle_between_vectors(right_wall.get_left(), mass.get_right())

        self.left_side = left_side = VGroup(left_spring, left_wall).rotate(PI, UP)
        system.next_to(left_spring.get_start(), RIGHT, buff=0)
        system += left_spring
        system += left_wall
        system.stretch_to_fit_width(config.frame_width * 0.9).stretch_to_fit_height(system.height * 0.4).center()
        self.system = system

        def update_spring(spring_update):
            if spring_update.get_x() < mass.get_x() or left_spring == spring_update:
                wall_point = left_wall.get_right()
                mass_point = mass.get_left()
                side = LEFT
            else:
                wall_point = right_wall.get_left()
                mass_point = mass.get_right()
                side = LEFT

            dist = np.linalg.norm(mass_point - wall_point)
            spring_update.rotate(-spring_update.orig_angle, about_point=mass_point)
            spring_update.stretch_to_fit_width(dist)
            spring_update.next_to(mass_point, -side, buff=0)
            spring_update.rotate(spring_update.orig_angle, about_point=mass_point)
            addition_angle = np.arctan2(wall_point[1] - mass_point[1],
                                        wall_point[0] - mass_point[0]) - spring_update.orig_angle
            spring_update.orig_angle += addition_angle
            spring_update.rotate(addition_angle, about_point=mass_point)

        right_spring.add_updater(update_spring)
        left_spring.add_updater(update_spring)


class Comsol(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        device_image = ImageMobject(str(RESOURCE_DIR / "device.png")).scale_to_fit_height(
            config.frame_height * 0.7).shift(DOWN * 0.5)
        comsol_image = ImageMobject(str(RESOURCE_DIR / "comsol.png")).scale_to_fit_height(config.frame_height * 0.6)
        mesh_image = ImageMobject(str(RESOURCE_DIR / "mesh.png"))
        title1 = Text("Complicated Physics...").scale_to_fit_width(config.frame_width * 0.5).to_edge(UP).scale(1.3)
        title2 = Text("Solution:").to_edge(UP).scale(1.3)
        self.play(Write(title1),
                  FadeIn(device_image.scale_to_fit_height((title1.get_bottom()[1] - config.bottom[1]) * 0.8)))
        self.next_section(pst.SUB_NORMAL)
        self.play(Unwrite(title1, run_time=0.1), FadeOut(device_image))
        self.play(Write(title2), FadeIn(comsol_image))
        self.next_section(pst.SUB_NORMAL)
        self.play(comsol_image.animate.shift(LEFT * 3),
                  FadeIn(mesh_image.shift(RIGHT * 3).scale_to_fit_height(device_image.height)))


class Results(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        # t0 = Table(
        #     [["1", "2", "3"],
        #      ["4","5", "6"]],
        #     row_labels=[Text("freq = ___"), Text("R2")],
        #     col_labels=[Text("Analytical g_{0}"), Text("Numeric g_{0}"), Text("Observed g_{0}")],
        #     top_left_entry=Text("TOP")).scale(0.5)
        t0 = MathTable([["1", "2", "3"], ["4", "5", "6"]], row_labels=[MathTex("freq = ___"), MathTex("R2")],
            col_labels=[MathTex("Analytical g_{0}"), MathTex("Numeric g_{0}"), MathTex("Observed g_{0}")],
            top_left_entry=Text("TOP")).scale(0.5)
        t0.add_highlighted_cell((2, 2), color=GREEN)
        title = Text("Results")
        self.play(Write(title), title.animate.to_edge(UP))
        self.wait(1)
        self.play(FadeIn(t0))


class Conclusion(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def construct(self):
        title = Text("Conclusion:")
        # a = Text("Developing theory and analytics behind the study")
        # b = Text("Simulation of realistic physics - not what we thought")
        # c = Text("Results - The project was completed for a basic case")
        blist = BulletedList("Developing theory and analytics behind the study",
                             "Simulation of realistic physics - not what we thought",
                             "Results - The project was completed for a basic case", height=13, width=13)
        self.play(Write(title), title.animate.to_edge(UP))
        self.wait(0.5)
        self.play(Create(blist))


# scenes_lst = [IntroSummary, HistoryBrief, SpringScene, TheoryToPracti, IntroSummary2, FirstSimuTry,
#               ComsolEigenmodes, DissipationDilution, IntroSummary3, Comsol, Results, Conclusion]
scenes_lst = [Conclusion]

for sc in scenes_lst:
    # try:
    disable_caching = sc in {DissipationDilution} or isinstance(sc, IntroSummary)
    quality = "fourk_quality" if PRESENTATION_MODE else "low_quality"
    # quality = "low_quality"
    with tempconfig({"quality": quality, "preview": True, "media_dir": MAIN_PATH / "media", "save_sections": True,
                     "disable_caching": disable_caching}):
        scene = sc()
        scene.render()  # except:  #     continue
