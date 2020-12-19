import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
# #test1
# StructWorkArea2D = [[2,2,2],[3,3,3],[4,4,4],[5,5,5]]
# a = np.zeros([4, 3, 5])
# b = np.array(StructWorkArea2D)
# b = b[:,:,np.newaxis]
# WorkArea = a + b
# print(WorkArea)
# #点坐标表示
# #括号从左到右表示列表内从大到小的[]
# print(WorkArea[0][1][2],WorkArea[1][1][3])
# #左开右闭
# temparea = WorkArea[:,0,:]
# print('temparea is')
# print(temparea)
# #len返回最外维的长度,shape返回各维度长度
# print(len(temparea))
# print(np.shape(temparea))

# Start_Index = (np.argwhere(temparea == 4))
# print(Start_Index[0][0])

# WorkArea[1:2,1:2,:] = 10
# test_list = WorkArea[1:2,1:2,:]
# print(' now WorkArea is')
# print(WorkArea)
# print(' now test_list is')
# print(test_list)

# StructWorkArea2D = [[0,0,1],[1,1,1],[1,1,1]]
# temparea = np.array(StructWorkArea2D)
# temparea = temparea.T 
# Start_Index = (np.argwhere(temparea == 1))
# print(Start_Index)
# a =  Start_Index[np.lexsort(Start_Index.T)]
aaa = [[0,1],[2,1],[4,1],[3,6],[4,8]]
z_min = np.min(aaa,axis=0)[1]
#print(z_min)
len = len(aaa)
for i in range(len):
    if aaa[i][1]>z_min:
        print(aaa[i-1][0])
        break

#test2
# a = [1,1]
# a = [a] * 1
# print(a[0][0])

#test3
# def flow_Newsize_Expansion (flow):
#     tempsize = flow['NewSize'] 
#     number = len(flow['Route']) - 1
#     flow['NewSize'] = [tempsize] * number
#     print("newsize is ",flow['NewSize'])

# flow = {'Route': [[410, 0, None],[410, 420, None],[0, 420, None]],
#         'Type': '12031',
#         'NewSize': [100,50]}  

# lens = len(flow['Route'])
# print(lens)
# flow_Newsize_Expansion(flow)
# lens = len(flow['NewSize'])
# print(" newsize is ",flow['NewSize'][1])
# print(lens)
# x = range(0,5,1)

# #test4 测试数学计算是否正确
# def check_mvacflow_size(mvacflow):
#     flowWidth = mvacflow['NewSizePixelLen'][0]
#     flowdepth = mvacflow['NewSizePixelLen'][1]

#     res =  flowWidth / flowdepth 
#     if res > 6 or res < 1/6 :
#         return False
        
#     else:
#         return True
    
#815 
# mvacflow={'Route': [[410, 0, None],[410, 420, None],[0, 420, None]],
#                'Type': '12031',
#                'Size': [101, 101],
#                'Elbow': [[0, 0], [0, 0]],
#                'Insulation':0,
#                'NewSizePixelLen':[[400,300],[200,150]]}
# #列表要使用copy,变量不用
# temp_flow_newsize1 = mvacflow['NewSizePixelLen'][1].copy()
# print(temp_flow_newsize1)
# mvacflow['NewSizePixelLen'][1] = temp_flow_newsize1.copy()
# mvacflow['NewSizePixelLen'][1][0] = 100 
# print(temp_flow_newsize1)
# print(temp_flow_newsize1)
# temp_flow_newsize1[0] = 100
# print(temp_flow_newsize1)
# print(mvacflow['NewSizePixelLen'][1])
# temp_flow_newsize0 = mvacflow['NewSizePixelLen'][0]
# print(temp_flow_newsize0)
# temp_flow_newsize0[0] = 100
# print(temp_flow_newsize0)
# print(mvacflow['NewSizePixelLen'][1])
# newsize1 = mvacflow['NewSizePixelLen'][1][0]
# newsize1 = 100
# print(mvacflow['NewSizePixelLen'][1][0])

#test6  切片也不会改变原来的值
# a = [6,6,6,7,7,7,8,8,8,9,9,9]
# b = a[:]
# b[1] = 4
# print(a)
# c  = a.copy()
# c[1] = 4
# print(a)
# d = a
# d[1] = 4
# print(a)

#test7
# val = 72
# graFlowflag = [61,62,63,100,101,102]
# mvacFlowflag = [71,72,73,200,201,202]

# if val in graFlowflag:
#     print('is graflow')
# elif val in mvacFlowflag :
#     print('is mvacflow')
# testlist = [1,[2,2],3,4]
# a,b,c,d= testlist
# print(a,b,c)

# import numpy as np

# def ReturnToRealCoord(Segment,LenPixel):
#     RealSegment = Segment.copy()
#     RealFlowRoute = []
#     for segment in RealSegment:
#         for coord in segment:
#             coord[0] *= LenPixel
#             coord[1] *= LenPixel
#             coord[2] *= LenPixel
#             RealFlowRoute.append([coord[0],coord[1],coord[2]])
#     return RealSegment,RealFlowRoute

# Segment = [[[10,0,5],[12,0,5],[12,0,10],[14,0,10],[14,0,5],[16,0,5]],[[16,0,5],[16,10,5]],[[16,10,5],[20,10,5]]]

# RealFlowRoute = []
# RealSegment = []
# RealSegment,RealFlowRoute = ReturnToRealCoord(Segment,10)
# print('RealFlowRoute',RealFlowRoute)
    
