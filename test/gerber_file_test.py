import sys
sys.path.append("../src")
from gerber_file import *

def test_two_circles():
    gerber_file = GerberFile("two_connected_circles.GBL")
    resulted_aps = gerber_file.process_aps_with_connection()
    assert len(resulted_aps) == 2
    assert len(resulted_aps[0].ap_connected_to) == 2
    assert len(resulted_aps[1].ap_connected_to) == 2
    assert resulted_aps[0] in resulted_aps[0].ap_connected_to
    assert resulted_aps[0] in resulted_aps[1].ap_connected_to
    assert resulted_aps[1] in resulted_aps[0].ap_connected_to
    assert resulted_aps[1] in resulted_aps[1].ap_connected_to
    print ("passed two circle test")
    

if __name__ == '__main__':
    test_two_circles()