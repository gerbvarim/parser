import os
from gerber.rs274x import read as gerber_read

if __name__ == "__main__":
    gerber_dir_path = 'C:\home_work\gerbers\Serial Demux All\Serial_Demux_v1\Gerber'
    # fname = 'Serial_Demux_v1.GTL'
    fname = 'Serial_Demux_v1.GP1'

    layer = gerber_read(os.path.join(gerber_dir_path, fname))

    print('read gerber')