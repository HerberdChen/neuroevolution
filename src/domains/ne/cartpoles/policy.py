import numpy as np
import tensorflow as tf
import gym
import os

from domains.ne.cartpoles.enviornment.cartpole import SingleCartPoleEnv
import domains.ne.cartpoles.enviornment.runner as runner
from domains.ne.cartpoles.enviornment import force

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

batch_size = 25
learning_rate = 1e-1
gamma = 0.99

xs, ys, drs = [], [], []
reward_sum = 0

total_episodes = 1000# ���ݵ�ǰ�Ļ���״̬�������ؽڵ���actionΪ1�ĸ���


class PolicyNet:
    def __init__(self):
        # �����
        self.input_dimension = 4
        self.var_input_x = tf.placeholder(tf.float32, [None, self.input_dimension], name="input_x")
        # ���ز㣱(50����Ԫ+Relu)
        self.H1 = 50
        self.W1 = tf.get_variable("w1", shape=[D, self.H1],
                     initializer=tf.contrib.layers.xavier_initializer())
        self.L1 = tf.nn.relu(tf.matmul(self.var_input_x, self.W1))
        # �����
        self.W2 = tf.get_variable("w2", shape=[self.H1, 1],
                     initializer=tf.contrib.layers.xavier_initializer())
        self.L2 = tf.matmul(self.L1, self.W2)

        self.var_output = tf.nn.sigmoid(self.L2)# ���ݸ���������ʧ���ݶ�

        self.var_input_y = tf.placeholder(tf.float32, [None, 1], name="input_y")
        self.var_reward  = tf.placeholder(tf.float32, name="reward")

        self.loglik = tf.log(self.var_input_y * (self.var_input_y - self.var_output) +
                (1 - self.var_input_y) * (self.var_input_y + self.var_output))
        self.loss = -tf.reduce_mean(self.loglik * self.var_reward )

        self.tvars = tf.trainable_variables()
        self.newGrads = tf.gradients(self.loss, self.tvars)# �����ݶ��Ż�ѵ������������
        self.learning_rate = 1e-1
        self.adam = tf.train.AdamOptimizer(learning_rate=learning_rate)
        self.W1grad = tf.placeholder(tf.float32, name="batch_grad1")
        self.W2grad = tf.placeholder(tf.float32, name="batch_grad2")
        self.batchGrad = [self.W1grad,self.W2grad]
        self.updateGrads = self.adam.apply_gradients(zip(self.batchGrad, self.tvars))

    def discount_reward(r):
        # ����ÿ��reward:r��gamma����ÿ�ε�Ǳ�ڼ�ֵ
        discount_r = np.zeros_like(r)
        running_add = 0
        for t in reversed(range(r.size)):
            running_add = running_add * gamma + r[t]
            discount_r[t] = running_add
        return discount_r

    def run(self):
        # Sessionִ��
        with tf.Session() as sess:
            rendering = False
            init = tf.global_variables_initializer()
            sess.run(init)
            observation = env.reset()
            gradBuff = sess.run(self.tvars)
            for ix, grad in enumerate(gradBuff):
                gradBuff[ix] = grad * 0
            episode_number = 1
            while episode_number <= total_episodes:
                if reward_sum / batch_size > 100 or rendering == True:
                    rendering = True
                    env.render()

                x = np.reshape(self.var_input_x, [1, self.input_dimension])

                tfprob = sess.run(self.var_output , feed_dict={self.var_input_x: x})
                action = 1 if np.random.uniform() < tfprob else 0
                xs.append(x)
                y = 1 - action
                ys.append(y)

                observation, reward, done, info = env.step(action)
        reward_sum += reward
        drs.append(reward)
        if done:
            episode_number += 1
            epx = np.vstack(xs)
            epy = np.vstack(ys)
            epr = np.vstack(drs)
            xs, ys, drs = [], [], []
            discount_epr = discount_reward(epr)
            discount_epr -= np.mean(discount_epr)
            discount_epr /= np.std(discount_epr)

            tGrad = sess.run(newGrads, feed_dict={observate:epx,
                                                  input_y:epy,
                                                  advantages: discount_epr})
            for ix, grad in enumerate(tGrad):
                gradBuff[ix] += grad
                if episode_number % batch_size == 0:
                    sess.run(updateGrads, feed_dict={W1grad:gradBuff[0],
                                                 W2grad:gradBuff[1]})
                    for ix, grad in enumerate(gradBuff):
                        gradBuff[ix] = grad * 0
                print('Average reward for episode %d: %f.' % \
                      (episode_number, reward_sum/batch_size))
                if reward_sum/batch_size > 200:
                    print('Task solve in', episode_number, 'episodes!')
                    break

                reward_sum = 0

            observation = env.reset()

env = SingleCartPoleEnv().unwrapped
net = PolicyNet()


def _do_learn(observation,action,reward,observation_,step,totalreward,total_step):
    RL.store_transition(observation, action, reward, observation_)
    if total_step > 10:
        RL.learn()

def run():
    complexes = []
    reward_list = []
    notdone_count_list = []
    steps = []

    episode_reward_list = []
    episode_notdone_count_list = []
    total_step = 0
    while True:
        # ִ��һ��
        notdone_count, episode_reward, step, total_step= runner.do_until_done(env,net.choose_action,total_step,_do_learn)
        # �ж��Ƿ�����������Ӷ�
        if notdone_count > env.max_notdone_count or total_step >= 1500:
            complexes.append(force.force_generator.currentComplex())
            reward_list.append(np.average(episode_reward_list))
            notdone_count_list.append(np.average(episode_notdone_count_list))
            steps.append(total_step)
            np.save('dqn_result.npz', (complexes, notdone_count_list, reward_list,steps))

            episode_notdone_count_list,episode_reward_list = [],[],
            total_step = 0

            print('���Ӷ�:', complexes)
            print('����:', reward_list)
            print("��������:", notdone_count_list)

            # �������Ӷ�,Ϊ�˼ӿ�ִ���ٶ�,�ø��Ӷ����ӷ������ٴ���min_up
            changed, newcomplex, k, w, f, sigma = force.force_generator.promptComplex(5.0)
            if not changed:
                break  # ���Ӷ��Ѿ��ﵽ���,����
            print('�µĻ������Ӷ�=%.3f,k=%.2f,w=%.2f,f=%.2f,sigma=%.2f' % (newcomplex, k, w, f, sigma))
        else:
            if total_step % 100 == 0 and total_step != 0:
                print("��������=", episode_notdone_count_list, ",ƽ��=", np.average(episode_notdone_count_list))
                print("�ۼƽ���=", episode_reward_list, ",ƽ��=", np.average(episode_reward_list))
            episode_reward_list.append(episode_reward)
            if len(episode_reward_list) > 10:
                episode_reward_list = episode_reward_list[-10:]
            episode_notdone_count_list.append(notdone_count)
            if len(episode_notdone_count_list) > 10:
                episode_notdone_count_list = episode_notdone_count_list[-10:]

    #np.save('dqn_result.npz', complexes, notdone_count_list,reward_list)
    RL.save()
    plt.plot(complexes, reward_list, label='reward')
    plt.plot(complexes, notdone_count_list, label='times')
    plt.xlabel('complexes')
    plt.savefig('dqn_cartpole.png')

#���ߣ�������
#���ӣ�https://www.imooc.com/article/36790
#��Դ��Ľ����