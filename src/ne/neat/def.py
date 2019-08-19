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

def createPopParam(netdef,fitness,**kwargs):
    if kwargs is None : kwargs = {}
    if 'size' not in kwargs: raise RuntimeError('lost size in createPopParam')
    if 'elitistSize' not in kwargs: raise RuntimeError('lost elitistSize in createPopParam')
    # ������Ⱥ
    popParam = {
        'indTypeName': 'network'  if 'indTypeName' not in kwargs else kwargs['indTypeName'],  # ��Ⱥ�ĸ�����������������룬�����͵ĸ������Ӧ�Ѿ�ע������μ�evolution.agent,����
        'genomeFactory': None if 'genomeFactory' not in kwargs else kwargs['genomeFactory'],  # ���򹤳��������������Ѿ��ṩ�˻��򹤳���������������ã������滻ǰ�ߣ���ѡ
        'factoryParam': {  # ��������������
            'connectionRate': 1.0 if 'connectionRate' not in kwargs else kwargs['connectionRate'],  # ���ӱ���
        },
        'genomeDefinition': netdef,  # ���������,��ѡ
        'size': kwargs['size'],  # ��Ⱥ��С������
        'elitistSize': kwargs['elitistSize'],  # ��Ӣ����ռ�ȣ�С��1��ʾ���������ڵ���1��ʾ����
        'species': {  # ���ֲ�������ѡ
            'method': 'neat_species',  # ���ַ��෽��,�����ֲ����б���
            'alg': 'kmean',  # �㷨����
            'size': 5,  # ���ָ����������ƣ�0��ʾ�����ƻ�̬
            'iter': 50,  # �㷨��������
        },
        'features': {  # ���������������ã�����
            'fitness': Evaluator('fitness', [(fitness, 1.0)]) if 'evaluator' not in kwargs else kwargs['evaluator']# ��Ӧ��������,���������ֻ����һ������,Ҳ����д��Evaluator('fitness',fitness)
        }
    }
    return Properties(popParam)


def createRunParam(maxIterCount=10000,maxFitness=10000,**kwargs):
    if kwargs is None:kwargs = {}
    # �������в���
    runParam = {
        'terminated': {
            'maxIterCount': maxIterCount,  # ����������������
            'maxFitness': maxFitness,  # �����Ӧ�ȣ�����
        },
        'log': {
            'individual': 'elite' if 'logindividual' not in kwargs else kwargs['logindividual'],  # ��־�м�¼���巽ʽ����¼���и��壬����ѡ��all,elite,maxfitness��ȱʡ��,custom
            'debug': False if 'debug' not in kwargs else kwargs['debug'],  # �Ƿ����������Ϣ
            'file': 'neat_cartpole.log' if 'logfile' not in kwargs else kwargs['logfile']  # ��־�ļ���
        },
        'evalate': {
            'parallel': 0  ,  # ����ִ���������̸߳�����ȱʡ0����ѡ
        },
        'operations': {
            # 'method' : 'neat',                                   # ���еĽ��������������ƣ���text����ֻ��һ��
            'text': 'neat_selection,neat_crossmate,neat_mutate' if 'operations' not in kwargs else kwargs['operations']  # ������������
        },
        'mutate': {
            'propotion': 0.1 if 'mutate_propotion' not in kwargs else kwargs['mutate_propotion'],  # �������,�ж��ٸ����������죬С�ڵ���1��ʾ����������1��ʾ�̶�����
            'parallel': 0 if 'mutate_parallel' not in kwargs else kwargs['mutate_parallel'],  # ����ִ�б�����̸߳�����ȱʡ0����ѡ
            'model': {
                'rate': 0.0 if 'mutate_model_rate' not in kwargs else kwargs['mutate_model_rate'],  # ģ�ͱ������
                'range': '' if 'mutate_model_range' not in kwargs else kwargs['mutate_model_range'] # ��ѡ�ļ���ģ�����ƣ�����ö��ŷֿ���ȱʡ��netdef������ģ��
            },
            'activation': {
                'rate': 0.0 if 'mutate_activation_rate' not in kwargs else kwargs['mutate_activation_rate'],  # ������ı������
                'range': 'sigmod' if 'mutate_activation_range' not in kwargs else kwargs['mutate_activation_range']  # �������
            },
            'topo': {
                'addnode': 0.4  if 'mutate_addnode' not in kwargs else kwargs['mutate_addnode'],  # ��ӽڵ�ĸ���
                'addconnection': 0.4 if 'mutate_addconnection' not in kwargs else kwargs['mutate_addconnection'],  # ������ӵĸ���
                'deletenode': 0.1  if 'mutate_deletenode' not in kwargs else kwargs['mutate_deletenode'],  # ɾ���ڵ�ĸ���
                'deleteconnection': 0.1  if 'mutate_deleteconnection' not in kwargs else kwargs['mutate_deleteconnection']  # ɾ�����ӵĸ���
            },
            'weight': {
                'parallel': 0 if 'weight_parallel' not in kwargs else kwargs['weight_parallel'],  # ����ִ��Ȩ�ر�����̸߳�����ȱʡ0����ѡ
                'epoch': 1 if 'weight_epoch' not in kwargs else kwargs['weight_epoch'],  # Ȩ�ص�������
            }
        }

    }
    return Properties(runParam)
