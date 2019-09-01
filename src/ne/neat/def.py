from brain.networks import  *
from utils.properties import Properties
from evolution.env import Evaluator

def createNetDef(task,**kwargs):
    '''
    ִ��
    :return:
    '''

    if kwargs is None: kwargs = {}
    if 'neuronCounts' not in kwargs:raise RuntimeError('can not find neuronCounts in createNetDef ')
    # ��������
    netdef = {
        'netType' : NetworkType.Perceptron if 'netType' not in kwargs else  kwargs['netType'],                       # NetworkType����������,����
        'neuronCounts' : kwargs['neuronCounts'],                                                                     # list����ʼ�����������Ԫ����,����
        'idGenerator' :  'neat' if 'idGenerator' not in kwargs else  kwargs['idGenerator'],                          # str �������磬��Ԫ��ͻ��id���࣬�μ�DefauleIDGenerator,list idgenerator��������г����е�id����������
        'config' : {
            'layered' : True if 'layered' not in kwargs else  kwargs['layered'],                                     # bool �Ƿ�ֲ�,��ѡ
            'substrate' : True if 'substrate' not in kwargs else  kwargs['substrate'],                               # bool �Ƿ�ʹ�û���,��ѡ
            'acyclie' : False if 'acyclie' not in kwargs else  kwargs['acyclie'],                                    # bool �Ƿ�������������,��ѡ
            'recurrent':False if 'recurrent' not in kwargs else  kwargs['recurrent'],                                # bool �Ƿ�����ͬ������,��ѡ
            'reversed':False if 'reversed' not in kwargs else  kwargs['reversed'],                                   # bool �Ƿ�����������,��ѡ
            'dimension':2  if 'dimension' not in kwargs else  kwargs['dimension'],                                   # int �ռ�����ά��,��ѡ
            'range':NeuralNetwork.MAX_RANGE if 'dimension' not in kwargs else  kwargs['dimension'],                  # list ���귶Χ����ѡ'
        },
        'runner':{
            'name' : 'simple' if 'runnername' not in kwargs else  kwargs['runnername'] ,                             # str ��������������,����
            'task' : task,                                        # NeuralNetworkTask,������������,����
        },
        'models':kwargs['models'] if 'models' not in kwargs else {                                                # dict ��Ԫ����ģ�͵�������Ϣ,����
            'input':{                                             # str ģ���������ƣ�����ģ�����ƣ�
                'name' : 'input',                                 # str,���ƣ�����������һ��,��ѡ
                'modelid':'input',                                # str��ģ��id�����룬��������ҵ���Ӧ�ļ���ģ�Ͷ���,���Ӧȷ���ü���ģ����ע��
            },
            'hidden':{
                'name':'hidden',                                  # str ������Ԫ�������ƣ���ѡ
                'modelid':'hidden',                               # str ������Ԫ����ģ��id,����
                'activationFunction':{                            # dict ��ѡ
                    'name' : 'sigmod',                            # str ��������ƣ�����
                    'a' :1.0,'b':1.0,'T':1.0                      # float �������������ѡ
                },
                'bias':'uniform[-30.0:30.0]',                     # str ������Ԫ��ƫ�ñ��������ȷֲ������룬������uniform[begin,end]����normal(u,sigma)
            },
            'synapse':{
                'name':'synapse',                                 # str ͻ������ģ����������,��ѡ
                'modelid':'synapse',                              # str ͻ������ģ��Id������
                'weight':'uniform[-30.0:30.0]'                    # str ͻ��ѧϰ���������ȷֲ�������
            }
        }
    }
    return Properties(netdef)

