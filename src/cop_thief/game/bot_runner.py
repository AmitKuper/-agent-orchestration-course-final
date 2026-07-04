"""Bot turn runner — advances the game until it is the human player's turn.

Called after every human action and after match creation to bring the game
to the state where human input is needed (or the game is over).
"""

from cop_thief.actors.base import Actor
from cop_thief.game_engine.engine import GameEngine
from cop_thief.game_engine.state import GameState


def run_bot_turns(
    engine: GameEngine,
    state: GameState,
    bot_actor: Actor,
    human_role: str,
) -> GameState:
    """Apply bot actions until it is *human_role*'s turn or the game ends.

    Args:
        engine: The game engine to use for action validation and application.
        state: Mutable game state (modified in place).
        bot_actor: Actor that generates moves for the bot player.
        human_role: The role ('cop' or 'thief') played by the human this sub-game.

    Returns:
        The same *state* object, mutated to the point where the human must act.
    """
    while not state.game_over and state.current_actor != human_role:
        bot_role = state.current_actor
        obs = engine.get_observation(state, bot_role)
        action = bot_actor.get_action(obs)
        engine.apply_action(state, bot_role, action)
    return state
