class FeedbackProcessor:
    """
    Feedback Processor (FPM) - A general adaptive system loop
    Author: John Carroll, Two Mile Solutions LLC
    """

    def __init__(self, goal_fn, adjust_fn):
        self.goal_fn = goal_fn
        self.adjust_fn = adjust_fn

    def step(self, input_data):
        output = self.goal_fn(input_data)
        feedback = self.observe(output)
        self.adjust_fn(feedback)
        return output

    def observe(self, output):
        return {"quality": self.goal_fn.__name__, "value": output}