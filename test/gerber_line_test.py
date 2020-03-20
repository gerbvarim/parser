import sys
sys.path.append("../src")
from gerber_line import GerberLine

def test_is_command():
    line = GerberLine("X79019Y18669D02*")
    assert line.line_is_command() == True
    line = GerberLine("%ADD19C,0.254*%")
    assert line.line_is_command() == False
    print ("sucess on test_is_command")

def test_get_var_dec_value():
    line = GerberLine("X79019Y18669D01*")
    assert line.get_var_dec_value("X") == 79019
    assert line.get_var_dec_value("Y") == 18669
    assert line.get_var_dec_value("D") == 1
    assert line.get_var_dec_value("Z") == None
    line = GerberLine("%FSLAX43Y43*%")
    assert line.get_var_dec_value("X") == None
    line = GerberLine("X-00238973Y-00044353D03*")#test line with negative cordinates
    assert line.get_var_dec_value("X") == -238973
    assert line.get_var_dec_value("Y") == -44353
    assert line.get_var_dec_value("D") == 3
    print ("sucess on test_get_var_dec_value")
    
    

if __name__ == '__main__':
    test_is_command()
    test_get_var_dec_value()