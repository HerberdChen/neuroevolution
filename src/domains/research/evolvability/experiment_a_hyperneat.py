#!/usr/bin/python
# -*- coding: UTF-8 -*-

import matplotlib.pyplot as plt
import gc
import os
import numpy as np
import csv

from domains.cartpoles.enviornment.cartpole import SingleCartPoleEnv
import ne.callbacks as callbacks
import ne.neat as neat
from brain.networks import NetworkType
from brain.networks import NeuralNetwork
from brain.runner import NeuralNetworkTask
from evolution.env import Evaluator
from evolution.session import EvolutionTask
from utils.properties import Properties
from ne.neat.idgenerator import NeatIdGenerator
import brain.networks as networks

import domains.cartpoles.enviornment.force as force
import domains.cartpoles.enviornment.runner as runner

from ne.hyperneat.decode import HyperNEAT
from evolution.agent import IndividualType
from ne.factory import DefaultNeuralNetworkGenomeFactory
import evolution.agent as agent
from brain.viewer import NetworkView
import utils.files as files

hyperneatdatapath = files.get_data_path()+os.sep + 'evolvability' + os.sep + 'experimentA' + os.sep + 'hyperneat' + os.sep

def fitness(ind,session):
    '''
    以连续不倒的次数作为适应度
    :param ind:
    :param session:
    :return:
    '''
    env = SingleCartPoleEnv()
    net = ind.getPhenome()
    reward_list, notdone_count_list = runner.do_evaluation(1,env,net.activate)

    return max(notdone_count_list)

env = SingleCartPoleEnv()
fitness_records = []
complex_records=[]
maxfitness_records = []

mode = 'noreset'
epochcount = 0
maxepochcount = 10
complexunit = 20.

exec_xh = 0
epoch_maxfitness = 0.
epoch_maxfitness_ind = None

# 记录最优个体的平衡车运行演示视频
def callback(event,monitor):
    callbacks.neat_callback(event,monitor)
    global epochcount
    global mode
    global exec_xh
    global epoch_maxfitness
    global epoch_maxfitness_ind
    if event == 'epoch.end':
        #gc.collect()
        maxfitness = monitor.evoTask.curSession.pop.inds[0]['fitness']
        maxfitness_ind = monitor.evoTask.curSession.pop.inds[0]
        maxfitness_records.append(maxfitness)
        if maxfitness > epoch_maxfitness:
            epoch_maxfitness = maxfitness
            epoch_maxfitness_ind = maxfitness_ind

        # 如果最大适应度达到了env.max_notdone_count（说明对当前环境已经产生适应），或者进化迭代数超过10次（当前环境下适应达到最大）
        # 则提升复杂度
        epochcount += 1
        if maxfitness >= env.max_notdone_count or epochcount >= maxepochcount:
            #保存复杂度和对应最大适应度记录
            fitness_records.append(maxfitness)
            complex_records.append(force.force_generator.currentComplex())
            print([(f, c) for f, c in zip(complex_records, fitness_records)])
            np.save('hyperneat_result', (complex_records, fitness_records))

            # 保存过程中每一步的最大适应度记录
            filename = hyperneatdatapath + 'hyperneat_' + mode + '_' + str(exec_xh) + '.csv'
            out = open(filename, 'a', newline='')
            csv_write = csv.writer(out, dialect='excel')
            csv_write.writerow([complex_records[-1]]+maxfitness_records)
            maxfitness_records.clear()

            # 保存最优基因网络拓扑
            filename = hyperneatdatapath + 'hyperneat_' + mode + '_' + str(exec_xh) + '_' + \
                       str(complex_records[-1]) + '_' + str(epoch_maxfitness_ind.id) + '_' + \
                       str(epoch_maxfitness) + '.svg'
            netviewer = NetworkView()
            netviewer.drawNet(maxfitness_ind.genome, filename=filename, view=False)

            # 提升复杂度
            changed, maxcomplex, k,w, f, sigma = force.force_generator.promptComplex(complexunit)
            if changed and  maxcomplex is not None:
                print('环境复杂度=%.3f,k=%.2f,w=%.2f,f=%.2f,sigma=%.2f' % (maxcomplex, k,w, f, sigma))
                if mode == 'reset':
                    monitor.evoTask.curSession.runParam.terminated.maxIterCount = epochcount-1
            else:
                np.save('hyperneat_result', complex_records, fitness_records)
                #plt.plot(complex_records, reward_list, label='reward')
                plt.plot(complex_records, fitness_records, label='times')
                plt.xlabel('complexes')
                plt.savefig('./hyperneat_cartpole.png')

            epoch_maxfitness = 0.
            epoch_maxfitness_ind = None
            epochcount = 0

    elif event == 'session.end':
        filename = 'singlecartpole.session.'+ str(monitor.evoTask.curSession.taskxh)+'.mov'
        eliest = monitor.evoTask.curSession.pop.eliest
        #cartpole.make_movie(eliest[0].getPhenome(),filename)

def run(**kwargs):
    global mode
    global maxepochcount
    global complexunit

    #mode = 'noreset' if 'mode' not in kwargs.keys() else kwargs['mode']
    #maxepochcount = 10 if 'maxepochcount' not in kwargs.keys() else int(kwargs['maxepochcount'])
    #complexunit = 20.0 if 'complexunit' not in kwargs.keys() else float(kwargs['complexunit'])
    mode = 'noreset' if 'mode' not in kwargs else kwargs['mode']
    maxepochcount = 10 if 'maxepochcount' not in kwargs else int(kwargs['maxepochcount'])
    complexunit = 20.0 if 'complexunit' not in kwargs else float(kwargs['complexunit'])

    while True:
        execute()
        if mode == 'reset':
            continue
        break


def execute():
    # 初始化neat算法模块
    neat.neat_init()

    # 定义网络训练任务

    task = NeuralNetworkTask()

    # 注册id生成器对象
    networks.idGenerators.register(NeatIdGenerator(), 'hyperneat')

    # 定义工作网络
    worknetdef = {
        'netType' : NetworkType.Perceptron,                       # NetworkType，网络类型,必须
        'neuronCounts' : [4,5,5,5,1],                             # list（初始）网络各层神经元数量,必须
        'idGenerator' :  'hyperneat',                                  # str 生成网络，神经元，突触id的类，参见DefauleIDGenerator,list idgenerator命令可以列出所有的id生成器对象
        'config' : {
            'layered' : True,                                     # bool 是否分层,可选
            'substrate' : True,                                   # bool 是否使用基座,可选
            'acyclie' : False,                                    # bool 是否允许自身连接,可选
            'recurrent':False,                                    # bool 是否允许同层连接,可选
            'reversed':False,                                     # bool 是否允许反向连接,可选
            'across':False,                                       # bool s是否允许跨层连接
            'dimension':2,                                        # int 空间坐标维度,可选
            'range':[(-2,2),(-3,3)]                               # 最大坐标范围,                      # list 坐标范围，可选'
        },
        'runner':{
            'name' : 'simple',                                    # str 网络运行器名称,必须
            'task' : task,                                        # NeuralNetworkTask,网络运行任务,必须
        },
        'models':{                                                # dict 神经元计算模型的配置信息,必须
            'input':{                                             # str 模型配置名称（不是模型名称）
                'name' : 'input',                                 # str,名称，与上面总是一样,可选
                'modelid':'input',                                # str，模型id，必须，用这个来找到对应的计算模型对象,因此应确保该计算模型已注册
            },
            'hidden':{
                'name':'hidden',                                  # str 隐藏神经元配置名称，可选
                'modelid':'hidden',                               # str 隐藏神经元计算模型id,必须
                'activationFunction':{                            # dict 可选
                    'name' : 'sigmod',                            # str 激活函数名称，必须
                    'a' :1.0,'b':1.0,'T':1.0                      # float 激活函数参数，可选
                },
                'bias':'uniform[-30.0:30.0]',                     # str 隐藏神经元的偏置变量，均匀分布，必须，可以是uniform[begin,end]或者normal(u,sigma)
            },
            'output': {
                'name': 'output',  # str 隐藏神经元配置名称，可选
                'modelid': 'hidden',  # str 隐藏神经元计算模型id,必须
                'activationFunction': {  # dict 可选
                    'name': 'sigmod',  # str 激活函数名称，必须
                    'a': 1.0, 'b': 1.0, 'T': 1.0  # float 激活函数参数，可选
                },
                'bias': 'uniform[-30.0:30.0]',  # str 隐藏神经元的偏置变量，均匀分布，必须，可以是uniform[begin,end]或者normal(u,sigma)
            },
            'synapse':{
                'name':'synapse',                                 # str 突触计算模型配置名称,可选
                'modelid':'synapse',                              # str 突触计算模型Id，必须
                'weight':'uniform[-30.0:30.0]'                    # str 突触学习变量，均匀分布，必须
            }
        }
    }


    # 定义cppn网络
    cppnnetdef = {
        'netType' : NetworkType.Perceptron,                       # NetworkType，网络类型,必须
        'neuronCounts' : [4,1],                                   # list（初始）网络各层神经元数量,必须
        'idGenerator' :  'neat',                                  # str 生成网络，神经元，突触id的类，参见DefauleIDGenerator,list idgenerator命令可以列出所有的id生成器对象
        'config' : {
            'layered' : True,                                     # bool 是否分层,可选
            'substrate' : True,                                   # bool 是否使用基座,可选
            'acyclie' : False,                                    # bool 是否允许自身连接,可选
            'recurrent':False,                                    # bool 是否允许同层连接,可选
            'reversed':False,                                     # bool 是否允许反向连接,可选
            'dimension':2,                                        # int 空间坐标维度,可选
            'range':NeuralNetwork.MAX_RANGE,                      # list 坐标范围，可选'
        },
        'runner':{
            'name' : 'simple',                                    # str 网络运行器名称,必须
            'task' : task,                                        # NeuralNetworkTask,网络运行任务,必须
        },
        'models':{                                                # dict 神经元计算模型的配置信息,必须
            'input':{                                             # str 模型配置名称（不是模型名称）
                'name' : 'input',                                 # str,名称，与上面总是一样,可选
                'modelid':'input',                                # str，模型id，必须，用这个来找到对应的计算模型对象,因此应确保该计算模型已注册
            },
            'hidden':{
                'name':'hidden',                                  # str 隐藏神经元配置名称，可选
                'modelid':'hidden',                               # str 隐藏神经元计算模型id,必须
                'activationFunction':{                            # dict 可选
                    'selection':['gaussian','linear','sigmod','sine'],# list 随机选取
                    'name' : 'sigmod',                            # str 激活函数名称，必须
                    'a' :1.0,'b':1.0,'T':1.0                      # float 激活函数参数，可选
                },
                'bias':'uniform[-5.0:5.0]',                     # str 隐藏神经元的偏置变量，均匀分布，必须，可以是uniform[begin,end]或者normal(u,sigma)
            },
            'synapse':{
                'name':'synapse',                                 # str 突触计算模型配置名称,可选
                'modelid':'synapse',                              # str 突触计算模型Id，必须
                'weight':'uniform[-5.0:5.0]'                    # str 突触学习变量，均匀分布，必须
            }
        }
    }


    hypneat = HyperNEAT(worknetdef)
    neuralNetworkIndType = IndividualType('cppn', NeuralNetwork, DefaultNeuralNetworkGenomeFactory(), NeuralNetwork,hypneat)
    agent.individualTypes.register(neuralNetworkIndType, 'cppn')
    # 定义种群
    popParam = {
        'indTypeName' : 'cppn',                                #种群的个体基因类型名，必须，该类型的个体基因应已经注册过，参见evolution.agent,必须
        'genomeFactory':None,                                     #基因工厂，个体类型中已经提供了基因工厂对象，这里如果设置，可以替换前者，可选
        'factoryParam' :{                                         # 工厂参数，必须
           'connectionRate':1.0,                                  # 连接比率
        },
        'genomeDefinition' : cppnnetdef,                              #基因定义参数,可选
        'size':30,                                               #种群大小，必须
        'elitistSize':0.1,                                        #精英个体占比，小于1表示比例，大于等于1表示数量
        'species':{                                               #物种参数，可选
            'method':'neat_species',                              # 物种分类方法,在物种参数中必须
            'alg':'kmean',                                        # 算法名称
            'size': 3,                                            # 物种个体数量限制，0表示无限制或动态
            'iter':50,                                            # 算法迭代次数
        },
        'features':{                                              # 特征评估函数配置，必须
            'fitness' : Evaluator('fitness',[(fitness,1.0)])      # 适应度评估器,如果评估器只包含一个函数,也可以写成Evaluator('fitness',fitness)
        }
    }


    # 定于运行参数
    runParam = {
        'terminated' : {
            'maxIterCount' : 100000,                               # 最大迭代次数，必须
            'maxFitness' : 1000000.,                                   # 最大适应度，必须
        },
        'log':{
            'individual' : 'elite',                                 # 日志中记录个体方式：记录所有个体，可以选择all,elite,maxfitness（缺省）,custom
            'debug': False,                                        # 是否输出调试信息
            'file': 'hyperneat_cartpole.log'  # 日志文件名
        },
        'evalate':{
            'parallel':30,                                         # 并行执行评估的线程个数，缺省0，可选
        },
        'operations':{
            #'method' : 'neat',                                   # 已有的进化操作序列名称，与text两个只用一个
            'text' : 'neat_selection,neat_crossmate,neat_mutate'  # 进化操作序列
        },
        'mutate':{
            'propotion' : 0.1,                                      # 变异比例,有多少个个体参与变异，小于等于1表示比例，大于1表示固定数量
            'parallel': 0,  # 并行执行变异的线程个数，缺省0，可选
            'model':{
                'rate' : 0.0,                                     # 模型变异比例
                'range' : ''                                      # 可选的计算模型名称，多个用逗号分开，缺省是netdef中所有模型
            },
            'activation':{
                'rate' : 0.1,                                     # 激活函数的变异比率
                'range':'sigmod'                                  # 激活函数的
            },
            'topo' : {
                'addnode' : 0.4,                                  # 添加节点的概率
                'addconnection':0.3,                              # 添加连接的概率
                'deletenode':0.1,                                 # 删除节点的概率
                'deleteconnection':0.1                            # 删除连接的概率
            },
            'weight':{
                'parallel': 30,  # 并行执行权重变异的线程个数，缺省0，可选
                'epoch':2,                                          # 权重调整次数
            }
        }
    }

    evolutionTask = EvolutionTask(1,popParam,callback)
    evolutionTask.execute(runParam)

if __name__ == '__main__':
    force.init()
    run(mode='noreset', maxepochcount=30, complexunit=20., xh=0)