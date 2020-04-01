import sys
sys.path.append("../src")
from gerber_line import GerberLine

def test_line_type():
    line = GerberLine("X79019Y18669D02*")
    assert line.line_is_command() == True
    assert line.line_is_basic_ap_def() == False
    assert line.line_is_scale() == False
    line = GerberLine("%ADD19C,0.254*%")
    assert line.line_is_command() == False
    assert line.line_is_basic_ap_def() == True
    assert line.line_is_scale() == False
    line = GerberLine("%FSLAX43Y43*%")
    assert line.line_is_command() == False
    assert line.line_is_basic_ap_def() == False
    assert line.line_is_scale() == True
    print ("sucess on test_line_type")

def test_get_var_dec_value():
    line = GerberLine("X79019Y18669D01*")
    assert line.get_var_dec_value("X") == 79019
    assert line.get_var_dec_value("Y") == 18669
    assert line.get_var_dec_value("D") == 1
    assert line.get_var_dec_value("Z") == None
    line = GerberLine("X-00238973Y-00044353D03*")#test line with negative cordinates
    assert line.get_var_dec_value("X") == -238973
    assert line.get_var_dec_value("Y") == -44353
    assert line.get_var_dec_value("D") == 3
    print ("sucess on test_get_var_dec_value")

def check_float_list(actual, expected):
    assert len(expected) == len(actual)
    for ind in range(len(actual)):
        assert actual[ind] >= 0.99 * expected[ind] and actual[ind] <= 1.01 * expected[ind]
    
def test_get_real_values_line_def():
    line = GerberLine("X79019Y18669D01*")
    assert line.get_real_values_line_def() == None
    line = GerberLine("%ADD60C,0.406*%")
    check_float_list([0.406], line.get_real_values_line_def())
    line = GerberLine("%ADD17P,.040X6X0.0X0.019*%")
    check_float_list([0.04, 6.0, 0.0, 0.019], line.get_real_values_line_def())
    line = GerberLine("%ADD22O,0.046X0.026X0.019*%")
    check_float_list([0.046, 0.026, 0.019], line.get_real_values_line_def())
    print ("sucess on test_get_real_values_line_def")
    
    

if __name__ == '__main__':
    test_line_type()
    test_get_var_dec_value()
    test_get_real_values_line_def()