from manim import *
from copy import deepcopy


class Count(Animation):
    """
    Example:
    class CountingScene(Scene):
    def construct(self):
        tex = Text("Some")
        number = DecimalNumber().set_color(WHITE).scale(5)
        number.add_updater(lambda number: number.move_to(ORIGIN))  # avoid moving number
        self.add(tex)
        self.add(number)
        # Play the Count Animation to count from 0 to 100 in 4 seconds
        self.play(Count(number, 0, 100), run_time=4, rate_func=linear)
    """

    def __init__(self, number: DecimalNumber, start: float, end: float, **kwargs) -> None:
        # Pass number as the mobject of the animation
        super().__init__(number, **kwargs)
        # Set start and end
        self.mobject_copy = deepcopy(self.mobject)
        self.start = start
        self.end = end

    def interpolate_mobject(self, alpha: float) -> None:
        # Set value of DecimalNumber according to alpha
        value = self.start + (alpha * (self.end - self.start))
        self.mobject.set_value(value).move_to(
            self.mobject_copy).rotate(50 * DEGREES, RIGHT).scale_to_fit_height(self.mobject_copy.height)
        # self.mobject.set_value(value)
