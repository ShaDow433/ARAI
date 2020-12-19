"""
规范：
    1、变量名采用StructWorkArea2D形式（每单词首字母大写）；但如果是两个大写字母相邻则需要加“_”隔开，如StructWorkArea3D_Temp;“With"前后需要接”_“即是”_With_“，如StructWorkArea3D_With_GraFlow
    2、而函数采用sort_pipes()形式（全小写，下划线为分隔符）；但变量名包含其中则变量名保持不变，如bulid_StructWorkArea3D_temp
"""
import sys
import os
import numpy as np
import math
import oldtestcase
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#put_pipe for GrawFlow
import put_pipe
#zhang for MVAC
from function_zhang import *  








def main():

    #################################创建记录文件，记录各种flag#################################
    # LogPath = os.path.dirname(os.getcwd()) + "file.log"
    LogPath = "file.log"
    f=open(LogPath,'w')
    f.close()




    #################################输入数据与必要处理#################################       
    StructWorkArea2D, (StructWorkArea_X, StructWorkArea_Y), Segment, HighInfo, Beams, Pipes = oldtestcase.testcase6_with_GraFlow_1()

    #延长或缩短Segment至接触走廊； 计算像素实际长度
    LenPixel = calculate_lenpixel(StructWorkArea2D, Segment)

    #写入安装空间信息\NewSize;按新NewSize为管道排序;为管道赋值，并返回对照字典PipesValueDict
    PipesValueDict, Pipes = processing_pipes(Pipes, LenPixel)

    #无横梁3d aray  
    Z_Max, H_Max, StructWorkArea3D_Temp = bulid_StructWorkArea3D_temp(HighInfo, LenPixel, StructWorkArea2D)
    #print('StructWorkArea3D_temp:',StructWorkArea3D_Temp)
    #加上横梁
    Beams, BeamsValueDict, StructWorkArea3D = processing_beams(StructWorkArea3D_Temp, Beams, LenPixel)
    print('StructWorkArea3D.shape:',StructWorkArea3D.shape)

    #################################排布重力流#################################
    StructWorkArea3D_With_GraFlow = StructWorkArea3D.copy()
    GraFlow_temp = Pipes[0].copy()

    # GraFlow_Against_Wall = put_pipe.Against_wall_GraFlow(StructWorkArea3D_With_GraFlow, Pipes[0], LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict)

    # print('GraFlow_Against_Wall:')
    # i=0
    # for i in range(len(GraFlow_temp)):
    #     print('%d:' % (i+1))
    #     print('before against_wall:', GraFlow_temp[i]['Route'].tolist())
    #     print( 'after against_wall:', GraFlow_Against_Wall[i]['Route'].tolist())

    # print('\n\n\n********靠墙结束，开始排障*****\n\n\n')

    # i = 1
    # for graflow in GraFlow_Against_Wall:
    #     print('\n\n\n=================排障：第%d条管======================='%i)
    #     StructWorkArea3D_With_GraFlow, Segment = put_pipe.put_GraFlow(StructWorkArea3D_With_GraFlow,StructWorkArea2D, GraFlow_Against_Wall, graflow, LenPixel, Z_Max, Beams, LogPath, PipesValueDict, BeamsValueDict)
        
    #     for segment in Segment:
    #         lowest_z, StructWorkArea3D_With_GraFlow = function_chen.put_output(graflow, StructWorkArea3D_With_GraFlow, StructWorkArea2D, segment, Z_Max, LenPixel)
    #     i+=1

    # print('\n\n\n********排障结束*****\n\n\n')

    StructWorkArea3D_With_GraFlow = StructWorkArea3D_With_GraFlow.astype(int)

    print('\n\n\n********开始排布风管*****\n\n\n')

    ################################排布风管#################################
    StructWorkArea3D_With_GraFlow_With_MVAV = StructWorkArea3D_With_GraFlow.copy()
    MVAC_temp = Pipes[1].copy()
    #MVACFlow_Against_Wall 为靠墙排布后的风管集合
    MVACFlow_Against_Wall = Against_wall_MVACFlow(StructWorkArea3D_With_GraFlow_With_MVAV, Pipes[1], LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict)

    print('MVACFlow_Against_Wall:')
    i = 0
    for i in range(len(MVAC_temp)):
        print('%d:' % (i + 1))
        print('before against_wall:', MVAC_temp[i]['Route'].tolist())
        print('after against_wall:', MVACFlow_Against_Wall[i]['Route'].tolist())

    print('\n\n\n********靠墙结束，开始排障*****\n\n\n')
    RealFlowRoute = []
    RealSegment = []
    i = 1
    for mvacflow in MVACFlow_Against_Wall:
        print('\n\n\n=================排障：第%d条管=======================' % i)
        #由一条mvacflow得到一根管道的Segment
        Segment= put_mvacFlow(StructWorkArea3D_With_GraFlow_With_MVAV, GraFlow_temp,
                            MVACFlow_Against_Wall, mvacflow, LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict)
        Point_number = 0
        for segment in Segment:
            
            lowest_z, StructWorkArea3D_With_GraFlow_With_MVAV = MVAC_put_output(mvacflow, Point_number,StructWorkArea3D_With_GraFlow_With_MVAV,
                                                StructWorkArea2D, segment, Z_Max, LenPixel)
            Point_number +=1
        
        #恢复实际值
        realSegment,realFlowRoute = ReturnToRealCoord(Segment,LenPixel)
        RealSegment.append(realSegment)
        RealFlowRoute.append(realFlowRoute)
        i += 1
    print('RealFlowRoute',RealFlowRoute)
    print('\n\n\n********排障结束*****\n\n\n')

    StructWorkArea3D_With_GraFlow_With_MVAV = StructWorkArea3D_With_GraFlow_With_MVAV.astype(int)

    #################################保存与展示#################################

    # # plot_3D_model(StructWorkArea3D_With_GraFlow_With_MVAV)

    fill_Space_in_Beams(StructWorkArea3D_With_GraFlow_With_MVAV, Beams, LenPixel) #把梁上的Space掏空部分画上
    np.savez(os.path.dirname(os.getcwd())+"\Data.npz", StructWorkArea3D_With_GraFlow_With_MVAV)
    print('\nstart plotting')
    plot_3D_model(StructWorkArea3D_With_GraFlow_With_MVAV)



def plot_3D_model(StructWorkArea3D_With_GraFlow_With_MVAC):
    '''
    后期甚至可以考虑在 put_output里完整这一堆for，使画图大大大大加快
    '''
    StructWorkArea3D_With_GraFlow_With_MVAC = StructWorkArea3D_With_GraFlow_With_MVAC[:,:,:]
    StructWorkArea3D_With_GraFlow_With_MVAC = StructWorkArea3D_With_GraFlow_With_MVAC[::20,::20,::3]

    cube1 = np.zeros(StructWorkArea3D_With_GraFlow_With_MVAC.shape, dtype='bool')
    cube2 = np.zeros(StructWorkArea3D_With_GraFlow_With_MVAC.shape, dtype='bool')
    cube3 = np.zeros(StructWorkArea3D_With_GraFlow_With_MVAC.shape, dtype='bool')
    cube4 = np.zeros(StructWorkArea3D_With_GraFlow_With_MVAC.shape, dtype='bool')
    for x in range(StructWorkArea3D_With_GraFlow_With_MVAC.shape[0]):
        for y in range(StructWorkArea3D_With_GraFlow_With_MVAC.shape[1]):
            for z in range(StructWorkArea3D_With_GraFlow_With_MVAC.shape[2]):
                # if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] == 0:  # 0为结构
                #     cube1[x, y, z] = 'true'
                if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] % 1000 == 61:  # 除以1000取模为61、62、63代表重力流
                    cube2[x, y, z] = 'true'
                if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] % 1000 == 62:
                    cube2[x, y, z] = 'true'
                if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] % 1000 == 63:
                    cube2[x, y, z] = 'true'
                if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] % 1000 == 127:  # 除以1000取模为127为横梁
                    cube3[x, y, z] = 'true'
                if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] % 1000 == 71:  # 除以1000取模为71、72、73代表风管
                    cube4[x, y, z] = 'true'  # 200为风管
                if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] % 1000 == 72:
                    cube4[x, y, z] = 'true'  # 200为风管
                if StructWorkArea3D_With_GraFlow_With_MVAC[x, y, z] % 1000 == 73:
                    cube4[x, y, z] = 'true'  # 200为风管

    voxels = cube1 | cube2 | cube3 | cube4

    colors = np.empty(voxels.shape, dtype=object)

    colors[cube1] = 'black'  # 0为结构，展示为黑色
    colors[cube2] = 'red'  # 100代表水管，展示为红色
    colors[cube3] = 'blue'  # 127为横梁，展示为蓝色
    colors[cube4] = 'yellow'  # 200为风管,展示为黄色

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.voxels(voxels, facecolors=colors, edgecolor='k')
    ax.invert_zaxis()
    plt.show()


#############  子函数 ###################
def find_corridor(StructWorkArea2D):

    Vertical = [np.argwhere(StructWorkArea2D[0,:]==255).min(),np.argwhere(StructWorkArea2D[0,:]==255).max()]
    Horizontal =  [np.argwhere(StructWorkArea2D[:,0]==255).min(),np.argwhere(StructWorkArea2D[:,0]==255).max()]
    print('Vertical',Vertical)
    print('Horizontal',Horizontal)
    return Vertical, Horizontal


def processing_pipes(Pipes, LenPixel):
    """
    1、按规则，为每条管道写入gap、安装空间等信息；
    2、增加包含包裹材料厚度关键字NewSize
    3、并按新Size为管道排序
    4、为每条管线分配Value
    5、扩充管道newsize和NewSizePixelLen，成为一个列表，列表元素为管道每一线段的长宽属性
    """

    for GraFlow in Pipes[0]:

        GraFlow["Space"], GraFlow['NewSize'],  GraFlow["SpacePixelLen"], GraFlow['NewSizePixelLen'] \
         = space(GraFlow['Type'], GraFlow['Size'], GraFlow['Insulation'], LenPixel)

        GraFlow['Ratio'] = ratio(GraFlow['Size'][0])
        flow_Newsize_Expansion(GraFlow)

    Pipes[0] = sorted(Pipes[0], key = lambda x: x['NewSize'][0][0], reverse = True)
  
    for Mvac in Pipes[1]:
        Mvac["Space"], Mvac['NewSize'],  Mvac["SpacePixelLen"], Mvac['NewSizePixelLen'] \
         = space(Mvac['Type'], Mvac['Size'], Mvac['Insulation'], LenPixel)

        flow_Newsize_Expansion(Mvac)

    Pipes[1] = sorted(Pipes[1], key = lambda x: (x['NewSize'][0][0] * x['NewSize'][0][1]), reverse = True)



    PipesValueDict = {}
    
    i = 0
    for GraFlow in Pipes[0]:
    
        GraFlow['X_EqValue'] = 61 + i*1000
        GraFlow['Y_EqValue'] = 62 + i*1000
        GraFlow['Z_EqValue'] = 63 + i*1000        
        GraFlow['X_Eq_SpaceValue'] = 100 + i*1000
        GraFlow['Y_Eq_SpaceValue'] = 101 + i*1000
        GraFlow['Z_Eq_SpaceValue'] = 102 + i*1000   
        PipesValueDict[GraFlow['X_EqValue']] = i
        PipesValueDict[GraFlow['Y_EqValue']] = i
        PipesValueDict[GraFlow['Z_EqValue']] = i
        PipesValueDict[GraFlow['X_Eq_SpaceValue']] = i
        PipesValueDict[GraFlow['Y_Eq_SpaceValue']] = i
        PipesValueDict[GraFlow['Z_Eq_SpaceValue']] = i
        i += 1

    i= 0
    for MVAC in Pipes[1]:
    
        MVAC['X_EqValue'] = 71 + i*1000
        MVAC['Y_EqValue'] = 72 + i*1000
        MVAC['Z_EqValue'] = 73 + i*1000
        MVAC['X_Eq_SpaceValue'] = 200 + i*1000
        MVAC['Y_Eq_SpaceValue'] = 201 + i*1000
        MVAC['Z_Eq_SpaceValue'] = 202 + i*1000
        PipesValueDict[MVAC['X_EqValue']] = i
        PipesValueDict[MVAC['Y_EqValue']] = i
        PipesValueDict[MVAC['Z_EqValue']] = i
        PipesValueDict[MVAC['X_Eq_SpaceValue']] = i
        PipesValueDict[MVAC['Y_Eq_SpaceValue']] = i
        PipesValueDict[MVAC['Z_Eq_SpaceValue']] = i
        i += 1

    return PipesValueDict, Pipes
    


def calculate_lenpixel(StructWorkArea, Segment):  
    """
    阶段构建的都是平行与X或Y轴的；后续阶段可以引入坐标变换应对更复杂情况

    1、延长或缩短Segment至接触走廊；
    2、计算像素实际长度
    """
    [StartPoint, EndPoint] = Segment['Route']
    diff_X = StartPoint[0] - EndPoint[0]
    diff_Y = StartPoint[1] - EndPoint[1]

    LenPixel = Segment['LenSegment'] / max(abs(StartPoint[1] - EndPoint[1]),abs(StartPoint[0] - EndPoint[0])+1)

    return LenPixel



def bulid_StructWorkArea3D_temp(HighInfo, LenPixel, StructWorkArea2D):

    H_Max = HighInfo['h_floor'] - HighInfo['h_false'] - HighInfo['thick_floor'] - HighInfo['thick_light']
    global Z_Max
    Z_Max = np.ceil(H_Max / LenPixel).astype(int)

    #构建全0 3d骨架，加上StruWorkArea2D由广播机制快速得到StructWorkArea3D_Temp 
    StructWorkArea3D_Temp = np.zeros((StructWorkArea2D.shape[0], StructWorkArea2D.shape[1],Z_Max)) + StructWorkArea2D[:,:,np.newaxis]

    return Z_Max, H_Max, StructWorkArea3D_Temp

#梁都是接触顶的
#输入的梁可能原来1/3，2/3处本来就有方形的孔，如果自己开孔，就开圆孔。
def processing_beams(StructWorkArea3D_temp, Beams, LenPixel):
    '''
    StructWorkArea3D：加上了各条梁的3D array。“注意各条梁的Value各不相同，但mod 1000值都为0
    '''   
    global  BeamsValueDict
    BeamsValueDict = {}
    i = 0
    for beam in Beams:

        beam['Value'] = 127 + i*1000
        BeamsValueDict[beam['Value']] = i
        i += 1
        HalfWidthPixel = math.ceil(beam['BWidth'] / LenPixel /2)#宽度像素个数的一半
        DepthPixel     = math.ceil(beam['BDepth'] / LenPixel)#深度像素个数
        beam['DepthPixel'] = DepthPixel
        if beam['Route'][0][0]-beam['Route'][1][0]==0: #梁平行于Y轴            
            if beam['Route'][0][1] < beam['Route'][1][1]: #如果梁的方向从小到大
                left = beam['Route'][0] #让第一个点为梁的左边
                right = beam['Route'][1]
            else:
                left = beam['Route'][1] #让第二个点为梁的左边
                right = beam['Route'][0]
            
            XofPoint = beam['Route'][0][0]
            OneThirdY = left[1]+abs(math.ceil((left[1]-right[1])/3))
            TwoThirdY = left[1]+abs(math.ceil((left[1]-right[1])*2/3))
            ZofPoint = 0 + math.ceil(DepthPixel/2)
            beam['ThirdPoints'] = [[XofPoint, OneThirdY, ZofPoint], [XofPoint,TwoThirdY, ZofPoint]] #孔在空间中的坐标点
            beam['holeLenth'] = math.ceil(DepthPixel/6) #梁的孔的半径或者1/2边长
            beam['ifhole'] = False  #目前都认为原来的梁是没有孔的，在排管时要自己开原孔
            '''增加xyz_scope array, shape = (3,2), 里面写了梁的X、Y、Z轴的范围'''
            beam['xyz_scope'] = np.array( [[ (left[0]-HalfWidthPixel), (right[0]+HalfWidthPixel) ], [ left[1], right[1] ], [ 0, DepthPixel] ])
            
            #把梁的值赋到area中
            StructWorkArea3D_temp[ (left[0]-HalfWidthPixel) : (left[0]+HalfWidthPixel+1), left[1] : (right[1]+1), 0 : (DepthPixel+1) ] =  beam['Value']

        elif  beam['Route'][0][1]-beam['Route'][1][1]==0:#梁平行于X轴
            if beam['Route'][0][0] < beam['Route'][1][0]:
                smallPoint = beam['Route'][0]
                bigPoint = beam['Route'][1]
            else:
                smallPoint = beam['Route'][1]
                bigPoint = beam['Route'][0]
            
            YofPoint = beam['Route'][0][1]
            OneThirdX = smallPoint[0]+abs(math.ceil((smallPoint[0]-bigPoint[0])/3))
            TwoThirdX = smallPoint[0]+abs(math.ceil((smallPoint[0]-bigPoint[0])*2/3))
            ZofPoint = 0 + math.ceil(DepthPixel/2)
            beam['ThirdPoints'] = [[OneThirdX, YofPoint, ZofPoint], [TwoThirdX,YofPoint, ZofPoint]] #孔在空间中的坐标点
            beam['holeLenth'] = math.ceil(DepthPixel/6) #梁的孔的半径或者1/2边长
            beam['ifhole'] = False  #目前都认为原来的梁是没有孔的，在排管时要自己开原孔
            '''增加xyz_scope array, shape = (3,2), 里面写了梁的X、Y、Z轴的范围'''
            beam['xyz_scope'] = np.array([ [smallPoint[0], bigPoint[0]], [(smallPoint[1]-HalfWidthPixel), (smallPoint[1]+HalfWidthPixel)], [0, DepthPixel] ])
            #把梁的值赋到area中
            StructWorkArea3D_temp[ smallPoint[0]:(bigPoint[0]+1) ,  (smallPoint[1]-HalfWidthPixel) : (smallPoint[1]+HalfWidthPixel+1), 0 : (DepthPixel+1) ] = beam['Value']            
    return Beams, BeamsValueDict,  StructWorkArea3D_temp


def fill_Space_in_Beams(StructWorkArea3D_temp, Beams, LenPixel):

    for beam in Beams:

        Width = beam['BWidth']
        Depth = beam['BDepth']

        HalfWidthPixel = math.ceil(Width / LenPixel / 2)  # 宽度像素个数的一半
        DepthPixel = math.ceil(Depth / LenPixel)  # 深度像素个数
        print('DepthPixel',DepthPixel)

        if beam['Route'][0][0] - beam['Route'][1][0] == 0:  # 梁平行轴Y轴（竖向）（误）

            if beam['Route'][0][1] < beam['Route'][1][1]:
                left = beam['Route'][0]
                right = beam['Route'][1]
            else:
                left = beam['Route'][1]
                right = beam['Route'][0]

            beamArea = StructWorkArea3D_temp[(left[0] - HalfWidthPixel): (left[0] + HalfWidthPixel + 1), left[1]: (right[1] + 1), 0: (DepthPixel + 1)]


        elif beam['Route'][0][1] - beam['Route'][1][1] == 0:  # 梁平行于X轴（横向）（误）

            if beam['Route'][0][0] < beam['Route'][1][0]:
                up = beam['Route'][0]
                down = beam['Route'][1]
            else:
                up = beam['Route'][1]
                down = beam['Route'][0]


            beamArea = StructWorkArea3D_temp[up[0]:(down[0] + 1), (up[1] - HalfWidthPixel): (up[1] + HalfWidthPixel + 1), 0: (DepthPixel + 1)]


        beamArea[beamArea % 1000 == 100] = beam['Value']
        beamArea[beamArea % 1000 == 101] = beam['Value']
        beamArea[beamArea % 1000 == 102] = beam['Value']







##############子子函数############
def ratio(Size):

    if Size<=100:             Ratio = 40

    elif 100<Size<150:        Ratio = 40

    elif 150<=Size<=200:      Ratio = 70

    elif 200<Size<225:        Ratio = 70

    elif 225<=Size<=250:      Ratio = 100

    elif 250<Size<300:        Ratio = 100

    elif 300<=Size<=350:      Ratio = 150

    elif 350<Size<400:        Ratio = 150

    elif Size>=400:           Ratio =200

    return Ratio



def Size_not_match():
    print("Size isn't match to any record from Rules") 
    sys.exit(0)



def space(Type, Size, InsulationThickness, LenPixel):
    Type = str(Type)
    Dia = Size[0]

    if Type[0] == '1':

        if Type[1] == '0':
            if Type[2]=="0":
                if Type[3]=="1":
                    if Type[4] == "1":
                            if Dia <= 50:           Space = 60
                            elif 80<= Dia <=100:    Space = 90
                            else:                   Space=90

                elif Type[3]=="2":
                    if Type[4] == "1":
                            if Dia <= 50:           Space = 60
                            elif 80<= Dia <=100:    Space = 90
                            else:                   Space=90

        elif Type[1]=="1":
            if Type[2]=="1":
                if Type[3]=="0":
                    if Type[4]=="1":
                        if Dia<=100:                Space=150
                        elif 100<Dia<=100:          Space=200
                        else:                       Space=200
        elif Type[1]=="2":
            if Type[2]=="0":
                if Type[3]=="3":
                    if Type[4] == "1":
                            if Dia <= 100:           Space = 50
                            elif 100<= Dia <=500:   Space = 60
                            else:                    Space=60
                elif Type[3]=="4":
                    if Type[4] == "1":
                            if Dia <= 100:           Space = 50
                            elif 100<= Dia <=500:    Space = 60
                            else:                    Space=60
                elif Type[3]=="5":
                    if Type[4] == "1":
                         if Dia <= 100:           Space = 50
                         elif 100<= Dia <=500:    Space = 60
                         else:                    Space=60
                elif Type[3]=="6":
                    if Type[4] == "1":
                            if Dia <= 100:           Space = 50
                            elif 100<= Dia <=500:    Space = 60
                            else:                    Space=60
    elif Type[0] == '2':
        if Type[1]=="0":
            if Type[2]=="0":
                if Type[3] == "0":
                    if Type[4]=="1":                Space=100

                    elif Type[4]=="2":                Space=75

            elif Type[2]=="2":
                if Type[3] == "1":
                    if Type[4]=="1":
                        if Dia<=100:                  Space=100
                        elif 100<Dia <= 350:          Space = 130
                        elif 350<Dia <= 600:          Space = 150
                        else:                         Space = 150
                if Type[3] == "2":
                    if Type[4]=="1":
                        if Dia<=100:                  Space=100
                        elif 100<Dia <= 350:          Space = 130
                        elif 350<Dia <= 600:          Space = 150
                        else:                         Space = 150
                if Type[3] == "3":
                    if Type[4]=="1":
                        if Dia<=100:                  Space=100
                        elif 100<Dia <= 350:          Space = 130
                        elif 350<Dia <= 600:          Space = 150
                        else:                         Space = 150
            elif Type[2]=="3":
                if Type[3] == "1":
                    if Type[4]=="1":
                        if Dia<=100:                  Space=120
                        elif 100<Dia <= 350:          Space = 140
                        elif 350<Dia <= 600:          Space = 150
                        else:                         Space = 150
                if Type[3] == "2":
                    if Type[4]=="1":
                        if Dia<=100:                  Space=120
                        elif 100<Dia <= 350:          Space = 140
                        elif 350<Dia <= 600:          Space = 150
                        else:                         Space = 150
                if Type[3] == "3":
                    if Type[4]=="1":
                        if Dia<=100:                  Space=120
                        elif 100<Dia <= 350:          Space = 140
                        elif 350<Dia <= 600:          Space = 150
                        else:                         Space = 150
            elif Type[2]=="4":
                if Type[3] == "4":
                    if Type[4]=="1":
                        if Dia<=100:                  Space=85
                        elif 100<Dia <= 60:           Space = 115
                        else:                         Space = 115


    NewSize = Size + np.array([InsulationThickness*2, InsulationThickness*2])

    SpacePixelLen = np.ceil( Space/LenPixel ).astype(int)
    NewSizePixelLen = np.ceil( NewSize/LenPixel ).astype(int)

    return Space, NewSize, SpacePixelLen, NewSizePixelLen

if __name__ == '__main__':
    main()





