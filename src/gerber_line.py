class GerberLine(object):
    """
    an object which represent a line in a gerber file.
    it should be able to do some basic processing on it.
    """

    def __init__(self, line_string):
        self.line_string = line_string
    
    def _dec_string_to_num(self, start_index):
        """
        read decimal value from the line string, starting at givven index.
        """
        digits = ['0','1','2','3','4','5','6','7','8','9']
        num = 0
        index = start_index
        neg_number = False
        if self.line_string[index] == '-':#if number is negative
            index += 1
            neg_number = True
            
        while index < len(self.line_string) and self.line_string[index] in digits:
            num = num * 10
            num += ord(self.line_string[index]) - ord('0')
            index += 1
        if neg_number:
            num = -1 * num
        return num
    
    def line_is_command(self):
        """
        check if the line is a gerber command.
        """
        return (self.line_string[0] != '%' and 'D' in self.line_string)
    
    def line_is_basic_ap_def(self):
        """
        check if the line is a basic definition command
        """
        return (self.line_string[0:4] == "%ADD")
        
    def line_is_scale(self):
        """
        check if the line is a basic definition command
        """
        return (self.line_string[0:5] == "%FSLA")
    
    def get_var_dec_value(self, var):
        """
        return the var value of a gerber line.
        if non-exist, return none.
        typical var for example is 'X', 'Y', 'D'
        """
        var_index = self.line_string.find(var)
        if var_index == -1:
            return None
        return self._dec_string_to_num(var_index + len(var))
    
    def get_real_values_line_def(self):
        """
        return all the real values of a basic definition line. return them in a list by order
        if non-exist, return none.
        """
        if not(self.line_is_basic_ap_def()):
            return None
        line_index = self.line_string.find('*')
        if line_index == -1:
            return None
        line_index -= 1
        results = []
        digits_of_float = ['0','1','2','3','4','5','6','7','8','9','.','X']
        accum_val = 0.0
        while self.line_string[line_index] in digits_of_float:
            if self.line_string[line_index] == 'X':#end of float
                results.append(accum_val)
                accum_val = 0.0
            elif  self.line_string[line_index] == '.':#not an actual digit, but still present
                if self.line_string[line_index -1] not in digits_of_float or self.line_string[line_index - 1] == 'X': # case of number termination without leading integer digits
                    accum_val = accum_val / 10.0
            else:
                accum_val = accum_val / 10.0
                accum_val += int(self.line_string[line_index])
            line_index -= 1
        
        results.append(accum_val)
        
        return results[::-1]#reverse order for getting numbers in order of appearance
        
        