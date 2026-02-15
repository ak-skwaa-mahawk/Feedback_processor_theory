import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
import random

class Actor(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(Actor, self).__init__()
        self.fc1 = nn.Linear(state_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_dim)
        self.tanh = nn.Tanh()

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        action = 0.3 + 0.1 * self.tanh(self.fc3(x))  # Scale to [0.2, 0.4]
        return action

class Critic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(Critic, self).__init__()
        self.fc1 = nn.Linear(state_dim + action_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, 1)

    def forward(self, state, action):
        x = torch.cat([state, action], 1)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        q_value = self.fc3(x)
        return q_value

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = []
        self.capacity = capacity

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done

    def __len__(self):
        return len(self.buffer)

class TriadEnv:
    def __init__(self):
        self.G = np.array([3.14162100062, 3.141592653589793, 3.23586896365])
        self.T = np.array([3.141592653589793, 3.23586896365, 3.14162100062])
        self.L = (self.G + self.T) / 2
        self.reset()

    def reset(self):
        self.v = np.array([3.173027539287, 3.173027539287, 3.173027539287])
        self.n_step = 0
        return self.get_state()

    def get_state(self):
        error = np.linalg.norm(self.v - self.L)
        sigma = 0.01 + (self.n_step / 50.0) * 0.04
        return np.array([error, sigma], dtype=np.float32)

    def step(self, k):
        sigma = 0.01 + (self.n_step / 50.0) * 0.04
        noise = np.random.normal(0, sigma, 3)
        v_noisy = self.v + noise
        self.v = (1 - k) * v_noisy + k * self.L
        self.n_step += 1
        done = self.n_step >= 50
        reward = -np.linalg.norm(self.v - self.L)  # Reward low error
        state = self.get_state()
        return state, reward, done

class DDPGAgent:
    def __init__(self, state_dim, action_dim):
        self.actor = Actor(state_dim, action_dim)
        self.actor_target = Actor(state_dim, action_dim)
        self.actor_target.load_state_dict(self.actor.state_dict())
        self.critic = Critic(state_dim, action_dim)
        self.critic_target = Critic(state_dim, action_dim)
        self.critic_target.load_state_dict(self.critic.state_dict())
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=1e-3)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=1e-3)
        self.replay_buffer = ReplayBuffer(10000)
        self.gamma = 0.95
        self.tau = 0.005
        self.batch_size = 64
        self.epsilon = 1.0
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.995

    def select_action(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        if random.random() < self.epsilon:
            action = np.random.uniform(0.2, 0.4)
        else:
            action = self.actor(state).detach().numpy()[0]
        return action

    def update(self):
        if len(self.replay_buffer) < self.batch_size:
            return
        batch = random.sample(self.replay_buffer, self.batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        state = torch.FloatTensor(state)
        action = torch.FloatTensor(action)
        reward = torch.FloatTensor(reward).unsqueeze(1)
        next_state = torch.FloatTensor(next_state)
        done = torch.FloatTensor(done).unsqueeze(1)

        # Critic update
        q_values = self.critic(state, action)
        next_actions = self.actor_target(next_state)
        target_q = self.critic_target(next_state, next_actions)
        target_q = reward + (1 - done) * self.gamma * target_q
        critic_loss = nn.MSELoss()(q_values, target_q.detach())
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # Actor update
        pred_actions = self.actor(state)
        actor_loss = -self.critic(state, pred_actions).mean()
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # Soft update targets
        for target_param, param in zip(self.actor_target.parameters(), self.actor.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
        for target_param, param in zip(self.critic_target.parameters(), self.critic.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

# Training
env = TriadEnv()
agent = DDPGAgent(state_dim=2, action_dim=1)
num_episodes = 100
rewards = []

for episode in range(num_episodes):
    state = env.reset()
    episode_reward = 0
    for step in range(50):
        action = agent.select_action(state)
        next_state, reward, done = env.step(action)
        agent.replay_buffer.push(state, action, reward, next_state, done)
        state = next_state
        episode_reward += reward
        if done:
            break
    agent.update()
    rewards.append(episode_reward)
    if episode % 20 == 0:
        print(f"Episode {episode}, Reward: {episode_reward}")

# Test Episode
state = env.reset()
test_errors = []
test_ks = []
for step in range(50):
    k = agent.select_action(state)[0]
    next_state, reward, done = env.step(k)
    error = np.linalg.norm(env.v - env.L)
    test_errors.append(error)
    test_ks.append(k)
    state = next_state
    if done:
        break

print("Test Episode Errors:", test_errors[:10], "...", test_errors[-5:])
print("Test Episode Learned k:", test_ks[:10], "...", test_ks[-5:])
print("Final Error Norm:", test_errors[-1])
print("Avg Learned k:", np.mean(test_ks))

# Plot and save to path (e.g., './ddpg_simulation.png')
plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1)
plt.plot(rewards)
plt.title('Training Rewards')
plt.xlabel('Episode')
plt.ylabel('Total Reward')

plt.subplot(1, 3, 2)
plt.plot(test_errors)
plt.title('Test Error Norm')
plt.xlabel('Step')
plt.ylabel('||e_n||')

plt.subplot(1, 3, 3)
plt.plot(test_ks)
plt.title('Learned k_n')
plt.xlabel('Step')
plt.ylabel('k')

plt.tight_layout()
plt.savefig('./ddpg_simulation.png')
print("Graph saved as './ddpg_simulation.png'")