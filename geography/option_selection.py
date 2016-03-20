from proso.models.option_selection import OptionsNumber


class PartialyFourOptionsNumber(OptionsNumber):
    def compute_number_of_options(self, target_probability, prediction):
        if prediction >= target_probability:
            return 0
        else:
            return 3
