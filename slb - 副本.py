#!/usr/bin/python
#coding=utf-8
# for ansible 
# change slb 后端服务器权重
# by lujin 卢进
# 2017-11-16
# 第二版，添加切换vpc中服务器负载
# 需要安装阿里云sdk
# pip install aliyun-python-sdk-ecs
# pip install aliyun-python-sdk-slb

import sys,json,time
from aliyunsdkcore import client
from aliyunsdkslb.request.v20140515 import  DescribeLoadBalancersRequest
from aliyunsdkslb.request.v20140515 import SetBackendServersRequest
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
import json

ID = '***'
Secret = '***'
RegionId = 'cn-beijing'



#后端服务器ip
Ip = sys.argv[1]
InsIp = [Ip]

#后端服务器权重(0-100)
weight = sys.argv[2]

#连接阿里云平台
clt = client.AcsClient(ID,Secret,RegionId)


def GetInstancesId(InsIp):

    try:
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')

        request.add_query_param('RegionId', RegionId)    
        request.add_query_param('InnerIpAddresses', InsIp)
        response = clt.do_action_with_exception(request)
        nobuer = response.replace('false','0').replace('true','1')
        dictecs = eval(nobuer)
        InstancesId = dictecs['Instances']['Instance'][0]['InstanceId']
        return InstancesId

    except:
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format('json')
        request.add_query_param('RegionId', RegionId)
        request.add_query_param('PrivateIpAddresses', InsIp)
        response = clt.do_action_with_exception(request)
        nobuer = response.replace('false','0').replace('true','1')
        dictecs = eval(nobuer)
        InstancesId = dictecs['Instances']['Instance'][0]['InstanceId']
        return InstancesId

def ChangeSlbWeight(LoadBalancerId,LoadBalancerName,serverid,weight):
    #定义参数
    BackendServers=[{"ServerId":serverid,"Weight":weight}]
    # 设置参数
    request1 = SetBackendServersRequest.SetBackendServersRequest()
    request1.set_accept_format('json')
#    request1.set_LoadBalancerId(LoadBalancerId)
    request1.add_query_param('LoadBalancerId', LoadBalancerId)
    request1.add_query_param('BackendServers', BackendServers)
    


    # 发起请求
    response1 = clt.do_action_with_exception(request1)
    # time.sleep(2)
    # 输出结果
    dicslb = eval(response1)
    #SId = dicslb['BackendServers']['BackendServer'][0]['ServerId']
    #FZ = dicslb['BackendServers']['BackendServer'][0]['Weight']
    slblist = dicslb['BackendServers']['BackendServer']
    slblen = len(slblist)
#    print dicslb
#    print slblist
#    print slblen
    if slblen >0:
#        outlist = []       
        for n in range(slblen):
            Sid = slblist[n]['ServerId']
            FZ = slblist[n]['Weight']
            if Sid == serverid:
                print LoadBalancerName,'负载权重为:',FZ,','


if __name__ == "__main__":


    #通过ip获取serverid的值
    serverid = GetInstancesId(InsIp)
    #print serverid
    ###获取slbid 
    # 设置参数 
    request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
    request.set_accept_format('json')
    request.add_query_param('RegionId', RegionId)
    request.add_query_param('ServerId', serverid)

    # 发起请求
    response = clt.do_action_with_exception(request)
    # 输出结果
    #print response
    #转换成字典
    dic = eval(response)
    #print dic
    #获取slb个数
    num = dic['TotalCount']
    for i in range(0,num):
       
        LoadBalancerName = dic['LoadBalancers']['LoadBalancer'][i]['LoadBalancerName']
        LoadBalancerId = dic['LoadBalancers']['LoadBalancer'][i]['LoadBalancerId']
        try: 
            ChangeSlbWeight(LoadBalancerId,LoadBalancerName,serverid,weight)
        except:    
            continue
