ready_state = "READY"
home_state = "HOME"
ack_state = "ACK"
pano_state = "PANO"


def parse_code(code):
  commands = code.split(';')
  parsed = []
  for command in commands:
    parse = { 'state': '', 'settings': {} }
    actions = command.split(':')
    parse['state'] = actions.pop(0)
    for action in actions:
      key, value = action.split('_')
      parse['settings'][key] = value
    parsed.append(parse)


class StateMachine:

  def __init__(self, states):
    self._step = 0
    self.history = []
    self.states = states

  def current_step(self):
    return self._step;

  def is_done(self):
    return self._step <= len(self.states)-1

  def next(self, code):
    states = parse_code(code)
    self.history.append(states)

    if self.states[self._step](states):
      self._step += 1
      return True

    return False


def get_pano_code(angle_step):
  return f"{pano_state}:angle_{angle_step};"


def get_home_code():
  return f"{home_state};"


def is_ready(states):
  return len(states) > 0 and states[0]['state'] == ready_state


def did_ack_home(states):
  return (
    len(states) > 0
    and states[0]['state'] == ack_state 
    and 'state' in states[0]['settings']
    and states[0]['settings']['state'] == home_state
  )


def is_home_state(states):
  return len(states) > 0 and states[0]['state'] == home_state


def is_pano_state(states):
  return len(states) > 0 and states[0]['state'] == pano_state


def get_pano_state_machine():
  return StateMachine([
    is_ready,
    is_home_state,
    is_pano_state,
    is_ready,
  ])