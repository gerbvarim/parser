from gerber_line import GerberLine


def remove_list_duplicate(list_in):
    list_out = []
    for elem in list_in:
        if not(elem in list_out):
            list_out.append(elem)
    return list_out


class GerberAP(object):
    def __init__(self, x = 0, y = 0, type = 0):
        self.location = (x, y)
        self.type = type
        self.ap_connected_to = [self] 
        self.points_connected_to = []

class GerberAPCircle(object):
    def __init__(self, param_list):
        self.r = param_list[0] / 2.0#you get diameter, not a radius
    def point_in_ap(self, point_tuple):
        return (point_tuple[0]**2 + point_tuple[1]**2) <= self.r**2

class GerberAPRectangle(object):
    def __init__(self, param_list):
        self.width = param_list[0]
        self.height = param_list[1]
    def point_in_ap(self, point_tuple):
        return abs(point_tuple[0]) < self.width / 2 and abs(point_tuple[1]) < self.height / 2

class GerberAPObround(object):
    def __init__(self, param_list):
        self.width = param_list[0]
        self.height = param_list[1]
    def point_in_ap(self, point_tuple):
        return abs(point_tuple[0]) < self.width / 2 and abs(point_tuple[1]) < self.height / 2

def point_diff_by2(point1, point2):
    return (point1[0] - point2[0])**2 + (point1[1] - point2[1])**2
        
class GerberAPLine(object):
    """
    a line apature.
    needed because some points are connected from the middle of a line drawn.
    """
    def __init__(self, start_point, end_point, radius):
        self.radius = radius
        self.start_point = start_point
        self.end_point = end_point
    
    def find_closest_line_point(self, point):
        min_point = self.start_point
        max_point = self.end_point
        mid_point = None
        while abs(max_point[0] - min_point[0]) > 1 or  abs(max_point[1] - min_point[1]) > 1 :
            mid_point = ( (min_point[0] + max_point[0]) / 2, (min_point[1] + max_point[1]) / 2 )
            if point_diff_by2(min_point, point) > point_diff_by2(max_point, point):
                min_point = mid_point
            else:
                max_point = mid_point
        return min_point
    
    def point_in_ap(self, point_tuple):
        closest_point = self.find_closest_line_point(point_tuple)
        return point_diff_by2(closest_point, point_tuple) <= self.radius ** 2

class GerberFile(object):
    def __init__(self, file_path):
        self.raw_lines = open(file_path, "r").read().split()
        
        #a dict with point_tuple-(x,y) as key, and a list of connected point_tuples[(x,y),...] as value
        #duplicate points are allowed, because it easy to remove them at the final stage.
        #for conviviance, apoint is connected to itself.
        self.connected_points_dict = {}
        
        #dict with point_tuple-(x,y) as key, and a GerberAP object as value
        self.gerber_ap_dict = {}
        
        #dict with all types of pass
        self.ap_types_dict = {}
        
        #dict of sipported types constructors
        self.ap_types_consturctor_dict = {}
        self.ap_types_consturctor_dict['C'] = GerberAPCircle
        self.ap_types_consturctor_dict['R'] = GerberAPRectangle
        self.ap_types_consturctor_dict['O'] = GerberAPObround
        
        #sacle. dec umber with msb fo integer part and lsb for fraction part
        self.x_scale = 99 # default value of extremly high precision and very large amount of digits. basically the maximum supported in the standart
        self.y_scale = 99
        
        #list of lines. will be used to detect point connected directly to line and not ap.
        self.ap_line_list = []
        
        #internal vars, used to transfer data between functions
        self.current_x = 0
        self.current_y = 0
        self.current_ap_type = 0
    
    def connect_points(self, point_tuple1, point_tuple2):
        """
        update connected_points_dict in such way that all points connected to point_tuple1 are now connected to all the points connected to point_tuple2,
        and viseversa
        """
        if not (point_tuple1 in self.connected_points_dict):
            self.connected_points_dict[point_tuple1] = [point_tuple1]
        if not (point_tuple2 in self.connected_points_dict):
            self.connected_points_dict[point_tuple2] = [point_tuple2]
        new_connection_group = self.connected_points_dict[point_tuple1] + self.connected_points_dict[point_tuple2]
        new_connection_group = remove_list_duplicate(new_connection_group)
        
        for point_tuple in new_connection_group:
            self.connected_points_dict[point_tuple] = new_connection_group
            
    
    def gerber_point_scaling(self, point_tuple):
        """
        get a point in the format of the average gerberline, 
        and convert it to the real unit scale of the gerber (mm or inch)
        """
        return (point_tuple[0] * 10**(-(self.x_scale % 10)),  point_tuple[1] * 10**(-(self.y_scale % 10)))
    
    def set_scale_line(self, line):
        self.x_scale = line.get_var_dec_value("X")
        self.y_scale = line.get_var_dec_value("Y")
    
    def add_ap_def_line(self, line):
        ap_type_defined = line.get_var_dec_value("ADD")
        shape_type = line.line_string[6]
        if shape_type in self.ap_types_consturctor_dict:
            self.ap_types_dict[ap_type_defined] = self.ap_types_consturctor_dict[shape_type](line.get_real_values_line_def())
        else: #shape undefined, handle as minimal size circle
            self.ap_types_dict[ap_type_defined] = self.ap_types_consturctor_dict['C']([10**(-(self.x_scale % 10))])
            
    
    def add_command_line(self, line):
        """
        get a command line and adding the appropriate line/apature
        """
        command_type = line.get_var_dec_value('D')
        line_x =  line.get_var_dec_value('X')
        line_y =  line.get_var_dec_value('Y')
        
        next_x = line_x if line_x != None else self.current_x
        next_y = line_y if line_y != None else self.current_y
        
        if command_type == 1: #connection_drawing command
            
            self.connect_points((next_x, next_y), (self.current_x, self.current_y))
            #assume x_scale and y_scale identical for line. may improve later
            ap_line = GerberAPLine( (self.current_x, self.current_y), (next_x, next_y), self.ap_types_dict[self.current_ap_type].r * 10**(self.x_scale % 10) )
            self.ap_line_list.append(ap_line)
            
        self.current_x = next_x
        self.current_y = next_y
            
        if command_type == 3:#aparture adding command
            ap = GerberAP(self.current_x, self.current_y, self.current_ap_type)
            self.gerber_ap_dict[(self.current_x, self.current_y)] = ap
        if command_type > 3: #aparture type command
            self.current_ap_type = command_type
    
    def parse_lines(self):
        """
        a function that parse all line, and generate required AP and points.
        note that resulted AP are not yet connected to any other APs.
        """
        self.current_x = 0
        self.current_y = 0
        self.current_ap_type = 0
        for raw_line in self.raw_lines:
            line = GerberLine(raw_line)
            if line.line_is_command():
                self.add_command_line(line)
            elif line.line_is_scale():
                self.set_scale_line(line)
            elif line.line_is_basic_ap_def():
                self.add_ap_def_line(line)
            else:
                pass
                
    
    def _remove_dup_from_connected_points_dict(self):
        for point in self.connected_points_dict:
            self.connected_points_dict[point] = remove_list_duplicate(self.connected_points_dict[point])
    
    def _remove_dup_from_connected_aps(self):
        for ap_loc in self.gerber_ap_dict:
            self.gerber_ap_dict[ap_loc].ap_connected_to = remove_list_duplicate(self.gerber_ap_dict[ap_loc].ap_connected_to)
    
    def link_ap_to_points(self):
        """
        pass on all ap and add each point connected to them to their list
        """
        for ap_loc in self.gerber_ap_dict:#for all ap
            ap = self.gerber_ap_dict[ap_loc]
            for point in self.connected_points_dict:#for all connection endpoints
                if self.ap_types_dict[ap.type].point_in_ap( self.gerber_point_scaling((point[0] - ap_loc[0], point[1] - ap_loc[1])) ):
                    ap.points_connected_to.append(point)
    
    def connect_point_to_line(self):
        """
        pass on all points and check if they are connected directely to a line
        """
        for point in self.connected_points_dict:
            for ap_line in self.ap_line_list:
                if ap_line.point_in_ap(point):
                    self.connect_points(point, ap_line.start_point)
                    self.connect_points(point, ap_line.end_point)
    
    def generate_APs_connections(self):
        """
        use the points connection to calc which APs are connected to each other
        """
        for ap_loc in self.gerber_ap_dict:#for all aps, based on thier location
            ap_checked = self.gerber_ap_dict[ap_loc]
            for ap_checked_connection_point in ap_checked.points_connected_to: #usuually one or 2 points
                for farther_point in self.connected_points_dict[ap_checked_connection_point]: #for all point connected to the connection point
                    for potential_connected_ap_loc in self.gerber_ap_dict:#for all aps, because we connaot know withou checking which one is connected to farther_point
                        potential_connected_ap = self.gerber_ap_dict[potential_connected_ap_loc]
                        if farther_point in potential_connected_ap.points_connected_to:#if farther_point is inside the ap
                            potential_connected_ap.ap_connected_to += ap_checked.ap_connected_to
                            ap_checked.ap_connected_to += potential_connected_ap.ap_connected_to
                            
                            potential_connected_ap.ap_connected_to = remove_list_duplicate(potential_connected_ap.ap_connected_to)
                            ap_checked.ap_connected_to = remove_list_duplicate(potential_connected_ap.ap_connected_to)
    
    def process_aps_with_connection(self):
        """
        this is the main functonality of this object.
        it shall return a list of GerberAP with thier connection
        """
        self.parse_lines()
        self._remove_dup_from_connected_points_dict()
        self.connect_point_to_line()
        self.link_ap_to_points()
        self.generate_APs_connections()
        self._remove_dup_from_connected_aps()
        
        result = []
        for ap_loc in self.gerber_ap_dict:
            result.append(self.gerber_ap_dict[ap_loc])
        return result
    
    def get_nets(self):
        """
        get al nets. net is represented by a list connected apartue_centers.
        net must contain more than one connection.
        """
        if len(self.gerber_ap_dict) == 0:
            self.process_aps_with_connection()
        
        already_processed_aps = []
        net_list = []
        for ap_loc in self.gerber_ap_dict:
            ap = self.gerber_ap_dict[ap_loc]
            if not(ap in already_processed_aps):
                net_list.append([connected_ap.location for connected_ap in ap.ap_connected_to])
                already_processed_aps += ap.ap_connected_to
        
        nontrivial_net_list = []#net list without nets with only 1 point
        for point_list in net_list:
            if len(point_list) > 1:
                nontrivial_net_list.append(point_list)
        
        return nontrivial_net_list
        
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                    