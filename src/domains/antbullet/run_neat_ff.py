# -*- coding: UTF-8 -*-

import os
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0, parentdir)

from pybullet_envs.bullet import bullet_client

from evolution.session import EvolutionTask
import ne.neat as neat
import ne.neat.config as config
import evolution
import domains.antbullet.env as env
from brain.networks import NeuralNetworkTask

if __name__ == '__main__':
    # NEAT 前馈网络
    neat.neat_init()

    task = NeuralNetworkTask()
    netdef = config.createNetDef(task,neuronCounts=[30,8])
    popParam = evolution.createPopParam(indTypeName='network',
                                    size=100,
                                    elitistSize=0.01,
                                    genomeDefinition=netdef,
                                    evaluators=env.fitness,
                                    species=config.defaultSpeciesMethod()
    )
    runParam = evolution.createRunParam()

    evolutionTask = EvolutionTask(1,popParam,env.callback)
    evolutionTask.execute(runParam)
