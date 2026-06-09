from time import perf_counter


class Timer:
    def __init__(self):
        self.start = perf_counter()

    def elapsed_ms(self):
        return round(
            (perf_counter() - self.start)*1000, 2
        )
