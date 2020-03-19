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
        self.ap_connected_to = [] 

class GerberFile(object):
    def __init__(self, file_path):
        self.raw_lines = open(file_path, "r").read().split()
        
        #a dict with point_tuple-(x,y) as key, and a list of connected point_tuples[(x,y),...] as value
        #duplicate points are allowed, because it easy to remove them at the final stage.
        #for conviviance, apoint is connected to itself.
        self.connected_points_dict = {}
        
        #dict with point_tuple-(x,y) as key, and a GerberAP object as value
        self.gerber_ap_dict = {}
    
    def connect_points(self, point_tuple1, point_tuple2):
        """
        update connected_points_dict in such way that all points connected to point_tuple1 are now connected to all the points connected to point_tuple2,
        and viseversa
        """
        if not (point_tuple1 in self.connected_points_dict):
            self.connected_points_dict[point_tuple1] = [point_tuple1]
        if not (point_tuple2 in self.connected_points_dict):
            self.connected_points_dict[point_tuple2] = [point_tuple2]
            
        for point_tuple in self.connected_points_dict[point_tuple1]:
            self.connected_points_dict[point_tuple] = self.connected_points_dict[point_tuple] + self.connected_points_dict[point_tuple2]
            
        for point_tuple in self.connected_points_dict[point_tuple2]:
            self.connected_points_dict[point_tuple] = self.connected_points_dict[point_tuple] + self.connected_points_dict[point_tuple1]
    
    def parse_lines(self):
        """
        a function that parse all line, and generate required AP and points.
        note that resulted AP are not yet connected to any other APs.
        """
        current_x = 0
        current_y = 0
        current_ap_type = 0
        for raw_line in self.raw_lines:
            line = GerberLine(raw_line)
            if line.line_is_command():
                command_type = line.get_var_dec_value('D')
                line_x =  line.get_var_dec_value('X')
                line_y =  line.get_var_dec_value('Y')
                
                if command_type == 1: #connection_drawing command
                    self.connect_points((line_x if line_x != None else current_x, line_y if line_y != None else current_y), (current_x, current_y))
                    
                if line_x != None:
                    current_x = line_x
                if line_y != None:
                    current_y = line_y
                    
                if command_type == 3:#aparture adding command
                    ap = GerberAP(current_x, current_y, current_ap_type)
                    self.gerber_ap_dict[(current_x, current_y)] = ap
                if command_type > 3: #aparture type command
                    current_ap_type = command_type
    
    def _remove_dup_from_connected_points_dict(self):
        for point in self.connected_points_dict:
            self.connected_points_dict[point] = remove_list_duplicate(self.connected_points_dict[point])
    
    def generate_APs_connections(self):
        """
        use the points connection to calc which APs are connected to each other
        """
        for ap_loc in self.gerber_ap_dict:#for all aps, based on thier location
            if ap_loc in self.connected_points_dict: # if ap has connectted points
                for point in self.connected_points_dict[ap_loc]: # go on all connected points
                    if point in self.gerber_ap_dict: #if there is an object on the connected point
                        self.gerber_ap_dict[ap_loc].ap_connected_to.append(self.gerber_ap_dict[point])
    
    def process_aps_with_connection(self):
        """
        this is the main functonality of this object.
        it shall return a list of GerberAP with thier connection
        """
        self.parse_lines()
        self._remove_dup_from_connected_points_dict()
        self.generate_APs_connections()
        
        result = []
        for ap_loc in self.gerber_ap_dict:
            result.append(self.gerber_ap_dict[ap_loc])
        return result
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                    