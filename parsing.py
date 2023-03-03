from plusminus import ArithmeticParser, safe_pow
from datetime import datetime
import regex as re

class EviewsParser(ArithmeticParser):
    def customize(self):

        def dateval_func(date):
            date = re.sub(':', 
                          '',
                          date)
            return int(date)
        
        def recode_func(condition,
                        true_result,
                        false_result):
            
            if condition == True:
                return true_result
            else:
                return false_result


        '''
        def fv(pv, rate, n_periods):
            return pv * safe_pow(1 + rate, n_periods)

        def pp(pv, rate, n_periods):
            return rate * pv / (1 - safe_pow(1 + rate, -n_periods))
        '''
        super().customize()
        '''
        self.add_operator("of", 2, ArithmeticParser.LEFT, lambda a, b: a * b)
        self.add_operator('%', 1, ArithmeticParser.LEFT, lambda a: a / 100)
        self.add_function('PV', 3, pv)
        self.add_function('FV', 3, fv)
        self.add_function('PP', 3, pp)
        '''

        #gets current year and month
        self.initialize_variable('date', int(str(datetime.now().year) + str('{:02d}'.format(datetime.now().month))))
        self.add_function('dateval', 1, dateval_func)
        self.add_function('recode', 3, recode_func)
        


parser = EviewsParser()
parser.runTests("""\
    
    date
    7 == 5
    dateval("2011:12")
    recode(7 <= 7, 1, 0)
    recode(date <= dateval("2023:02"), 1 , 0)
    recode(date == dateval("2023:03"), 1 , 0)
    recode(date <= dateval("2029:03"), 1 , 0)
    """,
    postParse=lambda _, result: result[0].evaluate()
)

#%% cleaning prior to 
import regex as re
def clean_equation(equation):
    equation = re.sub('@',
                    '',
                    equation)
    equation = re.sub('\s+',
                      ' ',
                      equation)
    equation = re.sub('date = ',
            'date == ',
            equation)
    equation = re.sub('""',
                      '"',
                      equation)
    return equation


clean_equation('@recode(@date  = @dateval(""2009:04"")')

# %%
