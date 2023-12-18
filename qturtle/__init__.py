__version__ = "0.0.1"

__all__ = []

from .core import make
__all__.append("make")


from gymnasium.envs.registration import register

# register(
#      id="qturtle/GymEnvironment-v0",
#      entry_point="qturtle.env:GymEnvironment",
# )

from qturtle.builders.default import create_qturtle_env_3x3

register(
    id='TurtleBot3x3-v0',
    entry_point=create_qturtle_env_3x3,
)

print("Registered TurtleBot3x3-v0")

from qturtle.builders.default import create_qturtle_env_4x4

register(
    id='TurtleBot4x4-v0',
    entry_point=create_qturtle_env_4x4,
)

print("Registered TurtleBot4x4-v0")

from qturtle.builders.default import create_qturtle_env_5x5

register(
    id='TurtleBot5x5-v0',
    entry_point=create_qturtle_env_5x5,
)

print("Registered TurtleBot5x5-v0")
