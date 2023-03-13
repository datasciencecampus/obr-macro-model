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

        def create_previous_period_string(input_string: str):

            # defines the operators that may be present in d/dlog
            operators = ["*", "/"]

            input_tokens = input_string.split()
            input_token_previous_period = []

            # iterates though the tokens and changes to previous period
            for token in input_tokens:
                # searches for match in token of form minus#
                match = re.search("(?<=minus)(\d+)", token)
                if match:
                    number = str(int(match[0]) + 1)
                    previous_period = re.sub(match[0], number, token)
                elif token not in operators:
                    previous_period = "{}_minus1".format(token)
                else:
                    previous_period = token
                input_token_previous_period.append(previous_period)
            return " ".join(input_token_previous_period)

        def d_function(input_string: str):

            previous_period_string = create_previous_period_string(input_string)
            return self.evaluate(input_string) - self.evaluate(previous_period_string)

        def dlog_function(input_string: str):

            previous_period_string = create_previous_period_string(input_string)

            return self.evaluate("log({})".format(input_string)) - self.evaluate(
                "log({})".format(previous_period_string)
            )

        def eval_function(variable, date):

            return self.evaluate(variable + "_" + date)

        super().customize()

        # gets current year and month
        self.initialize_variable(
            "date",
            int(str(datetime.now().year) + str("{:02d}".format(datetime.now().month))),
        )
        self.add_function("dateval", 1, dateval_func)
        self.add_function("recode", 3, recode_func)
        self.add_function("d", 1, d_function)
        self.add_function("dlog", 1, dlog_function)
        self.add_function("elem", 2, eval_function)


parser = EviewsParser()
parser["income_minus2"] = 9
parser["income_minus1"] = 10
parser["income"] = 6
parser["PBRENT_2009Q3"] = 12

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
    d('income / income_minus1')
    dlog('income / income_minus1')
    elem("PBRENT" , "2009Q3")
    """,
    postParse=lambda _, result: result[0].evaluate(),
)

#%% cleaning prior to
import regex as re
from nltk.tokenize import word_tokenize


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
    equation = re.sub(r"d\((.+)\)", r'd("\1")', equation)

    # put variable in dlog function in quotations
    equation = re.sub(r"dlog\((.+)\)", r'dlog("\1")', equation)

    # put variable in elem function in quotations
    equation = re.sub(r"elem\((\w+)", r'elem("\1"', equation)

    return equation


print(clean_equation("@d(income(-1))"))
print(clean_equation("@dlog(income(-1))"))
print(clean_equation("8^(-1)"))
print(clean_equation("9(-12)"))
print(clean_equation("dlog(GPW  / APH)"))
print(clean_equation("@elem(dave, 'Q1_1970')"))
# %%
