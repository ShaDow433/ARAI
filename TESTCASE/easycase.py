'''
Descripttion: 
version: 
Author: Zhiting Zhang
email: 1149357968@qq.com
Date: 2020-11-28 15:43:24
LastEditors: Zhiting Zhang
LastEditTime: 2020-12-05 17:22:59
'''

import numpy as np
import matplotlib.image as mpimg
from PIL import Image

def easycase1_with_GraFlow_MVAC_zhang():
    StructWorkArea = trans_pixel('E:\MYPROJECT\ARAI\TESTCASE图片\case1.jpg') 
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    #MVAC_2是原有的管道
    MVAC_0 = {'Route': [[660,6477,4450], [9355,6477,4450], [9355,15156,4450]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},
    #MVAC_1是需要排布的管道
    MVAC_1 = {'Route': [[11433,10706，4400], [9833,10706，4400], [9833,10706，4000], [4333,10706，4000]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},
    

    #Beam为梁，10x 代表101,102,103宽度相同            
    Beam_101 = {'Route':[[0, 798], [16709, 798]],
                'BWidth':1900,
                'BDepth':950
                }
    Beam_201 = {'Route':[[300, 950], [300, 13556]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_202 = {'Route':[[5600, 4504], [15709, 4504]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_203 = {'Route':[[5600, 7267], [15709, 7267]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_204 = {'Route':[[5600, 10030], [15709, 10030]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_205 = {'Route':[[5600, 12931], [15709, 12931]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_206 = {'Route':[[5900, 14455], [15709, 15644]],
                'BWidth':600,
                'BDepth':700
                }
    
    Beam_301 = {'Route':[[5650, 950], [5650, 13206]],
                'BWidth':700,
                'BDepth':1200
                }
    Beam_401 = {'Route':[[15708, 950], [15708, 16970]],
                'BWidth':2000,
                'BDepth':950
                }
    Beam_501 = {'Route':[[0, 13556], [1900, 13556]],
                'BWidth':700,
                'BDepth':2742
                }
    Beam_601 = {'Route':[[13971, 16796], [14439, 12931]],
                'BWidth':700,
                'BDepth':2742
                }
    Beam_602 = {'Route':[[5900, 16796], [10022, 16796], [10490, 12931] ],
                'BWidth':700,
                'BDepth':2742
                }
    

                
    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    GraFlow = []
    MVAC = [MVAC_0,MVAC_1]
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_101,
        Beam_201,Beam_202,Beam_203,Beam_204,Beam_205,Beam_206,
        Beam_301,
        Beam_401,
        Beam_501,
        Beam_601,Beam_602]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes




def easycase2_with_GraFlow_MVAC_zhang():
    StructWorkArea = trans_pixel('E:\MYPROJECT\ARAI\TESTCASE图片\case2.jpg') 
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])

    
    
    MVAC_1 = {'Route': [[0,14234,2895], [2826,14234,2895], [2826,14784,2895], [3766,14784,2895]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},
    MVAC_2 = {'Route': [[0,10845,4000], [4327,10845,4000]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},            
    MVAC_3 = {'Route': [[0,6577,4450], [4514,6577,4450]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},
    #需要排的是4            
    MVAC_4 = {'Route': [[1140,5084,4450], [1140,6044,4450], 
                        [1140,6044,4150], [1140,11746,4150], 
                        [1140,15801,4150], [1140,22025,4150]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},

                
    Beam_101 = {'Route':[[4300, 9231], [4300, 9231]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_102 = {'Route':[[300, 1000], [300, 23456]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_103 = {'Route':[[0, 13656], [4300, 13656]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_201 = {'Route':[[0, 23456], [4000, 23456]],
                'BWidth':1900,
                'BDepth':950
                }  
    Beam_301 = {'Route':[[0, 1000], [4300, 1000]],
                'BWidth':700,
                'BDepth':800
                }
                
    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    GraFlow = []
    MVAC = [MVAC_1]
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_101,Beam_102,Beam_103,Beam_201,Beam_301]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def easycase3_with_GraFlow_MVAC_zhang():
    StructWorkArea = trans_pixel('E:\MYPROJECT\ARAI\TESTCASE图片\case3.jpg') 
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])


    MVAC_1 = {'Route': [[3353,5278,4450], [3153,5278,4450], 
                        [3153,5278,4100], [1965,5278,4100], [1965,18330,4100]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},

                
    MVAC_2 = {'Route': [[651,8233,3860],[648,16923,3860],
                        [5885,16923,3860],[6005,14354,3860],[10885,14234,3860]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},
    MVAC_3 = {'Route': [[22,10845,4300],[6022,10845,4300],[6022,10845,4100],[10879,10845,4100]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},
    #需要排的是4 
    MVAC_4 = {'Route': [[2484,5248,4450],[2484,6577,4450],[10922,6577,4450]],
                'Type': '20002',
                'Size': [200, 200],
                'Elbow': [[0, 0], [0, 0]],
                'Insulation': 0},


    Beam_101 = {'Route':[[599, 9231], [7249, 9231]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_102 = {'Route':[[7270, 13307], [7270, 6131]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_103 = {'Route':[[599, 6131], [10570, 6131]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_104 = {'Route':[[10570, 1000], [10570, 23450]],
                'BWidth':600,
                'BDepth':700
                }
    Beam_201 = {'Route':[[0, 1001], [10870, 1001]],
                'BWidth':1200,
                'BDepth':900
                }
    Beam_301 = {'Route':[[5583, 1000], [5583, 6130]],
                'BWidth':500,
                'BDepth':400
                }
    Beam_401 = {'Route':[[600, 1000], [600, 14050]],
                'BWidth':1200,
                'BDepth':700
                }
    Beam_501 = {'Route':[[1720, 13656], [7270, 13656]],
                'BWidth':700,
                'BDepth':650
                }
    Beam_601 = {'Route':[[1370, 16581], [7420, 16581]],
                'BWidth':300,
                'BDepth':800
                }
    Beam_701 = {'Route':[[1370, 15331], [1370, 18431]],
                'BWidth':700,
                'BDepth':800
                }
    Beam_801 = {'Route':[[3345, 16590], [3345, 23556]],
                'BWidth':400,
                'BDepth':800
                }
    Beam_901 = {'Route':[[6270, 13657], [6270, 16581]],
                'BWidth':300,
                'BDepth':500
                }
    Beam_902 = {'Route':[[3570, 9231], [3570, 16581]],
                'BWidth':300,
                'BDepth':500
                }
    Beam_903 = {'Route':[[3570, 11656], [7249, 11656]],
                'BWidth':300,
                'BDepth':500
                }

    

    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    GraFlow = []
    MVAC = [MVAC_1]
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_101,Beam_102,Beam_103,Beam_104,
        Beam_201,
        Beam_301,
        Beam_401,
        Beam_501,
        Beam_601,
        Beam_701,
        Beam_801,
        Beam_901,Beam_902,Beam_903]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes

def trans_pixel(pic_name):
    im = np.array(Image.open(pic_name).convert('L'))  # 打开图片,灰度化处理,再转换成数组
    for i in range(im.shape[0]):
        for j in range(im.shape[1]):
            if (im[i, j] <= 127):
                im[i, j] = 0
            else:
                im[i, j] = 255
    return im