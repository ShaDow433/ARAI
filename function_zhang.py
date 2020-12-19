'''
Descripttion: functions about ARAI 
version: v1.1
Author: Zhiting Zhang
email: 1149357968@qq.com
Date: 2020-09-18 01:23:53
LastEditors: Zhiting Zhang
LastEditTime: 2020-12-13 22:48:46
'''
import numpy as np
import math






####处理管道部分###


'''
name: flow_Newsize_Expansion
msg: 扩充管道newsize和NewSizePixelLen，成为一个列表，列表元素为管道每一线段的长宽属性
扩充前： flow['NewSize'] = {x,z}
扩充后： flow['NewSize'] = {{x,z},{x,z},{x,z},{x,z},{x,z}} 个数为len(flow['Route']) - 1
param {flow} 
return { } 
'''
def flow_Newsize_Expansion (flow):
    number = len(flow['Route']) - 1

    flow['NewSize'] = [flow['NewSize']] * number
    flow['NewSizePixelLen'] = [flow['NewSizePixelLen']] * number
 
    print("newsize is ",flow['NewSize'])
    print("NewSizePixelLen is ",flow['NewSizePixelLen'])
    
####靠墙处理部分####

'''
name: Against_wall_MVACFlow
msg: #将风管集合靠墙排布，修改每根管道的route，返回新的风管集合
param {StructWorkArea3D_With_GraFlow_MVAC, MVACFlow, LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict} 
return {MVACFlow} 
'''
def Against_wall_MVACFlow(StructWorkArea3D_With_GraFlow_MVAC, MVACFlow, LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict):
    print('\nTest in Against_wall_MVACFlow():\n')
    print('Before Against_wall_MVACFlow:',MVACFlow)
    #Temporary_StructWorkArea3D_With_GraFlow_MVAC只是用于下面Against_wall函数靠墙处,并不是真正用于输出的矩阵
    Temporary_StructWorkArea3D_With_GraFlow_MVAC = StructWorkArea3D_With_GraFlow_MVAC.copy()
    #把所有管线的z轴都调到最高,z=0
    MVACFlow = up_graflow(MVACFlow)
    #每条管线进行遍历,mvacflow_number为第几个管线
    i = 1
    for mvacflow_number in range(len(MVACFlow)):
        print('====================第%d条管============================='%i)
        i+=1
        Point_Number = 0     #表示现在是管线的第几个坐标
        while(Point_Number<len(MVACFlow[mvacflow_number]['Route'])-2):  #如果是最后一个坐标,说明这条管线已经处理完了
            #把当前线段起始点和终点往距离少的一遍靠近(坐标改变)
            MVACFlow[mvacflow_number] =  MVAC_ArrangeSegment_Against_wall(Point_Number,MVACFlow[mvacflow_number],Temporary_StructWorkArea3D_With_GraFlow_MVAC)
            Point_Number+=1
        print('MVACFlow[mvacflow_number] 1:\n', MVACFlow[mvacflow_number])
        print('开始 put_finalsegment()')
        #最后一个线段的往左边靠墙
        MVACFlow[mvacflow_number] = MVAC_Arrange_final_segment_Against_wall(Point_Number,MVACFlow[mvacflow_number], Temporary_StructWorkArea3D_With_GraFlow_MVAC)
        #修改风管的z坐标
        MVACFlow[mvacflow_number] = Add_Z_For_Against_wall_MVACFlow(MVACFlow[mvacflow_number])
        # 根据更新好了的坐标去排布管线(不考虑冲突直接排布),更新Temporary_StructWorkArea3D_With_GraFlow_MVAC
        Temporary_StructWorkArea3D_With_GraFlow_MVAC = pre_put_mvacflow(MVACFlow[mvacflow_number], Temporary_StructWorkArea3D_With_GraFlow_MVAC, LenPixel)
    print('Against_wall_MVACFlow Test out \n\n')
    return MVACFlow



'''
name: MVAC_ArrangeSegment_Against_wall
msg:#在Against_wall_MVACFlow中调用
    #效果 将一根管道各线段的头尾坐标更新，得到靠墙排布的管道。 返回这根新的管道
    #缺陷：当某一线段需要下降时，所有线段都会下降  
param {Point_Number, mvacflow, StructWorkArea3D_With_GraFlow_MVAC} 
return {mvacflow} 
'''
def MVAC_ArrangeSegment_Against_wall(Point_Number, mvacflow, StructWorkArea3D_With_GraFlow_MVAC):
    print('\n===Enter  in Against_wall_MVAC--->MVAC_ArrangePipe_Against_wall()')

    Start_point, Final_point = mvacflow['Route'][Point_Number], mvacflow['Route'][Point_Number+1]
    #判断这个线段的方向
    Direction_Flat=Direction_Segment(Start_point, Final_point)
    LEN,down,top = calculate_corridor_topdown(Start_point, Final_point, StructWorkArea3D_With_GraFlow_MVAC)
    print('down in Against wall():',down)
    print('top in Against_wall()',top)
    #当前线段是沿着Y轴方向
    if Direction_Flat:
        print('当前线段是沿着Y轴方向')       
        #判断下一个线段是沿着X轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
        if mvacflow['Route'][Point_Number+1][0] < mvacflow['Route'][Point_Number+2][0]:
            mvacflow = Find_FromLtoS(Point_Number, top, down, mvacflow, 0, StructWorkArea3D_With_GraFlow_MVAC)               
            
        #判断下一个线段是沿着X轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
        elif mvacflow['Route'][Point_Number + 1][0] > mvacflow['Route'][Point_Number + 2][0]:
            mvacflow = Find_FromStoL(Point_Number, top, down, mvacflow, 0, StructWorkArea3D_With_GraFlow_MVAC)
                               
        else:
            raise Exception('Eoor2 in Against_wall()')

    # 当前线段是沿着x轴方向
    else:
        print('当前线段是沿着X轴方向')
        # 判断下一个线段是沿着Y轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
        if mvacflow['Route'][Point_Number + 1][1] < mvacflow['Route'][Point_Number + 2][1]:
            mvacflow = Find_FromLtoS(Point_Number, top, down, mvacflow, 1, StructWorkArea3D_With_GraFlow_MVAC)            
            
        # 判断下一个线段是沿着Y轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
        elif mvacflow['Route'][Point_Number + 1][1] > mvacflow['Route'][Point_Number + 2][1]:
            mvacflow = Find_FromStoL(Point_Number, top, down, mvacflow, 1, StructWorkArea3D_With_GraFlow_MVAC)            
            
        else:
            raise Exception('Eoor2 in Against_wall()')           
    print('Out test in MVAC_ArrangePipe_Against_wall--->Against_wall()')
    return mvacflow


'''
name: MVAC_Arrange_final_segment_Against_wall
msg: #在Against_wall_MVACFlow中调用
    #效果 将最后一个管道各线段的头尾坐标更新，得到靠墙排布的管道。 返回这根新的管道
    #缺陷：当某一线段需要下降时，所有线段都会下降
param {Point_Number, mvacflow, StructWorkArea3D_With_GraFlow_MVAC} 
return {mvacflow} 
'''
def MVAC_Arrange_final_segment_Against_wall(Point_Number, mvacflow, StructWorkArea3D_With_GraFlow_MVAC):
    print('\n================Test in put_final_segment()=====================')
    print('Route before put_finial():',mvacflow['Route'])
    Start_point, Final_point = mvacflow['Route'][Point_Number], mvacflow['Route'][Point_Number + 1]
    # 判断这个线段的方向
    Direction_Flat = Direction_Segment(Start_point, Final_point)
    LEN, down, top = calculate_corridor_topdown(Start_point, Final_point, StructWorkArea3D_With_GraFlow_MVAC)
    print('Start_point',Start_point)
    print('Final_point',Final_point)
    print('LEN:',LEN)
    print('down:',down)
    print('top:',top)

    #如果是单线段管线
    if len(mvacflow['Route'])==2:        
        if Direction_Flat:  # 当前线段是沿着Y轴方向            
            if Start_point[1] > Final_point[1]: # 如果线段沿着Y轴从大到小,那么线段就想X的正方向靠
                mvacflow = Find_FromLtoS(Point_Number, top, down, mvacflow, 0, StructWorkArea3D_With_GraFlow_MVAC)            
            else: # 如果线段沿着Y轴从小到大,那么线段就想X的反方向靠
                mvacflow = Find_FromStoL(Point_Number, top, down, mvacflow, 0, StructWorkArea3D_With_GraFlow_MVAC)                    
        else:               # 当前线段是沿着x轴方向            
            if Start_point[0] > Final_point[0]:# 当前线段是沿着X轴从大到小
                mvacflow = Find_FromLtoS(Point_Number, top, down, mvacflow, 1, StructWorkArea3D_With_GraFlow_MVAC)                
            else: # 沿着X轴从小到大
                mvacflow = Find_FromStoL(Point_Number, top, down, mvacflow, 1, StructWorkArea3D_With_GraFlow_MVAC)
                
    #如果不是单线段管线
    else:
        print('#如果不是单线段管线')
        
        if Direction_Flat:    # 当前线段是沿着Y轴方向         
            #如果上一个线段是X从小到大,那本线段就得按X从小到大找
            if mvacflow['Route'][Point_Number][0]<mvacflow['Route'][Point_Number-1][0]:
                mvacflow = Find_FromStoL(Point_Number, top, down, mvacflow, 0, StructWorkArea3D_With_GraFlow_MVAC)
            # 如果上一个线段是X从大到小,那本线段就得向X的负方向靠
            else:
                mvacflow = Find_FromLtoS(Point_Number, top, down, mvacflow, 0, StructWorkArea3D_With_GraFlow_MVAC)       
        else:                 # 当前线段是沿着X轴方向
            # 如果上一个线段是Y从小到大,那本线段就得向Y的正方向靠
            if mvacflow['Route'][Point_Number][1]<mvacflow['Route'][Point_Number-1][1]:
                mvacflow = Find_FromStoL(Point_Number, top, down, mvacflow, 1, StructWorkArea3D_With_GraFlow_MVAC)                
            # 如果上一个线段是Y从大到小,那本线段就得向Y的负方向靠
            else:
                mvacflow = Find_FromLtoS(Point_Number, top, down, mvacflow, 1, StructWorkArea3D_With_GraFlow_MVAC)
    print('Route after put_finial():',mvacflow['Route'])            
    return mvacflow


'''
name: Get_Start_Index
msg:   找到竖直平面zoom中最高(Start_Index_Ver尽量小)，最靠小/大端的点坐标。
        #LSFlag 12 表示找到最靠小端，即Start_Index_Hor值尽量小；21反之
param {zoom:二维数组,
        LSFlag: 寻找方式标志} 
return {Start_Index_Hor,Start_Index_Ver} 
'''
def Get_Start_Index(zoom,LSFlag):

    detact_zoom_T = zoom.T 
    space_list_t = np.argwhere(detact_zoom_T == 255)
    if LSFlag == 12:
        Start_Index = np.fliplr(space_list_t)[0]
        Start_Index_Hor = int(Start_Index[0])
        Start_Index_Ver = int(Start_Index[1])
    elif LSFlag == 21:
        space_list = np.fliplr(space_list_t)
        Start_Index_Ver = np.min(space_list,axis=0)[1]
        for i in range(len(space_list)):
            if space_list[i][1]>Start_Index_Ver:
                Start_Index_Hor = space_list[i-1][0]
                break
    return Start_Index_Hor,Start_Index_Ver

'''
name: Find_FromLtoS
msg: #在MVAC_ArrangeSegment_Against_wall,MVAC_Arrange_final_segment_Against_wall中调用
    #输入：
    # Point_Number, 管道的第n段
    # top, down,  检测切面的左右两顶点
    # mvacflow,   当前风管
    # direction,  direction = 0 表示当前线段沿着Y轴， =1 沿X轴
    # StructWorkArea3D_With_GraFlow_MVAC  整体空间
    #返回值：
    # mvacflow    当前风管
    #功能:按照坐标数值从大到小的准则，检测切面中是否有空位放入风管的第n段，如果有，就更新风管的route，如果没有，则报错。

param {Point_Number, top, down, mvacflow, direction, StructWorkArea3D_With_GraFlow_MVAC} 
return {mvacflow} 
'''
def Find_FromLtoS(Point_Number, top, down, mvacflow, direction, StructWorkArea3D_With_GraFlow_MVAC):    
    if direction == 0:
        print('condition a')
    else:
        print('condition c')
    
    while 1:        
        if down[2] == StructWorkArea3D_With_GraFlow_MVAC.shape[2]:#到最后一层找不到
            raise Exception('In Against_wall():遍历完了所有层，没有找到合适的位置')
        else: #修改管道z轴            
            for route in mvacflow['Route']:#整体管道下降
                route[2] = down[2]
        print('down,top:', down, top)
        if direction == 0:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0]:top[0], down[1], down[2]:]
        else:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0], down[1]:top[1], down[2]:]  

        original_flow_newsize = mvacflow['NewSizePixelLen'][Point_Number].copy()
        detact_zoom_copy = detact_zoom.copy()        
        zoomshape = np.shape(detact_zoom)

        flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]
        Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
        Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2

        if 255 in detact_zoom and zoomshape[0]>=Mvacflow_wedth_pixel: #走廊比管道宽
            deform_flag = 0
            horizon_deform_flag = 0
            while 1: 
                flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]
                # 因为管线两边都需要安装空间,所以space剩以2
                Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
                Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2

                Start_Index_Hor,Start_Index_Ver = Get_Start_Index(detact_zoom_copy,21)

                if Start_Index_Hor - Mvacflow_wedth_pixel>=0:#可行空间大于宽度
                    if detact_zoom[Start_Index_Hor - Mvacflow_wedth_pixel:Start_Index_Hor, Start_Index_Ver:Start_Index_Ver + Mvacflow_depth_pixel].sum() == 255*Mvacflow_wedth_pixel*Mvacflow_depth_pixel:              
                        
                        New_val = down[direction] + (Start_Index_Hor - math.ceil(Mvacflow_wedth_pixel / 2))
                        #改变这个线段所有坐标(也就是头尾两个点)的x/y值
                        mvacflow['Route'][Point_Number][direction] = New_val  #沿y轴时，修改x坐标，direction=0，反之为1
                        mvacflow['Route'][Point_Number + 1][direction] = New_val

                        #修改后面线段的NewSizePixelLen，和当前线段一致
                        Change_leftover_flow_Newsize(Point_Number,mvacflow,flow_newsize)                                    
                        return mvacflow
                    else: #放不下
                        if deform_flag == 0:
                            detact_zoom_copy=detact_zoom_copy[0:Start_Index_Hor,:] #矩阵x-1
                        else:
                            if horizon_deform_flag == 0: #处于缩小宽度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,0):
                                    pass
                                    #改变宽度进入下一次检测
                                else: #不能再缩小宽度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                            else:  #处于缩小高度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,1):
                                    pass
                                    #改变高度进入下一次检测
                                else: #不能再缩小高度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 0 #结束缩小高度循环
                                    detact_zoom_copy=detact_zoom_copy[0:Start_Index_Hor,:] #矩阵x-1
                else:#可行空间x小于管道宽度
                    if horizon_deform_flag == 0: #处于缩小宽度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,0):
                            pass  #改变宽度进入下一次检测
                        else: #不能再缩小宽度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                    else:  #处于缩小高度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,1):
                            pass  #改变高度进入下一次检测
                        else: #不能再缩小高度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            horizon_deform_flag = 0 #结束缩小高度循环
                            down[2] += 1
                            top[2] += 1
                            break
        else: 
            raise Exception('所有层都没有空位或者空间宽度小于管道宽度')   

'''
name: Find_FromStoL
msg: #在MVAC_ArrangeSegment_Against_wall,MVAC_Arrange_final_segment_Against_wall中调用
    #输入：
    # Point_Number, 管道的第n段
    # top, down,  检测切面的左右两顶点
    # mvacflow,   当前风管
    # direction,  direction = 0 表示当前线段沿着Y轴， =1 沿X轴
    # StructWorkArea3D_With_GraFlow_MVAC  整体空间
    #返回值：
    # mvacflow    当前风管
    #功能:按照坐标数值从小到大的准则，检测切面中是否有空位放入风管的第n段，如果有，就更新风管的route，如果没有，则报错。

param {Point_Number, top, down, mvacflow, direction, StructWorkArea3D_With_GraFlow_MVAC} 
return {mvacflow} 
'''
def Find_FromStoL(Point_Number, top, down, mvacflow, direction, StructWorkArea3D_With_GraFlow_MVAC): 
    if direction == 0:
        print('condition b')
    else:
        print('condition d')
    

    while 1:
        if down[2] == StructWorkArea3D_With_GraFlow_MVAC.shape[2] :
            raise Exception('In Against_wall():遍历完了所有层，没有找到合适的位置')
        else:
            for route in mvacflow['Route']:
                route[2] = down[2]
        print('down,top:', down, top)   
        if direction == 0:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0]:top[0], down[1], down[2]:]
        else:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0], down[1]:top[1], down[2]:]      
        
        detact_zoom_copy = detact_zoom.copy()
        original_flow_newsize = mvacflow['NewSizePixelLen'][Point_Number].copy()
        zoomshape = np.shape(detact_zoom_copy)

        flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]
        Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
        Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2

        if 255 in detact_zoom and zoomshape[0]>=Mvacflow_wedth_pixel:
            deform_flag = 0
            horizon_deform_flag = 0
            while 1:
                # 更新修改过长宽的管道所需要的总宽度和总深(高)度
                flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]                
                Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
                Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2
                #得到检测起点
                Start_Index_Hor,Start_Index_Ver = Get_Start_Index(detact_zoom_copy,12)

                test_len = int(zoomshape[0] - (Start_Index_Hor + Mvacflow_wedth_pixel)) 
                if test_len >0:
                    if detact_zoom[Start_Index_Hor:Start_Index_Hor + Mvacflow_wedth_pixel,Start_Index_Ver: Start_Index_Ver + Mvacflow_depth_pixel].sum() == 255*Mvacflow_wedth_pixel*Mvacflow_depth_pixel:
                        #线段沿y轴时输入的direction为0，需要更改的是x，所以用mvacflow['Route'][Point_Number][direction]表示 
                        #New_val = top[direction] - (zoomshape[0] - (Start_Index_Hor + math.ceil(Mvacflow_wedth_pixel/2)) )
                        New_val = down[direction] + Start_Index_Hor + math.ceil(Mvacflow_wedth_pixel/2)                      
                        print('New_val',New_val)
                        #改变这个线段所有坐标(也就是头尾两个点)的x值
                        mvacflow['Route'][Point_Number][direction] = New_val
                        mvacflow['Route'][Point_Number+1][direction] = New_val

                        #修改后面线段的NewSizePixelLen，和当前线段一致
                        Change_leftover_flow_Newsize(Point_Number,mvacflow,flow_newsize)
                        return mvacflow
                    else: #放不下
                        if deform_flag == 0:
                            detact_zoom_copy=detact_zoom_copy[Start_Index_Hor + 1:,:] #矩阵x-1
                        else:
                            if horizon_deform_flag == 0: #处于缩小宽度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,0):
                                    pass
                                    #改变宽度进入下一次检测
                                else: #不能再缩小宽度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                            else:  #处于缩小高度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,1):
                                    pass
                                    #改变高度进入下一次检测
                                else: #不能再缩小高度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 0 #结束缩小高度循环
                                    detact_zoom_copy=detact_zoom_copy[Start_Index_Hor + 1:,:] #缩小矩阵
                else:#可行空间x小于管道宽度
                    if horizon_deform_flag == 0: #处于缩小宽度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,0):
                            pass  #改变宽度进入下一次检测
                        else: #不能再缩小宽度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                    else:  #处于缩小高度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,1):
                            pass  #改变高度进入下一次检测
                        else: #不能再缩小高度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            horizon_deform_flag = 0 #结束缩小高度循环
                            down[2] += 1
                            top[2] += 1
                            break
        else: 
            raise Exception('所有层都没有空位或者空间宽度小于管道宽度')  


'''
name: Add_Z_For_Against_wall_MVACFlow
msg: #在Against_wall_MVACFlow中调用
     #修改管道z值，从管道顶点变为管道中心点
param {mvacFlow} 
return {mvacFlow} 
'''
def Add_Z_For_Against_wall_MVACFlow(mvacFlow):
    mvacFlow['Route'] = np.array(mvacFlow['Route'])
    for point_number in range(len(mvacFlow['Route']) -1 ):
        depth = math.ceil(mvacFlow['NewSizePixelLen'][point_number][1]/2) + mvacFlow['SpacePixelLen']
        mvacFlow['Route'] += [0, 0, depth]
    print('After Add_Z_For_Against_wall_MVACFlow  mvac Route is ')
    print(mvacFlow['Route'])
    return mvacFlow


'''
name: pre_put_mvacflow
msg: #在Against_wall_MVACFlow中调用
    #根据风管的不同类型给StructWorkArea3D_With_GraFlow_MVAC赋不同的值
    #输入的风管必须z值一样，缺陷是没有考虑风管中途下降的可能。下一版改善
param {mvacflow, StructWorkArea3D_With_GraFlow_MVAC, LenPixel} 
return {StructWorkArea3D_With_GraFlow_MVAC} 
'''
def pre_put_mvacflow(mvacflow, StructWorkArea3D_With_GraFlow_MVAC, LenPixel):
    print('Test in pre_put_graflow():', )

    Z = mvacflow['Route'][0][2]
    if Z != mvacflow['Route'][-1][2]:
        raise Exception('Error in pre_put_graflow()')

    for Point_Number in range(len(mvacflow['Route']) - 1):

        StartPoint = mvacflow['Route'][Point_Number]
        EndPoint = mvacflow['Route'][Point_Number + 1]

        FlagDirection = 'X_EqValue' if StartPoint[0] == EndPoint[0] else 'Y_EqValue'

        if FlagDirection == 'X_EqValue':
            Y_Star_Index = min(StartPoint[1], EndPoint[1])
            Y_End_Index = max(StartPoint[1], EndPoint[1])

            X_Star_Index = StartPoint[0] - np.ceil(mvacflow['NewSizePixelLen'][Point_Number][0] / 2).astype(int)
            X_End_Index = StartPoint[0] + np.ceil(mvacflow['NewSizePixelLen'][Point_Number][0] / 2).astype(int)

            Z_Star_Index = StartPoint[2] - np.ceil(mvacflow['NewSizePixelLen'][Point_Number][1] / 2).astype(int)
            Z_End_Index = StartPoint[2] + np.ceil(mvacflow['NewSizePixelLen'][Point_Number][1] / 2).astype(int)

            #安装空间赋值起点终点
            x_s , x_e = (X_Star_Index - mvacflow['SpacePixelLen']) , (X_End_Index + mvacflow['SpacePixelLen'] + 1)
            y_s , y_e = (Y_Star_Index) , (Y_End_Index + 1)
            z_s , z_e = (Z_Star_Index - mvacflow['SpacePixelLen']) , (Z_End_Index + mvacflow['SpacePixelLen'] + 1) 
            #安装空间赋值
            StructWorkArea3D_With_GraFlow_MVAC[x_s:x_e,y_s: y_e, z_s:z_e ] = mvacflow['X_Eq_SpaceValue']
            #管道空间赋值
            StructWorkArea3D_With_GraFlow_MVAC[X_Star_Index:X_End_Index + 1, Y_Star_Index: Y_End_Index + 1, (Z_Star_Index):(Z_End_Index + 1)] = mvacflow['X_EqValue']
            X_Eq_SpaceValue_area = StructWorkArea3D_With_GraFlow_MVAC[x_s:x_e, y_s: y_e, z_s:z_e]

        elif FlagDirection == 'Y_EqValue':
            X_Star_Index = min(StartPoint[0], EndPoint[0])
            X_End_Index = max(StartPoint[0], EndPoint[0])

            Y_Star_Index = StartPoint[1] - np.ceil(mvacflow['NewSizePixelLen'][Point_Number][0] / LenPixel / 2).astype(int)
            Y_End_Index = StartPoint[1] + np.ceil(mvacflow['NewSizePixelLen'][Point_Number][0] / LenPixel / 2).astype(int)

            Z_Star_Index = StartPoint[2] - np.ceil(mvacflow['NewSizePixelLen'][Point_Number][1] / 2).astype(int)
            Z_End_Index = StartPoint[2] + np.ceil(mvacflow['NewSizePixelLen'][Point_Number][1] / 2).astype(int)

            #安装空间赋值起点终点
            x_s , x_e = (X_Star_Index) , (X_End_Index + 1)
            y_s , y_e = (Y_Star_Index - mvacflow['SpacePixelLen']) , (Y_End_Index + mvacflow['SpacePixelLen'] + 1)
            z_s , z_e = (Z_Star_Index - mvacflow['SpacePixelLen']) , (Z_End_Index + mvacflow['SpacePixelLen'] + 1) 

            StructWorkArea3D_With_GraFlow_MVAC[x_s:x_e, y_s: y_e, z_s:z_e]  = mvacflow['Y_Eq_SpaceValue']
            StructWorkArea3D_With_GraFlow_MVAC[X_Star_Index:X_End_Index + 1, Y_Star_Index: Y_End_Index + 1, (Z_Star_Index):(Z_End_Index + 1)] = mvacflow['Y_EqValue']


    print('pre put Test Out\n\n\n')
    return StructWorkArea3D_With_GraFlow_MVAC


'''
name: check_mvacflow_size
msg: #在modify_mvacflow_size中调用
    # 检测风管的宽度和高度是否超过6比1
param {mvacflow,Point_Number} 
return {Bool} 
'''
def check_mvacflow_size(mvacflow,Point_Number):
    flowWidth = mvacflow['NewSizePixelLen'][Point_Number][0]
    flowdepth = mvacflow['NewSizePixelLen'][Point_Number][1]

    res =  flowWidth / flowdepth 
    if res > 6 or res < 1/6 :
        return False
        
    else:
        return True


'''
name: modify_mvacflow_size
msg: #修改风管的宽高比，保持总面积不变,减小高度以后会提高管道线段中心点的z值，使管道最高点和之前相同
    #direction 为决定让管道减小宽度还是减小高度，输入0减小宽度，输入1减小高度
param {mvacflow,Point_Number,direction} 
return {Bool} 
'''
def modify_mvacflow_size(mvacflow,Point_Number,direction):
    thisSegSize = mvacflow['NewSizePixelLen'][Point_Number]
    area = thisSegSize[0] * thisSegSize[1]
    if direction == 0 :
        thisSegSize[0] -= 1
        thisSegSize[1] =  int (area/thisSegSize[0])
    elif direction == 1:
        thisSegSize[1] -= 1
        thisSegSize[0] =  int (area/thisSegSize[1])

    if check_mvacflow_size(mvacflow,Point_Number) :#变形后再次判断是否符合1:6
        if direction == 1:
            for index in range(Point_Number,len(mvacflow['route'])):
                mvacflow['route'][index][2] -= 1 #提高管道后面线段中心点的z值
        return True
    else :
        return False


####排障处理部分####

#修改了平行撞管部分，替他部分基本没变
#修改了参数的名字，MVACFlow为风管集合，mvacflow为单条风管
'''
name: put_mvacFlow
msg: StructWorkArea3D_With_GraFlow, 整体空间
    MVACFlow, 风管集合
    mvacflow, 单条风管
    LenPixel, 长度比例
    Beams, 横梁集合
    LogPath, 日志
    PipesValueDict, 管道字典，用于寻找某根管道 
    BeamsValueDict  横梁字典
param {StructWorkArea3D_With_GraFlow, MVACFlow, mvacflow, LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict} 
return {Segment} 
'''
def put_mvacFlow(StructWorkArea3D_With_GraFlow, Graflow, MVACFlow, mvacflow, LenPixel, Beams, LogPath, PipesValueDict, BeamsValueDict):
    print('\n\nTest in put_MVACFlow:\n')
    #每条管线进行遍历
    print('\n\n\nmvacflow i:',mvacflow,'\n\n\n')
    # 每条管线的每条线段进行遍历,把管线分成几个线段,每个线段是一个数组,里面包括线段的起始点和终点,后续会插入一下转折点
    #Segment=[[(x1,y1),(x2,y2)],[(x2,y2),(x3,y3)]...]
    Segment = Create_Segment(mvacflow)
    print('1---- Original Segment:\n',Segment,'\n')
    '''定义FlagCrossBeam=[1,1,1,,1,0,0]'''
    '''remain_length_segment_number'''
    # 用来记录当前这个管线的各个大Segment中是否有撞梁
    FlagCrossBeam = {}
    for index_segment in range(len(Segment)+10):
        FlagCrossBeam[index_segment]=[]

    #一条管道分为大线段，大线段细分为小线段。
    segment_number = 0 # 当前是第几个大线段,也就是Segment中第几个数组
    while segment_number<len(Segment):

        Point_Number = 0     #表示现在是第几个小线段
        # 初始化起始点和终点为线段的头尾两点,检测冲突也是查看这Start_point,Final_point两个点之间是否有冲突
        Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
        while 1:
            print('the %d smallsegment in this Segment',Point_Number)
            print('start_point',Start_point)
            print('Final_point',Final_point)
            # print('Segment',Segment)
            flag, Return_List = Compare(mvacflow, Point_Number, StructWorkArea3D_With_GraFlow, Start_point,Final_point,FlagCrossBeam[segment_number])
            print(' compare flag is',flag)

            #如果Start_point到Final_point有冲突
            if flag != False:
                if flag==2 : #撞梁
                    print('\n Enter flag = 2')                    
                    NewSize = Calculate_MVACNewSize(mvacflow, Point_Number)
                    if NewSize <= 250:
                        print('\n Enter in if NewSize <= 250')
                        # 看当前起始点到终点穿梁的位置是否刚好满足要求,是的话返回flag_across=true,反之返回flag_across=false
                        flag_across = Check_Right(Start_point,Final_point, mvacflow, Point_Number, Beams, Return_List, \
                            StructWorkArea3D_With_GraFlow,LenPixel,PipesValueDict, BeamsValueDict)

                        #根据冲突点的value找到他是对应哪一条梁
                        beam_value=Return_List[0]
                        #beam_index为梁的索引
                        beam_index=BeamsValueDict[beam_value]
                        #找到梁的宽对应的像素个数
                        beam_width = math.ceil(Beams[beam_index]['BWidth']/LenPixel)
                        #计算出梁的点对应撞梁的点的高度差对应的像素个数
                        high_distance=math.ceil(beam_width/mvacflow['Ratio'])

                        if  flag_across:  #当前冲突的位置刚好满足穿梁要求

                            print('\n Enter in if flag_across==True,当前冲突的位置刚好满足穿梁要求')

                            #把冲突的点转进线段的坐标集合里面
                            '''Return_List[2]是质心'''
                            #计算起始地到冲突点的距离,更新遗留长度
                            remain_length += Calculate_distance(Start_point,Return_List[2])
                            # Point_Number +=1

                            #先判断线段的方向
                            segment_direction = Direction_Segment(Start_point, Final_point)
                            #先定义出梁的坐标跟撞梁的坐标一样
                            beam_out = Return_List[2].copy()
                            #如果是沿着y轴方向
                            if segment_direction:
                                #沿着y轴方向由小到大,x轴坐标不变
                                if Start_point[1] < Final_point[1]:
                                    beam_out[1] += beam_width
                                    beam_out[2] += high_distance
                                # 沿着y轴方向由大到小,x轴坐标不变
                                else:
                                    beam_out[1] -= beam_width
                                    beam_out[2] += high_distance
                            #计算出梁的坐标
                            #如果是沿着x轴方向
                            else:
                                #沿着x轴方向由小到大,y轴坐标不变
                                if Start_point[0] < Final_point[0]:
                                    beam_out[0] += beam_width
                                    beam_out[2] += high_distance
                                # 沿着x轴方向由大到小,y轴坐标不变
                                else:
                                    beam_out[0] -= beam_width
                                    beam_out[2] += high_distance
                            print('Segment before:',Segment)
                            ''' 增加穿梁点与梁背后的点'''
                            Segment[segment_number].insert((Point_Number + 1), Return_List[2])
                            Segment[segment_number].insert((Point_Number + 2), beam_out)
                            print('Segment after:', Segment)
                            print('Point_Number before:', Point_Number)
                            Point_Number += 2


                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                            print('2---- AfterProcessing Segment in flag_across:',Segment)
                            print('Point_Number after:',Point_Number)
                            print('len(Segment[segment_number]:',len(Segment[segment_number]))
                            print('OUT of if flag_across,当前冲突的位置刚好满足穿梁要求')
                            FlagCrossBeam[segment_number].append(Return_List[0])

                        else:
                            print('\nEnter in flag_cross==False, 当前冲突的位置不满足穿梁要求')
                            print('3---- Segment in this if in the begining:',Segment)
                            print('Conflic_Value, Conflict_Point, Confil_Cnenter, confli_center_go_back', Return_List[0],Return_List[1],Return_List[2],Return_List[3])

                            # 如果存在满足要求的穿孔位置,flag=true,返回满足要求所有穿孔的位置中离冲突点最近的一个(该点坐标不是在梁上,而是跟梁有一定距离,因为需要考虑安装空间和包裹)
                            # 反之返回flag=false
                            flag_right, The_right_point = Find_Best_Point(mvacflow, Return_List[0],Beams, Return_List[2],StructWorkArea3D_With_GraFlow, LenPixel,BeamsValueDict)


                            remain_length += Calculate_distance(Start_point, Return_List[2])

                            # 如果存在这个点
                            if flag_right:
                                print('\n in flag_right,存在Best_point')
                                print('Best Poing:', The_right_point)
                                #查看这条线段的前面部分是否已经穿梁了,如果是,那就不应该移动这条线段
                                #如果不是,那就可以移动这个线段。

                                if len(FlagCrossBeam[segment_number])!=0:        #说明前面装过了梁,这次又穿过另一个梁
                                    print('\nin  if len(FlagCrossBeam[segment_number])!=0:前面装过了梁,这次又穿过另一个梁')
                                    FlagCrossBeam[segment_number].append(Return_List[0])

                                    '''把回退后的点加进去'''
                                    Segment[segment_number].insert((Point_Number + 1), Return_List[3])
                                    Point_Number+=1

                                    #只有Z不一样
                                    if Return_List[2][0] == The_right_point[0] and Return_List[2][1] == The_right_point[1]:

                                        #当前小线段后面所有的点都下降
                                        Segment = Reduce_Z(Point_Number, Segment, segment_number, The_right_point[2] - Return_List[2][2])

                                        #在回退点下面加入垂直下降点
                                        Down_Point = Return_List[3].copy
                                        Down_Point[2] = The_right_point[2]
                                        Segment[segment_number].insert((Point_Number + 1), Down_Point)

                                        Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                                        remain_length = 0

                                    #存在XY不一样,Z是否一样未确定
                                    else:
                                        # 如果是冲突点的x坐标跟The_right_point点的坐标不一样
                                        if Return_List[2][0] != The_right_point[0]:
                                            Original_segment = Segment[segment_number].copy()

                                            #所处这段截至回退点
                                            Segment[segment_number] = Original_segment[:Point_Number + 1]

                                            #增加 回退点到Point_Change_X 这一段
                                            Point_Change_X = Return_List[3]
                                            Point_Change_X[0] = The_right_point[0]
                                            Segment.insert(segment_number+1, [Return_List[3], Point_Change_X])

                                            #不用改变z
                                            if Return_List[3][2] == The_right_point[2]:
                                                #原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[0] = The_right_point[0]

                                                Segment.insert(segment_number + 2, left_segment)

                                                #改变原本segment的下一个segment的首个点的X
                                                if segment_number+2 < len(Segment)-1:
                                                    Segment[segment_number + 3][0][0] = The_right_point[0]

                                            #需要改变z
                                            elif Return_List[3][2] != The_right_point[2]:
                                                #增加下降段
                                                Point_Change_X_Down = Point_Change_X.copy()
                                                Point_Change_X_Down[2] = The_right_point[2]
                                                Segment.insert(segment_number + 2, [Point_Change_X, Point_Change_X_Down])

                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[0] = The_right_point[0]

                                                Segment.insert(segment_number + 3, left_segment)

                                                # 改变原本segment的下一个segment的首个点的X
                                                if segment_number+3 < len(Segment)-1:
                                                    Segment[segment_number + 4][0][0] = The_right_point[0]

                                                #改变下降段后面所有段的点的Z值

                                                for i in range(segment_number + 3, len(Segment)):
                                                    for j in range(len(Segment[i])):
                                                        Segment[i][j][2] += (The_right_point[2] - Return_List[3][2])

                                            '''
                                            重新检测本segment到回退点这一段，它将发现没有冲突，从而把工作转移到我们新增加的segment
                                            默认新增加的segment没有冲突，否则就会产生bug！！！！
                                            '''
                                            Point_Number -= 1
                                            Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number+1]

                                            remain_length = 0 if segment_number==0 else remain_length_segment_number[segment_number-1]


                                        # 如果是冲突点的y坐标跟The_right_point点的坐标不一样
                                        elif Return_List[2][1] != The_right_point[1]:
                                            Original_segment = Segment[segment_number].copy()

                                            # 所处这段截至回退点
                                            Segment[segment_number] = Original_segment[:Point_Number + 1]

                                            # 增加 回退点到Point_Change_X 这一段
                                            Point_Change_Y = Return_List[3]
                                            Point_Change_Y[1] = The_right_point[1]
                                            Segment.insert(segment_number + 1, [Return_List[3], Point_Change_Y])

                                            # 不用改变z
                                            if Return_List[3][2] == The_right_point[2]:
                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[1] = The_right_point[1]

                                                Segment.insert(segment_number + 2, left_segment)

                                                # 改变原本segment的下一个segment的首个点的Y
                                                if segment_number + 2 < len(Segment)-1:
                                                    Segment[segment_number + 3][0][1] = The_right_point[1]

                                            # 需要改变z
                                            elif Return_List[3][2] != The_right_point[2]:
                                                # 增加下降段
                                                Point_Change_Y_Down = Point_Change_Y.copy()
                                                Point_Change_Y_Down[2] = The_right_point[2]
                                                Segment.insert(segment_number + 2,
                                                               [Point_Change_Y, Point_Change_Y_Down])

                                                # 原本segmetn剩余的point独立为一个segment
                                                left_segment = Original_segment[Point_Number:]
                                                for point in left_segment:
                                                    point[1] = The_right_point[1]

                                                Segment.insert(segment_number + 3, left_segment)

                                                # 改变原本segment的下一个segment的首个点的X
                                                if segment_number+3 < len(Segment)-1:
                                                    Segment[segment_number + 4][0][1] = The_right_point[1]

                                                # 改变下降段后面所有段的点的Z值
                                                for i in range(segment_number + 3, len(Segment)):
                                                    for j in range(len(Segment[i])):
                                                        Segment[i][j][2] += (The_right_point[2] - Return_List[3][2])


                                            '''
                                            重新检测本segment到回退点这一段，它将发现没有冲突，从而把工作转移到我们新增加的segment
                                            默认新增加的segment没有冲突，否则就会产生bug！！！！
                                            '''
                                            Point_Number -= 1
                                            Start_point, Final_point = Segment[segment_number][Point_Number], \
                                                                       Segment[segment_number][Point_Number + 1]

                                            remain_length = 0 if segment_number == 0 else remain_length_segment_number[
                                                segment_number - 1]

                                        else:
                                            raise Exception('Error in 撞梁，bestpoint与中心点不一致的处理过程中')

                                else:
                                    # 这是第一次穿梁,所以可以整体移动
                                    print('\nin else:这是第一次穿梁')
                                    # 这个线段之前没有穿梁,根据冲突点与The_right_point的坐标差异,移动整条线段,更新segment
                                    Segment = Remove(Segment, segment_number, Return_List[2], The_right_point, Point_Number, StructWorkArea3D_With_GraFlow, mvacflow)

                                    Point_Number = 0
                                    segment_number = 0
                                    # Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number+1]

                                    remain_length = 0 if segment_number==0 else remain_length_segment_number[segment_number-1]

                                    print('5-- Segment after processing:',Segment)
                                    print('OUT of this if \n\n\n')

                            #如果不存在这个点
                            else:
                                print('\n\nin put_pipe() if 不存在best_point,下降梁')
                                # 根据冲突点坐标计算绕过梁需要下降多少个像素

                                pixel_number = Calculate_Down_Beam(mvacflow, Beams, Return_List[0], Return_List[2],LenPixel, BeamsValueDict)
                                # 在线段中加入冲突点(也就是下降点)

                                print('pixel num:',pixel_number)
                                Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                                # 先判断线段的方向
                                #segment_direction = Direction_Segment(Start_point, Final_point)
                                # 先定义回退后的点为back_point
                                back_point = Return_List[3].copy()
                                
                                back_point_Down = back_point + [0,0,pixel_number]

                                '''#把回退后的点加进去'''
                                Segment[segment_number].insert((Point_Number + 1), back_point)
                                Segment[segment_number].insert((Point_Number + 2), back_point_Down)
                                Point_Number += 2
                                # 更新起始点和终点
                                Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                                remain_length = 0
                                print('Return_List',Return_List)
                                print('back_point',back_point)
                                print('back_point_Down',back_point_Down)

                                print('6--- After processing Segment:',Segment)
                                print('OUT of this if \n\n')
                            FlagCrossBeam[segment_number].append(Return_List[0])

                    #NewSize > 250,直接绕梁
                    else:
                        print('\n================\n Enter in if Else(NewSize >= 250)')
                        # 根据冲突点的坐标计算绕过梁需要下降多少个像素

                        print('Segment Before:', Segment)
                        for index in range(len(Segment)):
                            if not isinstance(Segment[index], list):
                                Segment[index] = Segment[index].tolist()

                        pixel_number = Calculate_Down_Beam(mvacflow, Beams, Return_List[0], Return_List[2],LenPixel, BeamsValueDict)
                        print('pixel_number',pixel_number)
                        # 在线段中加入冲突点(也就是下降点)

                        Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                        print('Segment after Reduce_Z:', Segment)

                        # 先定义回退后的点为back_point
                        back_point = np.array(Return_List[3])

                        back_point_Down = back_point + [0,0,pixel_number]

                        '''#把回退后的点加进去'''
                        Segment[segment_number].insert((Point_Number + 1), back_point)
                        Segment[segment_number].insert((Point_Number + 2), back_point_Down)
                        Point_Number += 2
                        # 更新起始点和终点
                        Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                        remain_length = 0
                        print('Segment after Out:', Segment)
                        print('out of this else\n======================\n')


                #平行撞管
                elif flag==3:
                    print('============================Enter in flag==3 平行撞管 special===============================')
                    print('segment before of pipe2')
                    print(Segment)
                    print('平行 conflictValue:', Return_List[0])
                    pixel_number = Find_point(Graflow, MVACFlow, mvacflow, StructWorkArea3D_With_GraFlow, PipesValueDict, Return_List.copy())

                    Segment,segment_number,Point_Number,Start_point,Final_point = Find_Room_MVACFlow(
                        Point_Number, pixel_number,segment_number,Start_point,Final_point,
                        Segment, StructWorkArea3D_With_GraFlow,
                        mvacflow,Return_List.copy(),FlagCrossBeam[segment_number])

                    print('segment after processing  in Find_Room_GraFlow:  ')
                    print(Segment,'\n')
                    print('=======================================Out================================\n\n')

                #两个线段交叉
                elif flag==4:
                    print('\n=========Enter in put_pipe flag=4 交叉 ')
                    print('Segment before:', Segment)
                    # 计算需要下降多少像素,绕过线段
                    pixel_number = Find_point(Graflow, MVACFlow, mvacflow, StructWorkArea3D_With_GraFlow, PipesValueDict, Return_List.copy())
                    print('pixel number', pixel_number)
                    print('center conflict point ', Return_List[2])

                    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                    # 先定义回退后的点为back_point
                    back_point = Return_List[3]
                    Segment[segment_number].insert((Point_Number + 1), back_point)
                    down_point = Return_List[3].copy()
                    down_point[2] += pixel_number

                    Segment[segment_number].insert((Point_Number + 2), down_point)
                    Point_Number += 2
                    # 更新起始点和终点
                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
                    remain_length = 0
                    print('\nAfter Processing \n Segment after:',Segment)
                    print('Pointer_Number:',Point_Number)
                    print('Start point:', Start_point)
                    print('Out of if;star loop again')

                elif flag==5:
                    # '''这里统一下降200'''
                    pixel_number = math.ceil(200/LenPixel)
                    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
                    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
                    # 先定义回退后的点为back_point
                    back_point = Return_List[3]
                    down_point = Return_List[3]
                    down_point[2] += pixel_number
                    Segment[segment_number].insert((Point_Number + 1), back_point)
                    Segment[segment_number].insert((Point_Number + 2), down_point)
                    Point_Number += 2
                    # 更新起始点和终点
                    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][
                        Point_Number + 1]
                    remain_length = 0
            #没有冲突
            else:
                print('\n\nin if 没有冲突')
                print('Segment:',Segment)

                Point_Number += 1

                # 如果是最后一个坐标,说明这条线段已经处理完了,开始进入下一个线段
                if Point_Number==(len(Segment[segment_number])-1):
                    print('进入到 没有冲突-》最后一个坐标，已经处理完毕，进入下一个阶段')
                    segment_number += 1
                    break
                else:
                    print('没有进入到if')

                    Start_point,Final_point=Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]

                print('Out of this if\n\n')
    return  Segment


'''
name: Compare
msg: #在put_MVACFlow中调用
#return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]
#返回冲突类型标志，冲突值，冲突点，冲突的中心点，需要回退的点
param {mvacflow, 单条风管
    Point_Number, 线段序号
    StructWorkArea3D_With_GraFlow_Temp, 整体空间
    start_point, 起始点
    final_point, 终点
    ValueList  不懂} 
return {flag,  冲突标志
 [Value_Conflict, 冲突点的值
 Conflict_Point,  冲突点
 CenterOfConflictPipe, 冲突点所在切面的中心点
 CenterOfConflictPipe_GoBack 回退(半个管道宽度加安装空间)后的中心点]} 
'''
def Compare(mvacflow, Point_Number, StructWorkArea3D_With_GraFlow_Temp, start_point, final_point, ValueList):
    #不懂这一段作用
    StructWorkArea3D_With_GraFlow = StructWorkArea3D_With_GraFlow_Temp.copy()
    for Value in ValueList:
        StructWorkArea3D_With_GraFlow[StructWorkArea3D_With_GraFlow==Value]=255
    #
    SpacePixelLen = mvacflow['SpacePixelLen']
    HalfNewSizePixelLen = np.ceil( mvacflow['NewSizePixelLen'][Point_Number][0]/2 ).astype(int)

    x_s,x_e,y_s,y_e,z_s,z_e = Get_SearchArea_coordinate(start_point, final_point, HalfNewSizePixelLen)

    SearchArea = StructWorkArea3D_With_GraFlow[ x_s:x_e, y_s:y_e, z_s:z_e ].copy()

    Coordinate = np.argwhere(SearchArea!=255).tolist()

    Coordinate = sorted(sorted(sorted(Coordinate, key = lambda x: x[0]), key = lambda x: x[2], reverse=True), key = lambda x: x[1])

    if len(Coordinate)==0:  #没有冲突
                print('test:无冲突')
                return False, []
    else:#有冲突
            
        #第一个冲突点各个坐标
        Conflict_X = x_s +  Coordinate[0][0] 
        Conflict_Y = y_s +  Coordinate[0][1]
        Conflict_Z = z_s +  Coordinate[0][2]
        Conflict_Point = np.array([ Conflict_X, Conflict_Y, Conflict_Z ] )


        Value_Conflict = StructWorkArea3D_With_GraFlow[Conflict_X, Conflict_Y, Conflict_Z]
        Value_Conflict_mod = Value_Conflict % 1000

        if start_point[0]==final_point[0] :
            CenterOfConflictPipe = np.array([Conflict_X, start_point[1], start_point[2]])
        elif start_point[1]==final_point[1]:
            CenterOfConflictPipe = np.array([start_point[0], Conflict_Y, start_point[2]])
        else:
            raise Exception('/n/nIn 管道不是平行于轴的/n/n')

        CenterOfConflictPipe_GoBack = np.array([start_point[0], Conflict_Y - HalfNewSizePixelLen - SpacePixelLen, start_point[2]])

        if Value_Conflict_mod==127: #撞梁
            flag = 2
            print('CenterOfConflictPipe',CenterOfConflictPipe)
            print('HalfNewSizePixelLen',HalfNewSizePixelLen)
            print('SpacePixelLen',SpacePixelLen)
            print('CenterOfConflictPipe_GoBack',CenterOfConflictPipe_GoBack)
            print('\nOut of Test in Compare()')
            return flag, [ Value_Conflict, Conflict_Point, CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

        elif Value_Conflict_mod==71 or Value_Conflict_mod==200:#平行撞管
            if start_point[0]==final_point[0] :
                flag = 3
                print('\ntest,平行撞管 Out of Test in Compare()')
            elif start_point[1]==final_point[1]:
                flag = 4
                print('\ntest, 交叉撞管 Out of Test in Compare()')
            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

        elif Value_Conflict_mod==72 or Value_Conflict_mod==201:#交叉撞管
            if start_point[0]==final_point[0] :
                flag = 4
                print('\ntest, 交叉撞管 Out of Test in Compare()')
            elif start_point[1]==final_point[1]:
                flag = 3
                print('\ntest,平行撞管 Out of Test in Compare()')
            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

        elif Value_Conflict_mod==73 or Value_Conflict_mod==202:#撞垂直管
            flag = 5
            print('\ntest 撞垂直管 Out of Test in Compare()')
            return flag, [Value_Conflict, Conflict_Point,  CenterOfConflictPipe, CenterOfConflictPipe_GoBack ]

        elif Value_Conflict == 0:
            raise Exception('/n/nIn Compare Value_Conflict == 0，撞结构？应该是find_room或靠墙出现了问题/n/n')
        print('\n')


'''
name: Get_SearchArea_coordinate
msg: #在Compare中调用
    返回6个坐标值，组合可得到用于检测是否有空间的管道某一线段(一个长方体)的8个顶点坐标
param {start_point, final_point, HalfNewSizePixelLen} 
return {x_s,x_e,y_s,y_e,z_s,z_e} 
'''
def Get_SearchArea_coordinate(start_point, final_point, HalfNewSizePixelLen):
    FlagDirection = 'X_EqValue' if start_point[0]==final_point[0] else 'Y_EqValue'

    if FlagDirection == 'X_EqValue':
        Flag = 'LowToHigh' if start_point[1]<final_point[1] else 'HighToLow'
        if Flag == 'LowToHigh' :           
            y_s = start_point[1]
            y_e = final_point[1] + 1
        else:
            y_s = final_point[1]
            y_e = start_point[1] + 1
        x_s = start_point[0] - HalfNewSizePixelLen
        x_e = start_point[0] + HalfNewSizePixelLen
    else:  #y值相等
        Flag = 'LowToHigh' if start_point[0]<final_point[0] else 'HighToLow'
        if Flag == 'LowToHigh':            
            x_s = start_point[0]
            x_e = final_point[0] + 1
        else:
            x_s = final_point[0]
            x_e = start_point[0] + 1
        y_s = start_point[0] - HalfNewSizePixelLen
        y_e = start_point[0] + HalfNewSizePixelLen
    z_s = start_point[2] - HalfNewSizePixelLen
    z_e = start_point[2] + HalfNewSizePixelLen

    return x_s,x_e,y_s,y_e,z_s,z_e


'''
name: Find_Room_MVACFlow
msg: #将管道某一线段靠墙排布，更改线段的新坐标
param {Point_Number, 线段序号，表示这是管道的第几个线段
    down_length, 如果管道需要下降，下降的距离
    segment_number, 线段序号，表示这是管道的第几个线段
    Start_point,Final_point,  检测的起点终点
    Segment, 线段集合
    StructWorkArea3D_With_GraFlow_MVAC, 
    mvacflow, 单条风管
    Return_List, 内容为flag,  冲突标志
                        [Value_Conflict, 冲突点的值
                        Conflict_Point,  冲突点
                        CenterOfConflictPipe, 冲突点所在切面的中心点
                        CenterOfConflictPipe_GoBack 回退(半个管道宽度加安装空间)后的中心点]
    FlagCrossBeam_segment 穿墙标志集合} 
return {Segment,segment_number,Point_Number,
    Start_point,Final_point 新的检测起点终点} 
'''
def Find_Room_MVACFlow(Point_Number,down_length,segment_number,Start_point,Final_point,Segment, StructWorkArea3D_With_GraFlow_MVAC, mvacflow, Return_List,FlagCrossBeam_segment):
    print('\n Test in Find_Room_MVACFlow')
    #如果这个线段之前没有穿梁
    if len(FlagCrossBeam_segment)==0:       
        print('这个线段之前没有穿梁')
        #判断这个线段的方向
        Direction_Flat=Direction_Segment(Start_point, Final_point)
        #len 是空间的长度，down是起始点，top是终点
        LEN,down,top = calculate_corridor_topdown(Start_point, Final_point, StructWorkArea3D_With_GraFlow_MVAC)
        #当前线段是沿着Y轴方向
        if Direction_Flat:
            print('Y方向')
            #先判断当前线段是不是最后一个线段,如果不是最后一个线段
            if segment_number<len(Segment)-1:
                #判断下一个线段是沿着X轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
                if Segment[segment_number+1][0][0]<Segment[segment_number+1][1][0]:
                    Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromLtoS(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 0, Return_List, StructWorkArea3D_With_GraFlow_MVAC)

                #判断下一个线段是沿着X轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
                else:
                    Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromStoL(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 0, Return_List, StructWorkArea3D_With_GraFlow_MVAC)
                    
                return Segment,segment_number,Point_Number,Start_point,Final_point    
            #如果是最后一个线段
            else:
                print('是最后一段')
                #当前线段沿着Y轴由小到大,靠墙就需要往X的负方向靠
                if Segment[segment_number][0][1]<Segment[segment_number][1][1]: 
                    Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromStoL(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 0, Return_List, StructWorkArea3D_With_GraFlow_MVAC)

                #当前线段沿着Y轴由大到小,靠墙就需要往X的正方向靠
                else:
                    Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromLtoS(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 0, Return_List, StructWorkArea3D_With_GraFlow_MVAC)
                return Segment,segment_number,Point_Number,Start_point,Final_point     
        # 当前线段是沿着x轴方向
        else:
            # 先判断当前线段是不是最后一个线段,如果不是最后一个线段
            if segment_number < len(Segment) - 1:
                # 判断下一个线段是沿着Y轴从小到大,也就是当前选段需要从走廊top到down去寻找可行空间
                if Segment[segment_number + 1][0][1] < Segment[segment_number + 1][-1][1]:
                    Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromLtoS(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 1, Return_List, StructWorkArea3D_With_GraFlow_MVAC)
                #判断下一个线段是沿着Y轴从大到小,也就是当前选段需要从走廊down到top去寻找可行空间
                else:
                    Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromStoL(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 1, Return_List, StructWorkArea3D_With_GraFlow_MVAC)
                return Segment,segment_number,Point_Number,Start_point,Final_point
            # 如果是最后一个线段
            else:
                # 当前线段沿着X轴由小到大,靠墙就需要往Y的负方向靠
                if Segment[segment_number][0][0] < Segment[segment_number][1][0]:
                     Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromStoL(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 1, Return_List, StructWorkArea3D_With_GraFlow_MVAC)   

                # 当前线段沿着X轴由大到小,靠墙就需要往Y的正方向靠
                else:
                    Segment,segment_number,Point_Number,Start_point,Final_point = FindSegmentFromLtoS(Point_Number, 
                    segment_number,down_length, top, down, Segment, mvacflow, 1, Return_List, StructWorkArea3D_With_GraFlow_MVAC)
                return Segment,segment_number,Point_Number,Start_point,Final_point
    #如果这个线段之前穿梁了,那么就只能下降
    else:
        Segment,segment_number,Point_Number, Start_point, Final_point = Make_Flow_Down(down_length,Return_List[3],Segment,Point_Number,segment_number)
        return Segment,segment_number,Point_Number,Start_point,Final_point

'''
name: Change_leftover_flow_Newsize
msg: #修改这条管道后面线段的NewSizePixelLen，和当前线段一致
param {Point_Number,mvacflow,flow_newsize} 
return { } 
'''
def Change_leftover_flow_Newsize(Point_Number,mvacflow,flow_newsize):
    
    for index in range(Point_Number,len(mvacflow['Route'])-1):
        mvacflow['NewSizePixelLen'][index] = flow_newsize

'''
name: FindSegmentFromLtoS
msg: #在Find_Room_MVACFlow中调用
    以垂直于走廊的方向做竖直切面，在这个切面中从数值大的一端开始靠墙排布管道线段，修改segment坐标。
    param {Point_Number, 线段序号，表示这是管道的第几个线段
    segment_number, 线段序号，表示这是管道的第几个线段
    down_length, 如果管道需要下降，下降的距离
    top, down, 
    Segment, 管道线段集合
    mvacflow, 风管
    direction, 方向，值为0时代表沿走廊y轴，为1时代表走廊沿x轴
    StructWorkArea3D_With_GraFlow_MVAC} 
return {Segment,segment_number,Point_Number,Start_point,Final_point} 
'''
def FindSegmentFromLtoS(Point_Number, segment_number,down_length, top, down, Segment, mvacflow, direction, Return_List, StructWorkArea3D_With_GraFlow_MVAC):    
    # 把矩阵中down到top之间的矩阵块取出来,这个矩阵块可能不在第一层,detact_zoom 2维矩阵，第一维是x/y，第二维是z
    
    while 1:        
        print('down,top:', down, top)
        if direction == 0:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0]:top[0], down[1], down[2]:]
        else:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0], down[1]:top[1], down[2]:] 

        original_flow_newsize = mvacflow['NewSizePixelLen'][Point_Number].copy()
        detact_zoom_copy = detact_zoom.copy()
        
        zoomshape = np.shape(detact_zoom)
        flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]
        Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
        Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2

        if 255 in detact_zoom and zoomshape[0]>=Mvacflow_wedth_pixel: #走廊比管道宽
            deform_flag = 0
            horizon_deform_flag = 0
            while 1: 
                flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]
                # 因为管线两边都需要安装空间,所以space剩以2
                Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
                Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2
                          
                Start_Index_Hor,Start_Index_Ver = Get_Start_Index(detact_zoom_copy,21)

                if Start_Index_Hor - Mvacflow_wedth_pixel>=0:#可行空间大于宽度
                    if detact_zoom[Start_Index_Hor - Mvacflow_wedth_pixel:Start_Index_Hor,Start_Index_Ver:Start_Index_Ver + Mvacflow_depth_pixel].sum() == 255*Mvacflow_wedth_pixel*Mvacflow_depth_pixel:              
                        New_val = down[direction] + (Start_Index_Hor - math.ceil(Mvacflow_wedth_pixel / 2))
                        #修改当前线段的所有x/y值
                        for index in range(len(Segment[segment_number])):
                            Segment[segment_number][index][direction] = New_val

                        #修改后面线段的NewSizePixelLen，和当前线段一致
                        Change_leftover_flow_Newsize(Point_Number,mvacflow,flow_newsize)
                        #如果这个线段是管线的第一个线段
                        if segment_number ==0:
                            Point_Number = 0
                            Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                        else: # 根据当前线段的起始点改变上一个线段的终点,也就是把当前线段的起始点加到上一个线段的末尾
                            Segment[segment_number - 1].append(Segment[segment_number][0])
                            segment_number -= 1
                            #从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                            Point_Number = len(Segment[segment_number]) - 2
                            # 更新起始点和终点为上一个线段延长部分的头尾两点
                            Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number + 1]
                        return Segment,segment_number,Point_Number,Start_point,Final_point
                    else: #放不下
                        if deform_flag == 0:
                            detact_zoom_copy=detact_zoom_copy[0:Start_Index_Hor,:] #矩阵x-1
                        else:
                            if horizon_deform_flag == 0: #处于缩小宽度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,0):
                                    pass #改变宽度进入下一次检测                                   
                                else: #不能再缩小宽度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                            else:  #处于缩小高度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,1):
                                    pass
                                    #改变高度进入下一次检测
                                else: #不能再缩小高度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 0 #结束缩小高度循环
                                    detact_zoom_copy=detact_zoom_copy[0:Start_Index_Hor,:] #矩阵x-1
                else:#可行空间x小于管道宽度
                    if horizon_deform_flag == 0: #处于缩小宽度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,0):
                            pass  #改变宽度进入下一次检测
                        else: #不能再缩小宽度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                    else:  #处于缩小高度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,1):
                            pass  #改变高度进入下一次检测
                        else: #不能再缩小高度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            Segment, segment_number, Point_Number, Start_point, Final_point = Make_Flow_Down(down_length,Return_List[3],Segment,Point_Number,segment_number)
                            return Segment,segment_number,Point_Number,Start_point,Final_point


        else: 
            raise Exception('所有层都没有空位或者空间宽度小于管道宽度')   


#在Find_Room_MVACFlow中调用
'''
name: FindSegmentFromStoL
msg: #在Find_Room_MVACFlow中调用
    以垂直于走廊的方向做竖直切面，在这个切面中从数值小的一端开始靠墙排布管道线段，修改segment坐标。
    param {Point_Number, 线段序号，表示这是管道的第几个线段
    segment_number, 线段序号，表示这是管道的第几个线段
    down_length, 如果管道需要下降，下降的距离
    top, down, 
    Segment, 管道线段集合
    mvacflow, 风管
    direction, 方向，值为0时代表沿走廊y轴，为1时代表走廊沿x轴
    StructWorkArea3D_With_GraFlow_MVAC} 
return {Segment,segment_number,Point_Number,Start_point,Final_point} 
'''
def FindSegmentFromStoL(Point_Number, segment_number,down_length, top, down, Segment, mvacflow, direction, Return_List, StructWorkArea3D_With_GraFlow_MVAC): 


    while 1:

        if direction == 0:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0]:top[0], down[1], down[2]:]
        else:
            detact_zoom = StructWorkArea3D_With_GraFlow_MVAC[down[0], down[1]:top[1], down[2]:]    

        print('down,top:', down, top)
        original_flow_newsize = mvacflow['NewSizePixelLen'][Point_Number].copy()         
        detact_zoom_copy = detact_zoom.copy()
        
        zoomshape = np.shape(detact_zoom)
        flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]
        Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
        Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2

        if 255 in detact_zoom and zoomshape[0]>=Mvacflow_wedth_pixel:
            deform_flag = 0
            horizon_deform_flag = 0
            while 1:
                # 更新修改过长宽的管道所需要的总宽度和总深(高)度
                flow_newsize = mvacflow['NewSizePixelLen'][Point_Number]                
                Mvacflow_wedth_pixel = flow_newsize[0] + mvacflow['SpacePixelLen'] * 2
                Mvacflow_depth_pixel = flow_newsize[1] + mvacflow['SpacePixelLen'] * 2
                
                Start_Index_Hor,Start_Index_Ver = Get_Start_Index(detact_zoom_copy,12)

                if Start_Index_Hor + Mvacflow_wedth_pixel < zoomshape[0]:
                    if detact_zoom[Start_Index_Hor:Start_Index_Hor + Mvacflow_wedth_pixel,Start_Index_Ver: Start_Index_Ver +Mvacflow_depth_pixel].sum() == 255*Mvacflow_wedth_pixel*Mvacflow_depth_pixel:
                        #线段沿y轴时输入的direction为0，需要更改的是x，所以用mvacflow['Route'][Point_Number][direction]表示 
                        New_val = top[direction] - (zoomshape[0] - (Start_Index_Hor + math.ceil(Mvacflow_wedth_pixel/2)) ) 
                        for index in range(len(Segment[segment_number])):
                            Segment[segment_number][index][direction] = New_val

                        #修改后面线段的NewSizePixelLen，和当前线段一致
                        Change_leftover_flow_Newsize(Point_Number,mvacflow,flow_newsize)
                        # 如果这个线段是管线的第一个线段
                        if segment_number == 0:
                            Point_Number = 0
                            Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number+1]
                        else:  # 根据当前线段的起始点改变上一个线段的终点
                            Segment[segment_number - 1].append(Segment[segment_number][0])
                            segment_number -= 1
                            #从上一个线段的倒数第二个点开始走起,也就是延长了的部分要重新检测一遍
                            Point_Number = len(Segment[segment_number]) - 2
                            # 更新起始点和终点为上一个线段延长部分的头尾两点
                            Start_point, Final_point = Segment[segment_number][Point_Number],Segment[segment_number][Point_Number + 1]
                        return Segment,segment_number,Point_Number,Start_point,Final_point
                    else: #放不下
                        if deform_flag == 0:
                            detact_zoom_copy=detact_zoom_copy[Start_Index_Hor + 1:,:] #矩阵x-1
                        else:
                            if horizon_deform_flag == 0: #处于缩小宽度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,0):
                                    pass
                                    #改变宽度进入下一次检测
                                else: #不能再缩小宽度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                            else:  #处于缩小高度循环中
                                if modify_mvacflow_size(mvacflow,Point_Number,1):
                                    pass
                                    #改变高度进入下一次检测
                                else: #不能再缩小高度
                                    mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                                    horizon_deform_flag = 0 #结束缩小高度循环
                                    detact_zoom_copy=detact_zoom_copy[Start_Index_Hor + 1:,:] #矩阵x-1
                else:#可行空间x小于管道宽度
                    if horizon_deform_flag == 0: #处于缩小宽度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,0):
                            pass  #改变宽度进入下一次检测
                        else: #不能再缩小宽度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            horizon_deform_flag = 1 #结束缩小宽度循环，进入缩小高度循环
                    else:  #处于缩小高度循环中
                        if modify_mvacflow_size(mvacflow,Point_Number,1):
                            pass  #改变高度进入下一次检测
                        else: #不能再缩小高度
                            mvacflow['NewSizePixelLen'][Point_Number] = original_flow_newsize.copy()
                            Segment, segment_number, Point_Number, Start_point, Final_point = Make_Flow_Down(down_length,Return_List[3],Segment,Point_Number,segment_number)
                            return Segment,segment_number,Point_Number,Start_point,Final_point

        else: 
            raise Exception('所有层都没有空位或者空间宽度小于管道宽度')  


'''
name: Make_Flow_Down
msg: #在FindSegmentFromStoL，LtoS中调用
    如果管道需要下降，下降从这个线段开始后面所有的线段，下一版需改善
param {pixel_number,Conflict_GoBack_Point,Segment,Point_Number,segment_number} 
return {Segment, segment_number, Point_Number, Start_point, Final_point} 
'''
def Make_Flow_Down(pixel_number,Conflict_GoBack_Point,Segment,Point_Number,segment_number):
    Down_Point = np.array(Conflict_GoBack_Point) + np.array([0, 0, pixel_number])

    print('in else: #这一层走廊没有空间可以容纳得下这条线段,在冲突点制造下降')
    # 把当前Start_point开始管线后面所有z轴坐标统一减少pixel_number,输入segment为当前线段,输入Segment为线段坐标集合
    '''函数参数列表加多了Point_Number OK'''
    Segment = Reduce_Z(Point_Number, Segment, segment_number, pixel_number)
    # 在管线中加入冲突点(也就是下降点)
    Segment[segment_number].insert((Point_Number + 1), Conflict_GoBack_Point)

    Segment[segment_number].insert((Point_Number + 2), Down_Point)

    Point_Number += 2
    # 更新起始点和终点
    Start_point, Final_point = Segment[segment_number][Point_Number], Segment[segment_number][Point_Number + 1]
    return  Segment, segment_number, Point_Number, Start_point, Final_point


    
'''
name: Find_point
msg: #在put_MVACFlow函数里调用
    #风管的findPoint，如果线段需要下降，返回需要下降的距离
param {Graflow, MVACflow, thisflow,  StructWorkArea3D_With_GraFlow,  PipesValueDict, Return_List} 
return {np.ceil(pixel_number_cross).astype(int)} 
'''
def Find_point(Graflow, MVACflow, thisflow,  StructWorkArea3D_With_GraFlow,  PipesValueDict, Return_List):
    ConflictValue, conflict_point, CenterOfConflictPoint, NoUsePoint = Return_List
    print('\nEnter in find point()')
    print('ConflictValue',ConflictValue)
    print('CenterOfConflictPoint',CenterOfConflictPoint)

    graFlowflag = [61,62,63,100,101,102]
    mvacFlowflag = [71,72,73,200,201,202]

    if ConflictValue%1000 in graFlowflag:
        Exist_flow = Graflow[PipesValueDict[ConflictValue]] 
    elif ConflictValue%1000 in mvacFlowflag :
        Exist_flow = MVACflow[PipesValueDict[ConflictValue]]

    #找到冲突的已排布管线在现排布管线经过的空间的最低点Z
    Slide_For_Searching_Lowest_Z = StructWorkArea3D_With_GraFlow[conflict_point[0], conflict_point[1],  :].copy()
    Z_Lowest = np.argwhere(Slide_For_Searching_Lowest_Z==ConflictValue).max()
    print('np.argwhere(Slide_For_Searching_Lowest_Z==ConflictValue).max():',Z_Lowest)
    print('conflict_point[2]',conflict_point[2])
    print('Z_Lowest',Z_Lowest)

    if ConflictValue%1000==61 or ConflictValue%1000==62 or ConflictValue%1000==63:
        print('enter in Find_Point; if ConflictValue%1000==61 or ConflictValue%1000==62 or ConflictValue%1000==63:')
        print('Z_Lowest befor:', Z_Lowest)
        Z_Lowest += Exist_flow['SpacePixelLen']
        print('Z_Lowest after:',Z_Lowest)

    elif ConflictValue%1000==71 or ConflictValue%1000==72 or ConflictValue%1000==73:
        print('enter in Find_Point; if ConflictValue%1000==71 or ConflictValue%1000==72 or ConflictValue%1000==73:')
        print('Z_Lowest befor:', Z_Lowest)
        Z_Lowest += Exist_flow['SpacePixelLen']
        print('Z_Lowest after:',Z_Lowest)

    # 求需要下降的长度，共用了安装空间
    if ConflictValue%1000 in graFlowflag: #如果是水管        
        if thisflow['SpacePixelLen'] <= Exist_flow['SpacePixelLen']:
            pixel_number_cross = Z_Lowest - CenterOfConflictPoint[2] + 1 +  np.ceil(thisflow['NewSizePixelLen'][1]/2).astype(int)
        else:
            pixel_number_cross = Z_Lowest - CenterOfConflictPoint[2] + 1 + np.ceil(thisflow['NewSizePixelLen'][1]/2).astype(int) + thisflow['SpacePixelLen'] -Exist_flow['SpacePixelLen']
    elif ConflictValue%1000 in mvacFlowflag:
        if thisflow['SpacePixelLen'] <= Exist_flow['SpacePixelLen']:
            #无法知道当前冲突的是第几个线段，但因为风管当前线段的NewSizePixelLen和最后一个线段的NewSizePixelLen相同，所以采用最后一个线段的NewSizePixelLen
            pixel_number_cross = Z_Lowest - CenterOfConflictPoint[2] + 1 +  np.ceil(thisflow['NewSizePixelLen'][-1][1]/2).astype(int)
        else:
            pixel_number_cross = Z_Lowest - CenterOfConflictPoint[2] + 1 + np.ceil(thisflow['NewSizePixelLen'][-1][1]/2).astype(int) + thisflow['SpacePixelLen'] -Exist_flow['SpacePixelLen']
    print('pixel_number_cross：', pixel_number_cross)
    print('OUT Find_Point()\n')
    return np.ceil(pixel_number_cross).astype(int)


#### 画管####
'''
name: MVAC_put_output
msg: 根据线段给空间的点赋值
param {mvacflow, Point_number, StructWorkArea3D_With_GraFlow, StructWorkArea2D, segment, Z_Max, LenPixel} 
return {lowest_z, StructWorkArea3D_With_GraFlow} 
'''
def MVAC_put_output(mvacflow, Point_number, StructWorkArea3D_With_GraFlow, StructWorkArea2D, segment, Z_Max, LenPixel):
    print('\nTest in put_output():')
    print('小segment:', segment)

    FlagDirection = 'X_EqValue' if segment[0][0] == segment[-1][0] else 'Y_EqValue'

    if FlagDirection == 'X_EqValue':
        Flag = 'LowToHigh' if segment[0][1] < segment[-1][1] else 'HighToLow'

    else:
        Flag = 'LowToHigh' if segment[0][0] < segment[-1][0] else 'HighToLow'


    SpacePixelLen = mvacflow['SpacePixelLen']
    HalfNewWidthPixelLen = np.ceil(mvacflow['NewSizePixelLen'][Point_number][0] / 2).astype(int)
    HalfNewDepthPixelLen = np.ceil(mvacflow['NewSizePixelLen'][Point_number][1] / 2).astype(int)

    lowest_z = segment[-1][2] + HalfNewDepthPixelLen

    if lowest_z > Z_Max:
        print('穿假天花了')
        print('Segment[-1]:', segment[-1], '\n')
        '''
        增加StructWorkArea3D_With_GraFlow厚度，
        报告穿板
        '''
        StructWorkArea3D_Append = np.zeros(
            (StructWorkArea2D.shape[0], StructWorkArea2D.shape[1], lowest_z - Z_Max)) + StructWorkArea2D[:, :,
                                                                                        np.newaxis]
        StructWorkArea3D_With_GraFlow = np.append(StructWorkArea3D_With_GraFlow, StructWorkArea3D_Append, axis=2)


    # 分段, 画Space
    for i in range(len(segment) - 1):

        # 垂直下降段
        if segment[i][0] == segment[i + 1][0] and segment[i][1] == segment[i + 1][1]:

            StructWorkArea3D_With_GraFlow[
                     (segment[i][0] - HalfNewWidthPixelLen - SpacePixelLen): (segment[i][0] + HalfNewWidthPixelLen + SpacePixelLen),
                     (segment[i][1] - HalfNewWidthPixelLen - SpacePixelLen): (segment[i][1] + HalfNewWidthPixelLen + SpacePixelLen),
                                                             segment[i][2]: segment[i + 1][2] + 1 ] = mvacflow['Z_Eq_SpaceValue']

        else:  # 水平非垂直段

            # 分锯齿 ; 先整体填充Space，再在这个基础上填充管线NewSize;
            Space_Z_Strat = segment[i][2] - HalfNewDepthPixelLen - SpacePixelLen 
            Space_Z_End = segment[i][2] + HalfNewDepthPixelLen + SpacePixelLen 
            NewSize_Z_Start = segment[i][2] - HalfNewDepthPixelLen
            NewSize_Z_End = segment[i][2] + HalfNewDepthPixelLen

            if FlagDirection == "X_EqValue":

                if Flag == 'LowToHigh':  # Y从小到大

                    StructWorkArea3D_With_GraFlow[(segment[i][0] - HalfNewWidthPixelLen - SpacePixelLen):(
                    segment[i][0] + HalfNewWidthPixelLen + SpacePixelLen),
                    segment[i][1]: (segment[i + 1][1] + 1),
                    Space_Z_Strat: Space_Z_End
                    ] = mvacflow['X_Eq_SpaceValue']

                elif Flag == 'HighToLow':  # Y从大到小

                    StructWorkArea3D_With_GraFlow[(segment[i][0] - HalfNewWidthPixelLen - SpacePixelLen): (
                        segment[i][0] + HalfNewWidthPixelLen + SpacePixelLen),
                        segment[i + 1][1]: (segment[i][1] + 1),
                        Space_Z_Strat: (Space_Z_End)
                        ] = mvacflow['X_Eq_SpaceValue']

            elif FlagDirection == "Y_EqValue":

                if Flag == 'LowToHigh':
                    StructWorkArea3D_With_GraFlow[(segment[i][0] ): ( segment[i + 1][0] + 1),
                    (segment[i][1] - HalfNewWidthPixelLen - SpacePixelLen): (segment[i][1] + HalfNewWidthPixelLen + SpacePixelLen),
                    Space_Z_Strat: (Space_Z_End)
                    ] = mvacflow['Y_Eq_SpaceValue']

                elif Flag == 'HighToLow':

                    StructWorkArea3D_With_GraFlow[
                    ( segment[i + 1][0]): (segment[i][0] + 1),
                    (segment[i][1] - HalfNewWidthPixelLen - SpacePixelLen): (segment[i][1] + HalfNewWidthPixelLen + SpacePixelLen),
                    Space_Z_Strat: (Space_Z_End)
                    ] = mvacflow['Y_Eq_SpaceValue']

    #分段，画NewSize
    for i in range(len(segment) - 1):

        # 垂直下降段
        if segment[i][0] == segment[i + 1][0] and segment[i][1] == segment[i + 1][1]:
            StructWorkArea3D_With_GraFlow[
            (segment[i][0] - HalfNewWidthPixelLen): (segment[i][0] + HalfNewWidthPixelLen),
            (segment[i][1] - HalfNewWidthPixelLen): (segment[i][1] + HalfNewWidthPixelLen),
            segment[i][2]: segment[i + 1][2] + 1] = mvacflow['Z_EqValue']
        else:  # 水平非垂直段

            Space_Z_Strat = segment[i][2] - HalfNewDepthPixelLen - SpacePixelLen 
            Space_Z_End = segment[i][2] + HalfNewDepthPixelLen + SpacePixelLen 
            NewSize_Z_Start = segment[i][2] - HalfNewDepthPixelLen
            NewSize_Z_End = segment[i][2] + HalfNewDepthPixelLen

            if FlagDirection == "X_EqValue":

                if Flag == 'LowToHigh':  # Y从小到大
                    StructWorkArea3D_With_GraFlow[
                    (segment[i][0] - HalfNewWidthPixelLen): (segment[i][0] + HalfNewWidthPixelLen),
                    (segment[i][1] ): (segment[i + 1][1] + 1),
                    NewSize_Z_Start: (NewSize_Z_End)
                    ] = mvacflow['X_EqValue']

                elif Flag == 'HighToLow':  # Y从大到小

                    StructWorkArea3D_With_GraFlow[
                    (segment[i][0] - HalfNewWidthPixelLen): (segment[i][0] + HalfNewWidthPixelLen),
                    (segment[i + 1][1]): (segment[i][1] + 1),
                    NewSize_Z_Start: (NewSize_Z_End)
                    ] = mvacflow['X_EqValue']

            elif FlagDirection == "Y_EqValue":

                if Flag == 'LowToHigh':

                    StructWorkArea3D_With_GraFlow[
                    (segment[i][0] ): (segment[i + 1][0] + 1),
                    (segment[i][1] - HalfNewWidthPixelLen): (segment[i][1] + HalfNewWidthPixelLen),
                    NewSize_Z_Start: (NewSize_Z_End)
                    ] = mvacflow['Y_EqValue']

                elif Flag == 'HighToLow':

                    StructWorkArea3D_With_GraFlow[
                    (segment[i + 1][0]): (segment[i][0] + 1),
                    (segment[i][1] - HalfNewWidthPixelLen): (segment[i][1] + HalfNewWidthPixelLen),
                    NewSize_Z_Start: (NewSize_Z_End)
                    ] = mvacflow['Y_EqValue']



    print('Test Out from put——output()\n\n')
    return lowest_z, StructWorkArea3D_With_GraFlow


###################恢复管道实际坐标##########################
'''
name: ReturnToRealCoord
msg: 将管道坐标恢复回实际的值。将route重新变回一维列表RealFlowRoute
param Segment,LenPixel 
return RealSegment,RealFlowRoute
使用实例：
Segment = [[[10,0,5],[12,0,5],[12,0,10],[14,0,10],[14,0,5],[16,0,5]],[[16,0,5],[16,10,5]],[[16,10,5],[20,10,5]]]
RealFlowRoute = []
RealSegment = []
RealSegment,RealFlowRoute = ReturnToRealCoord(Segment,10)
print('RealFlowRoute',RealFlowRoute)
'''
def ReturnToRealCoord(Segment,LenPixel):
    RealSegment = Segment.copy()
    RealFlowRoute = []
    for segment in RealSegment:
        for coord in segment:
            coord[0] *= LenPixel
            coord[1] *= LenPixel
            coord[2] *= LenPixel
            RealFlowRoute.append([coord[0],coord[1],coord[2]])
    return RealSegment,RealFlowRoute


##################以下为用到的其他师兄编写的函数，为了方便直接复制过来，不需要再import##################
#计算走廊空间
'''
name: calculate_corridor_topdown
msg: 根据管道线段起点终点和所在走廊空间，返回走廊的宽度，和走廊两边的端点
param {Start_point,Final_point,StructWorkArea3D_With_GraFlow} 
return {LEN,down,top} 
'''
def calculate_corridor_topdown(Start_point,Final_point,StructWorkArea3D_With_GraFlow):
    Start_point = np.array(Start_point)
    Final_point = np.array(Final_point)
    print('==================================In  calculate_corridor_topdown========================')

    # Tmp_Start_Point_array要来存放线段中点,四分之一点,四分之三点
    Tmp_Start_Point_array = []
    # 分别当前线段的中点,四分之一点，四分之三,垂直于当前线段沿y轴向上作一条长度为走廊宽度的线段(不取首、终点，因为图像边缘有些锯齿什么的，导致不准）
    Tmp_Start_Point_array.append((Start_point + Final_point) / 2)
    Tmp_Start_Point_array.append((Tmp_Start_Point_array[0] + Start_point) / 2)
    Tmp_Start_Point_array.append((Tmp_Start_Point_array[0] + Final_point) / 2)
    Tmp_Start_Point_array = np.array(Tmp_Start_Point_array).astype(int)
    print('Point_List in calculate_corridor_topdown: ')
    print(Tmp_Start_Point_array)
    '''使用少武的函数'''
    LEN,down,top=calculate_corridor_topdown_chen(StructWorkArea3D_With_GraFlow, Tmp_Start_Point_array)
    print('\n top in calculate_corridor_topdown():',top)
    print('\n down in calculate_corridor_topdown():',down)
    print('=================out from calculate_corridor_topdown========================')

    return LEN,down,top

'''
内部函数，不需要外部调用
'''
def calculate_corridor_topdown_chen(StructWorkArea3D_With_GraFlow, PointList):

    print('\nTest in calculate_corridor_topdown_chen():')
    #PointList为取得走廊上5点,[起点， 中间点1， 中间点2， 中间点3，终点]
    PointList = np.array(PointList).astype(int)
    StartPoint = PointList[0]
    EndPoint = PointList[-1]

    #Direction指管线段方向
    if StartPoint[0]==EndPoint[0]:
      Direction='X_Eq'

    elif StartPoint[1]==EndPoint[1]:
      Direction='Y_Eq'
    else:
      raise Exception('Error in calculate_corridor_topdown_chen()') 

    LEN = 9999999999
    i = 0
    for i in range(len(PointList)):
        Point = PointList[i]
        Len, A_Pair_Of_Point = calculate_corridor_with_one_point_chen(Point, StructWorkArea3D_With_GraFlow, Direction )
        print('%d, Len, A_Pair_Of_Point:'%(i+1), Len, A_Pair_Of_Point)
        if Len==False:
            pass
        else:

            if Len<LEN:
                LEN = Len 
                down = np.array(A_Pair_Of_Point[0]).astype(int)
                top = np.array(A_Pair_Of_Point[1]).astype(int)
    if LEN==9999999999:
        raise Exception('没有找到top  down')
    else:
        print('down',down)
        print('top',top)
        print('out from calculate_corridor_topdown_chen\n')

    return Len, down, top
'''
内部函数，不需要外部调用
'''
def calculate_corridor_with_one_point_chen(Point, StructWorkArea3D, Direction ):

    if Direction=='Y_Eq':
        Coordinate = np.argwhere( StructWorkArea3D[ int(Point[0]), :, Point[2]]==0 ).squeeze()

        if Coordinate.size <2:
            return False,[]
        else:
            #做差值，找走廊的两端点1
            Coordinate2 =  abs(Coordinate - Point[1] )         
            point1_Y = Coordinate[Coordinate2.argmin()]

            #做差值，找走廊的两端点2
            if point1_Y+1 in Coordinate:
                Coordinate3 = np.array([x for x in Coordinate if x<point1_Y ])
            else:
                Coordinate3 = np.array([x for x in Coordinate if x>point1_Y ])
            Coordinate4 = abs(Coordinate3 - Point[1])

            if Coordinate4.shape[0]==0:
                return False,[]
            else:
                point2_Y = Coordinate3[Coordinate4.argmin()]
       
                point1 = np.array([ Point[0], point1_Y, Point[2]])
                point2 = np.array([ Point[0], point2_Y, Point[2]])

                LEN =  abs(point1[1] - point2[1]) +1

                if point1_Y<point2_Y: 
                    return LEN, [point1, point2]
                else: 
                    return LEN, [point2, point1]


    elif Direction=='X_Eq':

 
        #取一整条线
        Coordinate = np.argwhere( StructWorkArea3D[ :, int(Point[1]), Point[2]]==0 ).squeeze()


        if Coordinate.size <2:

            return False,[]
        else:
            #做差值，找走廊的两端点1
            Coordinate2 =  abs(Coordinate - Point[0] )         
            point1_X = Coordinate[Coordinate2.argmin()]

            #做差值，找走廊的两端点2
            if point1_X+1 in Coordinate:
                Coordinate3 = np.array([x for x in Coordinate if x<point1_X ])
            else:
                Coordinate3 = np.array([x for x in Coordinate if x>point1_X ])
            Coordinate4 = abs(Coordinate3 - Point[0])

            if Coordinate4.shape[0]==0:

                return False,[]
            else:
                point2_X = Coordinate3[Coordinate4.argmin()]
           
                point1 = np.array([ point1_X, Point[1],  Point[2]])
                point2 = np.array([ point2_X, Point[1],  Point[2]])

                LEN =  abs(point2[0] - point1[0]) +1

                if point1_X<point2_X: 
                    return LEN, [point1, point2]
                else: 
                    return LEN, [point2, point1]

'''
name: up_graflow
msg: 把管道集合里所有管道route的所有z值调到最高(0)
param {GraFlow} 
return {GraFlow} 
'''
def up_graflow(GraFlow):
    for graflow in GraFlow:
        for index in range(len(graflow['Route'])):
            graflow['Route'][index][2]=0
    return GraFlow

'''
name: Create_Segment
msg: 创造以管道route为元素的segment列表。 segment = {((x1,y1),(x2,y2)),((x2,y2),(x3,y3)),...}
param {graflow} 
return {Segment} 
'''
def Create_Segment(graflow):
    Segment=[]
    for i in range(len(graflow['Route'])-1):
        Segment.append([graflow['Route'][i],graflow['Route'][i+1]])
    return Segment


'''
name: Direction_Segment
msg: # 输入线段的群起始点和终点,确定这条线段是跟x轴平行就返回False，跟y轴平行就返回True
param {Start_Point,Final_Point} 
return {bool} 
'''
def Direction_Segment(Start_Point,Final_Point):
    #首尾的坐标x的差,和坐标y的差
    diff_X = Start_Point[0] - Final_Point[0]
    diff_Y = Start_Point[1] - Final_Point[1]
    #线段是跟y轴平行
    if abs(diff_X) < abs(diff_Y):
        return True
    else:
        return False

def Reduce_Z(Point_Number,Segment,segment_number,pixel_number):
    #输出Segment=[[[x1,y1],[x2,y2]],[[x2-pixel_number,y2-pixel_number],[x3-pixel_number,y3-pixel_number]]...]
    for index_segment in range(Point_Number+1,len(Segment[segment_number])):
        Segment[segment_number][index_segment][2]+=pixel_number

    for i in range(segment_number+1,len(Segment)):
        for j in range(len(Segment[i])):
            Segment[i][j][2]+=pixel_number

    return Segment

def Calculate_MVACNewSize(flow, Point_Number):

    return graflow['NewSize'][Point_Number][0]

def Calculate_GraNewSize(flow, Point_Number):
    return graflow['NewSize'][0]
# 判断当前起始点到终点穿梁的位置是否刚好满足要求,是的话返回flag_across=true,反之返回flag_across=false

def Check_Right(Start_point,Final_point, mvacflow, Point_Number, Return_List, LenPixel, \
             Beams, BeamsValueDict, StructWorkArea3D_With_Gra_MVAC,):
    #撞梁截面处管线的含包裹最高点Z、最低点Z
    HalfHighPixel =  np.ceil(mvacflow['NewSizePixelLen'][Point_Number][1] / 2).astype(int)
    HalfWedthPixel =  np.ceil(mvacflow['NewSizePixelLen'][Point_Number][0] / 2).astype(int)
    Pipe_Z_Highest = CenterOfConflictPipe[2] - HalfHighPixel #注意 最高点的Z轴是0，越低Z值反而越大
    Pipe_Z_Lowest = CenterOfConflictPipe[2] + HalfHighPixel
    
    BeamValue = Return_List[0]
    CenterOfConflictPipe = Return_List[2]
    Beam = Beams[BeamsValueDict[BeamValue]]
    
    if Beam['Route'][0][0] == Beam['Route'][1][0]:  
        Flag_Beam = 'X_Eq'
        ValueOfPipe = 72  #梁平行于Y轴，那么与之垂直的管必是平行于X轴,MVAC['Y_EqValue'] = 72 + i*1000
        ValueOfSpace = 201
