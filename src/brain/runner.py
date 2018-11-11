import numpy as np
from enum import Enum
from utils import collections
from utils.properties import Registry
from utils.strs import ExtendJsonEncoder

import brain.models as models

__all__ = ['EndCondition','NeuralNetworkTask','SimpleNeuralNetworkRunner','runners']
# 训练终止条件类型
class EndCondition(Enum):
    MAXEPOCH = 1,
    MINDICATOR = 2,
    MAXDICATOR = 4,
    MINERROR = 8,
    MAXERRORUNCHANGED = 16

# 神经网络训练任务
class NeuralNetworkTask:

    #region 测试指标名称
    #测试指标：测试样本数
    INDICATOR_TEST_COUNT = 'testCount'
    #测试指标：测试正确数
    INDICATOR_CORRECT_COUNT = 'correctCount'
    # 测试指标：准确率
    INDICATOR_ACCURACY = 'accuracy'
    # 测试指标：MAE
    INDICATOR_MEAN_ABSOLUTE_ERROR = 'MAE'
    # 测试指标：MSE
    INDICATOR_MEAN_SQUARED_ERROR = 'MSE'
    #endregion

    #region 初始化

    def __init__(self,train_x=[],train_y=[],test_x=[],test_y=[],**kwargs):
        '''
        神经网训练任务
        :param train_x:   训练样本
        :param train_y:   训练标签
        :param test_x:    测试样本
        :param test_y:    测试标签
        :param kwargs     配置参数:
                           'deviation' : 0.00001 float or list of float 度量准确性的允许误差
                           'multilabel': False   bool                   是否是多标签
        '''
        self.train_x = train_x
        self.train_y = train_y
        self.test_x = test_x
        self.test_y = test_y
        self.test_result = [[]]*len(test_y)
        self.kwargs = {} if kwargs is None else kwargs
        if 'deviation' not in self.kwargs.keys():self.kwargs['deviation'] = 0.00001
        if 'multilabel' not in self.kwargs.keys():self.kwargs['multilabel'] = False




# 简单前馈神经网络运行期
class SimpleNeuralNetworkRunner:
    def __init__(self):
        '''
        简单前馈神经网络运行器（要求神经网络无自连接，无循环，全部都是前馈连接）
        '''
        pass

    def doLearn(self,net,task):
        '''
        未实现
        :param net:
        :param task:
        :return:
        '''
        pass

    def doTest(self,net,task):
        '''
        执行测试
        :param net:  测试网络
        :param task: 测试任务
        :return: None
        '''
        # 取得输入
        inputNeurons = net.getInputNeurons()
        #对每一个输入样本
        for index,value in enumerate(task.test_x):
            # 重置神经元和突触状态
            collections.foreach(net.getNeurons(),lambda n:n.reset())
            collections.foreach(net.getSynapses(),lambda s:s.reset())

            # 设置输入
            for d,v in enumerate(value):
                if d >= len(inputNeurons):break
                model = models.nervousModels.find(inputNeurons[d].modelConfiguration.modelid)
                model.execute(inputNeurons[d],net,value=v)

                s = net.getOutputSynapse(inputNeurons[d].id)
                if collections.isEmpty(s):continue

                collections.foreach(s,lambda x:x.getModel().execute(x,net))

            # 反复执行
            ns = net.getNeurons()
            neuronCount = net.getNeuronCount()
            iterCount = 0
            outputNeurons = net.getOutputNeurons()
            while not collections.all(outputNeurons,lambda n:'value' in n.states.keys()) and iterCount<=neuronCount:
                iterCount += 1
                uncomputeNeurons = collections.findall(ns,lambda n:'value' not in n.states.keys())
                if collections.isEmpty(uncomputeNeurons):break
                for n in uncomputeNeurons:
                    model = n.getModel()
                    synapses = net.getInputSynapse(n.id)
                    if collections.isEmpty(synapses):continue
                    if not collections.all(synapses,lambda s:'value' in s.states.keys()):continue
                    model.execute(n,net)

                    synapses = net.getOutputSynapse(n.id)
                    if collections.isEmpty(synapses):continue
                    collections.foreach(synapses,lambda s:s.getModel().execute(s,net))

            # 将没结果的输出神经元的值设置为0
            outputNeuronsWithNoResult = collections.findall(outputNeurons,lambda n:'value' not in n.states.keys())
            if not collections.isEmpty(outputNeuronsWithNoResult):
                collections.foreach(outputNeuronsWithNoResult,lambda n:exec("n['value']=0"))
            # 取得结果
            outputs = list(map(lambda n:n['value'],outputNeurons))
            if len(outputs) == 1:outputs = outputs[0]
            net.setTestResult(index,outputs)



# 基于tf的神经网络运行器
class TensorflowNeuralNetworkRunner:
    pass



# 运行器注册
runners = Registry()
runners.register(SimpleNeuralNetworkRunner(),'simple')

ExtendJsonEncoder.ignoreTypes.append(NeuralNetworkTask)
