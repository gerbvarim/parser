import sys
sys.path.append("../src")
from gerber_file import *

def test_two_circles():
    gerber_file = GerberFile("two_connected_circles.GBL")
    resulted_aps = gerber_file.process_aps_with_connection()
    assert len(resulted_aps) == 2
    print (resulted_aps[0].ap_connected_to)
    assert len(resulted_aps[0].ap_connected_to) == 2
    assert len(resulted_aps[1].ap_connected_to) == 2
    assert resulted_aps[0] in resulted_aps[0].ap_connected_to
    assert resulted_aps[0] in resulted_aps[1].ap_connected_to
    assert resulted_aps[1] in resulted_aps[0].ap_connected_to
    assert resulted_aps[1] in resulted_aps[1].ap_connected_to
    assert resulted_aps[0].type == 11
    assert resulted_aps[1].type == 11
    assert resulted_aps[0].location != resulted_aps[1].location #check the circles are indeed different
    assert resulted_aps[0].location == (100000, 100000) or resulted_aps[0].location == (300000, 200000)
    assert resulted_aps[1].location == (100000, 100000) or resulted_aps[1].location == (300000, 200000)
    print ("passed two circle test")

def test_circles_and_squares():
    gerber_file = GerberFile("connected_circiles_and_squares.GBL")
    resulted_aps = gerber_file.process_aps_with_connection()
    assert len(resulted_aps) == 5
    for ap in resulted_aps:
        assert ap.type == 11 or ap.type == 12
        if ap.type == 11:#ap is one of the 2 circles
            assert len(ap.ap_connected_to) == 2
            for ap_connected in ap.ap_connected_to:
                assert ap_connected.type == 11 #check circles are only connected to circles
        if ap.type == 12:#ap is one of the 2 circles
            assert len(ap.ap_connected_to) == 3
            for ap_connected in ap.ap_connected_to:
                assert ap_connected.type == 12 #check squares are only connected to squares
    print ("passed circles ans sqaures test")
    
def minor_test_from_real_life():
    gerber_file = GerberFile("Serial_Demux_top_test.GTL")
    gerber_file.process_aps_with_connection()
    print (len(gerber_file.gerber_ap_dict))
    print (len(gerber_file.gerber_ap_dict[(64745, 63373)].ap_connected_to))
    for ap in gerber_file.gerber_ap_dict[(64745, 63373)].ap_connected_to:
        print (ap.location)
    assert len(gerber_file.gerber_ap_dict[(64745, 63373)].ap_connected_to) == 8
    assert len(gerber_file.gerber_ap_dict[(55030, 50311)].ap_connected_to) == 2
    assert len(gerber_file.gerber_ap_dict[(58864, 50038)].ap_connected_to) == 3

if __name__ == '__main__':
    test_two_circles()
    test_circles_and_squares()
    minor_test_from_real_life()