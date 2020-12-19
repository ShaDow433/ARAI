import numpy as np
import matplotlib.image as mpimg
from PIL import Image


def testcase10_with_GraFlow_MVAC_chen():
    """
    StructWorkArea中有两条走廊分别平行于X、Y轴，长分别为10m和10m，没有梁
    功能性展示：1、水管和风管分集合排在两边
               已完成
    """
    StructWorkArea = trans_pixel('E:\项目\ARAI\ARAI_withmvac-1.1\Structure_3.jpg') # 1000*1000
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_10={'Route': [[410, 0, None],[410, 420, None],[0, 420, None]],
               'Type': '12031',
               'Size': [101, 101],
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    GraFlow_11={'Route': [[410, 0, None],[410, 420, None],[900, 420, None]],
               'Type': '12031',
               'Size': [101, 101],
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}

    GraFlow_12={'Route': [[410, 900, None],[410, 550, None],[900, 550, None]],
               'Type': '12031',
               'Size': [101, 101],
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    GraFlow_13={'Route': [[410, 900, None],[410, 420, None],[50, 420, None]],
               'Type': '12031',
               'Size': [101, 101],
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}

    GraFlow_2 = {'Route': [[430, 0, None],[430, 440, None],[0, 440, None]],
                 'Type': '12031',
                 'Size': [101, 101],
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}
    GraFlow_3 = {'Route': [[475, 0, None],[475, 990, None]],
                 'Type': '12031',
                 'Size': [101, 101],
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}

    MVAC_1 = {'Route': [[521, 0, None], [521, 990, None]],
              'Type': '20002',
              'Size': [200, 200],
              'Elbow': [[0, 0], [0, 0]],
              'Insulation': 0}
    MVAC_2 = {'Route': [[560, 0, None], [560, 420, None], [990, 420, None]],
              'Type': '20002',
              'Size': [200, 200],
              'Elbow': [[0, 0], [0, 0]],
              'Insulation': 0}

    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    GraFlow = [GraFlow_10, GraFlow_12, GraFlow_13, GraFlow_2]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[]
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


def testcase3():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,有两横梁
    功能性展示：f)   一条管穿樑,另一条（大于300）不穿
    修改不穿梁
    """
    StructWorkArea = trans_pixel('testcase2.jpg')  # 10000mm*10000mm
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[424, 0, None], [424, 980, None]],
               'Type': '10011',
               'Size': [100, 100],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':25
               }
    '''
    GraFlow_2 = {'Route': [[330, 0, None], [330, 1000, None]],
                 'Type': '12031',
                 'Size': [300, 300],#梯度比1：150
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    '''

    Segment = {'Route':  [[308, 100], [656, 100]],
               'LenSegment':  3490
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    Beam_1 = {'Route':[[308, 100], [656, 100]],
              'BWidth':400,
              'BDepth':700
              }
    Beam_2 = {'Route': [[308, 900], [656, 900]],
              'BWidth': 400,
              'BDepth': 700
              }
    GraFlow = [GraFlow_1]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_1,Beam_2]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase4():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,有两横梁
    功能性展示：f)   一条管穿樑,另一条（大于300）不穿
    修改不穿梁
    """
    StructWorkArea = trans_pixel('testcase2.jpg')  # 10000mm*10000mm
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[424, 0, None], [424, 980, None]],
               'Type': '10011',
               'Size': [100, 100],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':25
               }

    GraFlow_2 = {'Route': [[330, 0, None], [330, 999, None]],
                 'Type': '12031',
                 'Size': [300, 300],#梯度比1：150
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }

    Segment = {'Route':  [[308, 100], [656, 100]],
               'LenSegment':  3490
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    Beam_1 = {'Route':[[308, 100], [656, 100]],
              'BWidth':400,
              'BDepth':700
              }
    Beam_2 = {'Route': [[308, 900], [656, 900]],
              'BWidth': 400,
              'BDepth': 700
              }
    GraFlow = [GraFlow_1,GraFlow_2]
    # GraFlow = [GraFlow_2]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_1,Beam_2]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase1_with_GraFlow():
    """
    StructWorkArea中有两条走廊分别平行于X、Y轴,长分别为40m和10m,没有梁,长为40m的走廊上有一条重力流,长为10m的走廊有一条风管
    存在冲突：重力流长度超过30m
    """
    StructWorkArea = trans_pixel("Structure_1.png") # 1000*4000
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[450, 0, None], [450, 3990, None]],
               'Type': '12031',
               'Size': [250, 250],  #  梯度比1：200
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0
               }
    Segment = {'Route':  [[369, 100], [560, 100]],
               'LenSegment':  1920
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    GraFlow = [GraFlow_1]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase2_with_GraFlow():
    """
        StructWorkArea中有两条十字交叉的走廊,无梁
        功能性展示：并排多条管,一些向左转,一些向右转,自动贴墙转弯
        """
    StructWorkArea = trans_pixel("Structure_2.png")  # 1000*1000
    (StructWorkArea_X, StructWorkArea_Y) = (StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1 = {'Route': [[380, 0, None], [380, 1970, None],[0, 1970, None]],
                 'Type': '10021',
                 'Size': [100, 100],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}
    GraFlow_2 = {'Route': [[400, 0, None], [400, 1970, None],[999, 1970, None]],
                 'Type': '10021',
                 'Size': [100, 100],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    GraFlow_3 = {'Route': [[420, 0, None], [420, 1950, None],[999, 1950, None]],
                 'Type': '10021',
                 'Size': [100, 100],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    GraFlow_4 = {'Route': [[510, 0, None], [510, 2010, None],[0, 2010, None]],
                 'Type': '10021',
                 'Size': [100, 100],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    GraFlow_5 = {'Route': [[530, 0, None], [530, 1930, None],[999, 1930, None]],
                 'Type': '10021',
                 'Size': [100, 100],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    GraFlow_6 = {'Route': [[550, 0, None], [550, 1910, None], [999, 1910, None]],
                 'Type': '10021',
                 'Size': [100, 100],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}
    Segment = {'Route': [[369, 100], [560, 100]],
               'LenSegment': 1920}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    GraFlow = [GraFlow_1, GraFlow_2, GraFlow_3,]
    # GraFlow = [GraFlow_1, GraFlow_2, GraFlow_3, GraFlow_4, GraFlow_5, GraFlow_6]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam = []
    return StructWorkArea, (StructWorkArea_X, StructWorkArea_Y), Segment, High_Info, Beam, Pipes


def testcase3_with_GraFlow():
    """
    StructWorkArea中有两条走廊分别平行于X、Y轴,长分别为10m和10m,没有梁
    功能性展示：1、两条水管十字交叉
               已完成
    """
    StructWorkArea = trans_pixel('E:\项目\ARAI\ARAI_withmvac-withbrief-1.1\Structure_3.jpg') # 1000*1000
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[500, 0, None], [500, 990, None]],
               'Type': '12031',
               'Size': [400, 400],  #  梯度比1：200
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    GraFlow_2 = {'Route': [[0, 500, None], [990, 500, None]],
                 'Type': '12031',
                 'Size': [300, 300],  # 梯度比1：200
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}
    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    GraFlow = []
    MVAC = [GraFlow_1,GraFlow_2]
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase4_with_GraFlow():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,有一条梁
    功能性展示：多条管线穿樑并排成2层
    已完成
    """

    '''该尺寸ratio是70！！！！！！！！！！！！！'''
    StructWorkArea = trans_pixel("E:\项目\ARAI\ARAI_withmvac-1.1\Structure_4.jpg")  # 1000*1000
    (StructWorkArea_X,StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[453, 0, None], [453, 999, None]],
               'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
               'Size': [150, 150],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    GraFlow_2 = {'Route': [[470, 0, None], [470, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [150, 150],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0}
    GraFlow_3 = {'Route': [[482, 0, None], [482, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [150, 150],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_4 = {'Route': [[495, 0, None], [495, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [150, 150],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_5 = {'Route': [[508, 0, None], [508, 999, None]],
                 'Type': '10021',# PWP饮用水,直径50,installation60,无包裹材料
                 'Size': [150, 150],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_6 = {'Route': [[519, 0, None], [519, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [150, 150],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    Segment = {'Route': [[308, 100], [656, 100]],
               'LenSegment':  3490}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    Beam_1 = {'Route': [[308, 80], [656, 80]],
              'BWidth': 400,
              'BDepth': 700}
    GraFlow = [GraFlow_1,GraFlow_2,GraFlow_3,GraFlow_4,GraFlow_5,GraFlow_6]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_1]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase4_with_GraFlow_chen():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,有一条梁
    功能性展示：多条管线穿樑并排成2层
    已完成
    """

    '''该尺寸ratio是70！！！！！！！！！！！！！'''
    StructWorkArea = trans_pixel("Structure_4.jpg")  # 1000*1000
    (StructWorkArea_X,StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[453, 0, None], [453, 999, None]],
               'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
               'Size': [60, 60],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    GraFlow_2 = {'Route': [[470, 0, None], [470, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0}
    GraFlow_3 = {'Route': [[482, 0, None], [482, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_4 = {'Route': [[495, 0, None], [495, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_5 = {'Route': [[508, 0, None], [508, 999, None]],
                 'Type': '10021',# PWP饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_6 = {'Route': [[519, 0, None], [519, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_7 = {'Route': [[519, 0, None], [519, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_8 = {'Route': [[519, 0, None], [519, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_9 = {'Route': [[519, 0, None], [519, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    GraFlow_10 = {'Route': [[519, 0, None], [519, 999, None]],
                 'Type': '10021',# 饮用水,直径50,installation60,无包裹材料
                 'Size': [60, 60],#梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation':0
                 }
    Segment = {'Route': [[308, 100], [656, 100]],
               'LenSegment':  3490}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    Beam_1 = {'Route': [[308, 80], [656, 80]],
              'BWidth': 400,
              'BDepth': 700}
    GraFlow = [GraFlow_1,GraFlow_2,GraFlow_3,GraFlow_4,GraFlow_5,GraFlow_6,GraFlow_7,GraFlow_8,GraFlow_9,GraFlow_10]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_1]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes




def testcase5_with_GraFlow():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,有两横梁
    功能性展示：f)	一条管穿樑,另一条（大于300）不穿
    修改不穿梁
    """
    StructWorkArea = trans_pixel('Structure_4.jpg')  # 10000mm*10000mm
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[424, 0, None], [424, 980, None]],
               'Type': '10011',
               'Size': [100, 100],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':25
               }
    """
    GraFlow_2 = {'Route': [[330, 1, None], [330, 999, None]],
                 'Type': '12031',
                 'Size': [300, 300],#梯度比1：150
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
     """
    Segment = {'Route':  [[308, 100], [656, 100]],
               'LenSegment':  3490
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    Beam_1 = {'Route':[[308, 100], [656, 100]],
              'BWidth':400,
              'BDepth':700
              }
    Beam_2 = {'Route': [[308, 900], [656, 900]],
              'BWidth': 400,
              'BDepth': 700
              }
    GraFlow = [GraFlow_1]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[Beam_1,Beam_2]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase6_with_GraFlow_1():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,
    功能性展示：
    """
    StructWorkArea = trans_pixel('E:\MYPROJECT\ARAI\ARAI_withmvac-withbrief-1.1\Structure_5.png')
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1 = {'Route': [[440, 0, None], [440, 999, None]],
               'Type': '10011',
               'Size': [250, 250],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':25
                 }

    GraFlow_2 = {'Route': [[450, 0, None], [450, 999, None]],
                 'Type': '10011',
                 'Size': [250, 250],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 25
                 }
    GraFlow_3 = {'Route': [[460, 0, None], [460, 999, None]],
                 'Type': '10011',
                 'Size': [250, 250],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 25
                 }
    GraFlow_4 = {'Route': [[470, 0, None], [470, 999, None]],
                 'Type': '10011',
                 'Size': [250, 250],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 25
                 }

    Segment = Segment = {'Route':  [[369, 100], [560, 100]],
               'LenSegment':  1920
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    #GraFlow = [GraFlow_1]
    GraFlow = []
    MVAC = [GraFlow_1,GraFlow_2,GraFlow_3,GraFlow_4]
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase6_with_GraFlow_2():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,
    功能性展示：3条水管无间隙排在一起,算法画图出来自动拉开
    """
    StructWorkArea = trans_pixel('Structure_5.png')
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[440, 0, None], [440, 999, None]],
               'Type': '10011',
               'Size': [250, 250],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':25
               }

    GraFlow_2 = {'Route': [[450, 0, None], [450, 999, None]],
                 'Type': '10011',
                 'Size': [250, 250],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 25
                 }
    """
    GraFlow_3 = {'Route': [[460, 0, None], [460, 999, None]],
                 'Type': '10011',
                 'Size': [250, 250],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 25
                 }
    """
    Segment = Segment = {'Route':  [[369, 100], [560, 100]],
               'LenSegment':  1920
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    GraFlow = [GraFlow_1,GraFlow_2]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes
def testcase6_with_GraFlow_3():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,
    功能性展示：3条水管无间隙排在一起,算法画图出来自动拉开
    """
    StructWorkArea = trans_pixel('Structure_5.png')
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[440, 0, None], [440, 999, None]],
               'Type': '10011',
               'Size': [250, 250],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':25
               }
    GraFlow_2 = {'Route': [[450, 0, None], [450, 999, None]],
                 'Type': '10011',
                 'Size': [250, 250],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 25
                 }
    GraFlow_3 = {'Route': [[460, 0, None], [460, 999, None]],
                 'Type': '10011',
                 'Size': [250, 250],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 25
                 }

    Segment = Segment = {'Route':  [[369, 100], [560, 100]],
               'LenSegment':  1920
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    GraFlow = [GraFlow_1,GraFlow_2,GraFlow_3]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes
def testcase7A_with_MVAC():
    """
    StructWorkArea中有两条走廊分别平行于X、Y轴,长度均为10m,没有梁,长为40m的走廊上有一条重力流,长为10m的走廊有一条风管
    存在冲突：1、十字交叉相撞
             2、风管宽改扁
    """
    StructWorkArea = trans_pixel("E:\MYPROJECT\ARAI\ARAI_withmvac-withbrief-1.1\Structure_3.jpg") # 1000*4000
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    MVAC_1={'Route': [[500, 0, None], [500, 999, None]],
               'Type': '12031',
               'Size': [1500, 700],
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    MVAC_2 = {'Route': [[0, 500, None], [999, 500, None]],
               'Type': '20002',
               'Size': [600, 600],
               'Elbow': [[0, 0], [0, 0]],
              'Insulation': 0}
    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3430,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    GraFlow = []
    MVAC = [MVAC_1,MVAC_2]
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase7B_with_GraFlow():
    """
    StructWorkArea中有两条走廊分别平行于X、Y轴,长度均为10m,没有梁,长为40m的走廊上有一条重力流,长为10m的走廊有一条风管
    存在冲突：1、十字交叉相撞
             2、风管宽改扁
    """
    StructWorkArea = trans_pixel("Structure_3_1.jpg") # 1000*4000
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[500, 0, None], [500, 999, None]],
               'Type': '12031',
               'Size': [700, 700],
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    MVAC_1 = {'Route': [[0, 500, None], [999, 500, None]],
              'Type': '20002',
              'Size': [600, 600],
              'Elbow': [[0, 0], [0, 0]],
              'Insulation': 0}
    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3430,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    GraFlow = [GraFlow_1]
    MVAC = [MVAC_1]
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes


def testcase8_with_GraFlow():
    """
    StructWorkArea中只有一条平行于Y轴长度为10m的走廊,
    功能性展示：水管一排排不下排两排
    """
    StructWorkArea = trans_pixel('Structure_5.png')
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[396, 0, None], [396, 999, None]],
               'Type': '10011',
               'Size': [600, 600],#梯度比1：40
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0
               }
    GraFlow_2 = {'Route': [[433, 0, None], [433, 999, None]],
                 'Type': '10011',
                 'Size': [600, 600],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    GraFlow_3 = {'Route': [[464, 0, None], [464, 999, None]],
                 'Type': '10011',
                 'Size': [600, 600],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    GraFlow_4 = {'Route': [[494, 0, None], [494, 999, None]],
                 'Type': '10011',
                 'Size': [600, 600],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    GraFlow_5 = {'Route': [[534, 0, None], [534, 999, None]],
                 'Type': '10011',
                 'Size':[600, 600],  # 梯度比1：40
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0
                 }
    Segment = {'Route':  [[369, 100], [560, 100]],
               'LenSegment':  1920
               }
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150
                 }
    GraFlow = [GraFlow_1,GraFlow_2,GraFlow_3,GraFlow_4,GraFlow_5]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes

#


def testcase10_with_GraFlow_MVAC():
    """
    StructWorkArea中有两条走廊分别平行于X、Y轴,长分别为10m和10m,没有梁
    功能性展示：1、水管和风管分集合排在两边
               已完成
    """
    StructWorkArea = trans_pixel('Structure_3.jpg') # 1000*1000
    (StructWorkArea_X, StructWorkArea_Y)=(StructWorkArea.shape[0], StructWorkArea.shape[1])
    GraFlow_1={'Route': [[410, 0, None],[410, 420, None],[0, 420, None]],
               'Type': '12031',
               'Size': [100, 100],  #  梯度比1：200
               'Elbow': [[0, 0], [0, 0]],
               'Insulation':0}
    GraFlow_2 = {'Route': [[430, 0, None],[430, 440, None] [0, 440, None]],
                 'Type': '12031',
                 'Size': [100, 100],
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}
    GraFlow_3 = {'Route': [[480, 0, None],[480, 999, None]],
                 'Type': '12031',
                 'Size': [100, 100],
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}
    GraFlow_4 = {'Route': [[550, 0, None], [550, 999, None]],
                 'Type': '12031',
                 'Size': [100, 100],
                 'Elbow': [[0, 0], [0, 0]],
                 'Insulation': 0}
    MVAC_1 = {'Route': [[456, 0, None], [456, 520, None][999, 520, None]],
              'Type': '12031',
              'Size': [200, 200],
              'Elbow': [[0, 0], [0, 0]],
              'Insulation': 0}
    MVAC_1 = {'Route': [[510, 0, None], [510, 480, None][999, 480, None]],
              'Type': '12031',
              'Size': [200, 200],
              'Elbow': [[0, 0], [0, 0]],
              'Insulation': 0}
    Segment = {'Route':  [[401, 100], [598, 100]],
               'LenSegment':  1980}
    High_Info = {'h_floor': 5000,
                 'h_false': 3000,
                 'thick_floor': 120,
                 'thick_light': 150}
    GraFlow = [GraFlow_1,GraFlow_2]
    MVAC = []
    Pipes = [GraFlow, MVAC]
    Beam=[]
    return StructWorkArea,(StructWorkArea_X, StructWorkArea_Y),Segment,High_Info,Beam,Pipes








