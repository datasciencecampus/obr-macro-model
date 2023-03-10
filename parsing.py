from datetime import datetime

import regex as re
from plusminus import ArithmeticParser


class EviewsParser(ArithmeticParser):
    def customize(self):
        def dateval_func(date):
            date = re.sub(":", "", date)
            return int(date)

        def recode_func(condition, true_result, false_result):

            if condition == True:
                return true_result
            else:
                return false_result

        def d_function(variable_name: str):
            match = re.search("\d+", variable_name)
            if match:
                number = str(int(match[0]) + 1)
                previous_period = re.sub(match[0], number, variable_name)
            else:
                previous_period = "{}_minus1".format(variable_name)
            return self.evaluate(variable_name) - self.evaluate(previous_period)

        def dlog_function(variable_name: str):
            match = re.search("\d+", variable_name)
            if match:
                number = str(int(match[0]) + 1)
                previous_period = "log({})".format(
                    re.sub(match[0], number, variable_name)
                )
            else:
                previous_period = "log({}_minus1)".format(variable_name)
            return self.evaluate("log({})".format(variable_name)) - self.evaluate(
                previous_period
            )

        super().customize()
        """
        self.add_operator("of", 2, ArithmeticParser.LEFT, lambda a, b: a * b)
        self.add_operator('%', 1, ArithmeticParser.LEFT, lambda a: a / 100)
        self.add_function('PV', 3, pv)
        self.add_function('FV', 3, fv)
        self.add_function('PP', 3, pp)
        """

        # gets current year and month
        self.initialize_variable(
            "date",
            int(str(datetime.now().year) + str("{:02d}".format(datetime.now().month))),
        )
        self.add_function("dateval", 1, dateval_func)
        self.add_function("recode", 3, recode_func)
        self.add_function("d", 1, d_function)
        self.add_function("dlog", 1, dlog_function)


parser = EviewsParser()
parser["income_minus2"] = 9
parser["income_minus1"] = 10
parser["income"] = 6
parser.runTests(
    """\
    date
    7 == 5
    dateval("2011:12")
    recode(7 <= 7, 1, 0)
    recode(date <= dateval("2023:02"), 1 , 0)
    recode(date == dateval("2023:03"), 1 , 0)
    recode(date <= dateval("2029:03"), 1 , 0)
    d('income')
    dlog('income')
    d('income_minus1')
    dlog('income_minus1')
    """,
    postParse=lambda _, result: result[0].evaluate(),
)

#%% cleaning prior to
import regex as re


def clean_equation(equation):
    # remove @ as unable to parse
    equation = re.sub("@", "", equation)

    # remove more than single spaces
    equation = re.sub("\s+", " ", equation)

    # put double equals in date
    equation = re.sub("date = ", "date == ", equation)

    # remove double quotes
    equation = re.sub('""', '"', equation)

    # replace (-#) with _minus# unless it is being used as power e.g. ^(-#)
    equation = re.sub(r"(?<!\^)\(-(\d+)\)", r"_minus\1", equation)

    # put variable in d function in quotations
    equation = re.sub(r"d\((\w+)\)", r'd("\1")', equation)

    # put variable in dlog function in quotations
    equation = re.sub(r"dlog\((\w+)\)", r'dlog("\1")', equation)

    return equation


print(clean_equation("@d(income(-1))"))
print(clean_equation("@dlog(income(-1))"))
print(clean_equation("8^(-1)"))
print(clean_equation("9(-12)"))
print(clean_equation("dlog(GPW  / APH)"))
# %%
