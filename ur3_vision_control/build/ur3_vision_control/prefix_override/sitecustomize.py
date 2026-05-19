import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/delia/Documents/MUAR/ProyectoREC/ur3_vision_control/install/ur3_vision_control'
