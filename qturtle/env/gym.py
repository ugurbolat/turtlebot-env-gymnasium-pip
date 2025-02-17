import gym
#from gym.spaces import Box
from gymnasium.spaces import Box
from ..sim import close_pybullet
import numpy as np

class GymEnvironment(gym.Env):
    """ Qturtle composable environment following the OpenAI Gym API """

    def __init__(self,
                 sim,
                 sim_steps,
                 turtlebot,
                 world,
                 control,
                 reward,
                 termination):

        """The constructor

        Parameters
        ----------
        sim : pybullet client
            The Simulation object
        sim_steps : int
            Default number of simulation steps per action
        turtlebot : qturtle.Turtlebot
            The robot object
        world : qturtle.world.World
            The world (walls, obstacles, start, goal) for the environment
        control : qturtle.control.Control
            Control scheme for the robot
        reward : qturtle.reward.Reward
            Reward function
        termination : qturtle.termination.Termination
            Termination criterion
        """
        self.sim = sim
        self.sim_steps = sim_steps

        self.world = world
        self.turtlebot = turtlebot

        self.control = control
        self.reward = reward
        self.termination = termination

        self.collisions = False

        # NOTE StepControl is modified to return a gymnasium space instead of gym space
        self.action_space = control.get_action_space()
        # TODO min-max values are set to -inf and inf for a now
        #self.observation_space = Box(low=-float('inf'), high=float('inf'), shape=(3,), dtype=np.float32)
        self.observation_space = Box(
            low=np.array([-float('inf'), -float('inf'), -np.pi]),
            high=np.array([float('inf'), float('inf'), np.pi]),
            shape=(3,)
        )
        self.steps = 0

    def step(self, action):
        """ One step of the agent in the environment

        Parameters
        ----------
        action : Any
            The action to take

        Returns
        -------
        Tuple[Any, float, boolean, dict]
            The next state, reward, flag indicating if the environment is finished and extra info
            (empty)
        """
        left, right, steps = self.control(action)

        self.turtlebot.set_velocities(left, right)
        self._run_sim_steps(steps)

        next_state = [list(self.turtlebot.get_pos_and_orientation())]
        next_state = np.array(next_state , dtype=np.float32)
        #done = self.termination(next_state, self.collisions)
        terminated = self.termination(next_state, self.collisions)
        reward = self.reward(next_state, self.collisions)
        # convert next_state to numpy array
        #next_state = np.array(next_state)

        self.steps += 1

        # gym version
        #return next_state, reward, done, {}
        # gymnasium version
        info = {}  # Update this based on your environment
        # NOTE trucated is set to False
        return next_state, reward, terminated, False, info

    def reset(self, seed=None, random=False, options=None):
        """Reset environment to starting state

        Parameters
        ----------
        random : boolean
            Reset to one of the alternative start states of the world at random

        Returns
        -------
        Any
            The starting state of the robot
        """

        super().reset(seed=seed)

        # TODO integrate seed and random (e.g., self.world.seed(seed))
        if random:
            pos, angle = self.world.sample_start()
            self.turtlebot.reset(pos, angle)
        else:
            self.turtlebot.reset()

        self._run_sim_steps(self.sim_steps)
        self.reward.reset()
        self.steps = 0

        # gym version
        #return  [list(self.turtlebot.get_pos_and_orientation())]

        # gymnaisum version
        observation = [list(self.turtlebot.get_pos_and_orientation())]
        observation = np.array(observation , dtype=np.float32)
        info = {}  # Update this based on your environment

        return observation, info

    def render(self, *_):
        """ Only exists for API compatibility with OpenAI gym """
        raise NotImplementedError("Rendering the env is controlled via the"
                                  " `gui` parameter")

    def close(self):
        """ Closes the environment and the underlying pybullet client """
        close_pybullet(self.sim)

    def seed(self, *_):
        """ Only exists for API compatibility with OpenAI gym """
        print("Info: No seeding for this env")

    def _run_sim_steps(self, steps, check_collisions=True):
        for _ in range(steps):
            self.sim.stepSimulation()

        if check_collisions:
            self._check_collisions()

    def _check_collisions(self):
        for obj in self.world.collision_objects:
            if len(self.sim.getContactPoints(self.turtlebot.robot, obj)) > 0:
                self.collisions = True
                return

        self.collisions = False
