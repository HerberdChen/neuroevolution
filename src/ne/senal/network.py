import numpy as np
import brain.networks as networks
from brain.networks import NeuralNetwork
from ne.senal.box import BoxGene
from ne.senal.box import Box
from ne.senal.box import FeatureNeuron
from brain.networks import DefaultIdGenerator
import utils.collections as collecitons
import operator


class SenalIdGenerator(DefaultIdGenerator):
    def __init__(self):
        super(SenalIdGenerator, self).__init__()
        self.boxids = {}
        self.boxid = 1

    def getNeuronId(self):
        self.neuronId += 1
        return self.neuronId

    def getBoxId(self,attented_boxid_list,sensor_name=''):
        if sensor_name != '':
            if sensor_name not in self.boxids:
                self.boxids[sensor_name] = self.boxid
                self.boxid += 1
            return self.boxids[sensor_name]
        else:
            attented_boxid_list = np.sort(attented_boxid_list)

class SENetworkGenome:
    def __init__(self,genomeDefinition):
        '''
        SENAL网络染色体
        '''
        self.definition = genomeDefinition
        self.sensor_box_genes = []            # 感知盒子基因，参见BoxGene
        self.attention_box_genes = []         # 注意盒子基因，参见BoxGene
        self.action_box_genes = []            # 动作盒子基因，保留
        self.receptor_box_genes = []          # 感受器基因，参见BoxGene

        self.attention_genes = []             # 注意基因，参见BoxAttentionGene
        self.action_connection_genes = []     # 动作连接基因，参见BoxActionGene

    def find_box_by_expression(self,expression):
        boxes = self.sensor_box_genes + self.attention_box_genes + self.action_box_genes + self.receptor_box_genes
        for box in boxes:
            if box.expression == expression:return box
        return None

    def select_group_sensor(self,receptor_box):
        '''
        选择同组的感知基因
        :param receptor_box: BoxGene 效应器盒子
        :return: list of BoxGene
        '''
        # 将分组路径反过来
        groups = list(reversed(receptor_box.group.split('.')))
        results = []

        for i, group in enumerate(groups):
            for box in self.sensor_box_genes:
                if box.expression + '_' == receptor_box.expression: #该感知是对输出自身的感知，忽略
                    continue
                box_groups = box.group.split('.')
                if group in box_groups:
                    results.append(box)
            if len(results)>0:
                return results

        for box in self.sensor_box_genes:
            if box.expression + '_' == receptor_box.expression:  # 该感知是对输出自身的感知，忽略
                continue
            results.append(box)
        return results



    def get_upstream_genes(self,cur_box):
        '''
        取得cur_box的上游box
        :param cur_box:
        :return: list of BoxGene
        '''
        if cur_box.type == BoxGene.type_sensor or cur_box.type == BoxGene.type_attention:
            return [g for g in self.attention_genes if g.watcher == cur_box.id]
        else:
            return [g for g in self.action_connection_genes if g.action_box.id == cur_box.id]
    def get_downstream_attention_genes(self,cur_box):
        '''
        取得cur_box的下游box
        :param cur_box:
        :return: list of BoxGene
        '''
        return [g for g in self.attention_genes if cur_box.id in g.watched]

    def get_downstream_action_genes(self,cur_box):
        '''
        取得cur_box的下游动作盒子基因
        :param cur_box:
        :return:
        '''
        return [g for g in self.action_connection_genes if cur_box.id in g.activation_boxes]



class SENetworkDecoder:
    def __init__(self):
        '''
        基因解码器
        '''
        pass
    def decode(self,ind):
        '''
        解码方法
        :param ind:         Individual 个体
        :return: SENetwork
        '''

        genome = ind.genome
        all_genes = genome.sensor_box_genes + genome.attention_box_genes + \
                    genome.action_box_genes + genome.receptor_box_genes
        net = SENetwork(ind.id,genome.definition)
        idGenerator = networks.idGenerators.find(genome.definition.idGenerator)

        for box_gene in all_genes:
            box = Box(box_gene,net)
            net.putBox(box)
            for dis in box_gene.initdistribution:
                neuron = FeatureNeuron(idGenerator.getNeuronId(), 0, box.id, dis[0], dis[1], 0, None)
                box.nodes.append(neuron)

        for attention_gene in genome.attention_genes:
            watcher_box = net.getBox(attention_gene.watcher_id)
            watched_boxes = net.getBox(attention_gene.watched_ids)
            watcher_box.put_input_boxes(watched_boxes)
            for x in watched_boxes:
                x.put_output_boxes(watcher_box)

        for action_connection_gene in genome.action_connection_genes:
            action_box = net.getBox(action_connection_gene.action_box_id)
            attention_boxes = net.getBox(action_connection_gene.attention_box_ids)
            receptor_box = net.getBox(action_connection_gene.receptor_box_id)
            if action_box is not None:
                action_box.put_input_boxes(attention_boxes)
                for attention_box in attention_boxes:
                    attention_box.put_output_boxes(action_box)

                receptor_box.put_input_boxes(action_box)
                action_box.put_output_boxes(receptor_box)
            else:
                receptor_box.put_input_boxes(attention_boxes)
                if isinstance(attention_boxes,list):
                    for attention_box in attention_boxes:
                        attention_box.put_output_boxes(receptor_box)
                else:
                    attention_boxes.put_output_boxes(receptor_box)
        net.rearrange_depth()
        return net

class SENetwork(NeuralNetwork):
    def __init__(self,id,definition):
        super(SENetwork, self).__init__(id,definition)
        self.sensor_boxes = []  # 感知盒子，参见BoxGene
        self.attention_boxes = []  # 注意盒子，参见BoxGene
        self.action_boxes = []  # 动作盒子，保留
        self.receptor_boxes = []  # 感受器，参见BoxGene

        self.attentions = []  # 注意，参见BoxAttentionGene
        self.connections = []  # 动作连接，参见BoxActionGene

    def __str__(self):
        allbox = self.allbox()
        return str(self.id)+":"+collecitons.reduce(lambda x,y:str(x)+'\n'+str(y),allbox)

    def allbox(self):
        box = self.sensor_boxes + self.attention_boxes + self.action_boxes + self.receptor_boxes
        box = sorted(box,key=lambda x:x.depth)
        return box
    def get_sensor_box(self):
        return self.sensor_boxes
    def get_attention_box(self):
        return self.attention_boxes
    def get_cognition_box(self):
        return self.sensor_boxes + self.attention_boxes

    def get_action_box(self):
        return self.action_boxes
    def get_receptor_box(self):
        return self.receptor_boxes

    def putBox(self,box):
        if box.gene.type == BoxGene.type_sensor:
            self.sensor_boxes.append(box)
        elif box.gene.type == BoxGene.type_attention:
            self.action_boxes.append(box)
        elif box.gene.type == BoxGene.type_action:
            self.attention_boxes.append(box)
        elif box.gene.type == BoxGene.type_receptor:
            self.receptor_boxes.append(box)

    def getBox(self,id):
        if id is None:
            return None
        all_boxes = self.sensor_boxes + self.attention_boxes + self.action_boxes + self.receptor_boxes
        ids = []
        if isinstance(id,int):
            ids.append(id)
        else: ids = id

        r = [box for box in all_boxes if box.id in ids]
        return r[0] if len(r)==1 else r

    def findBox(self,type=None,group=None,expressType=None,depth=-1,expression=''):
        '''
        查找特定类型和分组条件的盒子
        :param type:
        :param group:
        :return:
        '''
        boxes = self.allbox()
        r = []

        for b in boxes:
            if group is not None and not b.gene.group.startswith(group):continue
            if type is not None and b.gene.type != type:continue
            if expressType is not None and not b.gene.expression.startswith(expressType):continue
            if depth>=0 and b.depth != depth:continue
            if expression is not None and expression != '' and expression != b.gene.expression:continue
            r.append(b)

        return r
        #return r if len(r)>1 or len(r)<=0 else r[0]


    def findTBox(self,cause=None,effect=None):
        allbox = self.allbox()
        box = [b for b in allbox if
                (b.getExpressionOperation() == 'T') and
                (cause is not None and b.isInExpressionParam(cause,parts='cause')) and
                (effect is not None and b.isInExpressionParam(effect,parts='effect'))]
        return sorted(box,key='depth',reverse=True)

    def findABox(self,params=None):
        allbox = self.allbox()
        box = [b for b in allbox if
                (b.getExpressionOperation() == 'A') and
                (params is not None and b.isInExpressionParam(params))]
        return sorted(box, key='depth', reverse=True)

    def find_receptor_boxes(self):
        return self.receptor_boxes;

    def findEnvSensorBox(self):
        '''
        查找负责环境感知的所有盒子
        :return:
        '''
        return self.findBox('sensor','env.')

    def rearrange_depth(self):
        allbox = self.allbox()
        maxdepth = 0
        for b in allbox:b.depth = -1
        for b in self.get_sensor_box():
            b.depth = 0
            allbox.remove(b)
        while len(allbox)>0:
            for b in allbox:
                if len(b.inputs)<=0:allbox.remove(b)
                elif collecitons.all(b.inputs,lambda x:x.depth != -1):
                    b.depth = np.max([t.depth for t in b.inputs])+1
                    maxdepth = b.depth if maxdepth<b.depth else maxdepth
                    allbox.remove(b)
        allbox = self.allbox()
        for b in allbox:
            if b.depth<0:b.depth = maxdepth+1

    def get_attented_box(self,boxes):
        '''
        取得以boxes为输入的所有box
        :param boxes: list 输入box
        :return:  list
        '''
        boxes.sort(key = 'id')
        all_box = self.allbox()
        r = []
        for box in all_box:
            inputs = box.inputs
            inputs.sort(key='id')
            if inputs == boxes:r.append(box)
        return r


    def clear_expect(self):
        allbox = self.allbox()
        for box in allbox:
            box.expection = 0.


    def activate(self, inputs):
        '''
        网络的一次激活活动
        :param inputs: list of (box,value) 多个元组组成的list，box是指Box本身或者id，value是给box的输入值向量
                       list中可以只有部分感知box
        :return:
        '''
        if inputs is None: return []

        allbox = self.allbox()
        count = len(allbox)

        for box,values in inputs:
            box.activate(values)
            allbox.remove(box)
            count -= len(allbox)

        max_depth = np.max([box.depth for box in allbox])
        for i in range(1,max_depth+1):
            boxes = self.findBox(depth=i)
            for box in boxes:
                if box not in allbox:continue
                if box.type != Box.type_attention:continue 
                if collecitons.all(box.inputs,lambda b: b in allbox):continue
                box.do_attention()
                allbox.remove(box)
                count -= len(allbox)

    def inference(self):
        depth = 1
        while True:
            boxes = self.findBox(depth=depth)
            if boxes is None or len(boxes)<=0:break
            collecitons.foreach(boxes,lambda b:b.do_inference)
        
