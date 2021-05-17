
import DisableServices from '../widgets/DisableServices';
import ToggleServices from '../widgets/ToggleServices';
import LiveStream from '../widgets/LiveStream';
import GlobalSettings from '../widgets/GlobalSettings';
import ManualWatering from '../widgets/ManualWatering';
import Alarms from '../widgets/Alarms';

export const WidgetTypes = {
  'disable': {
    settings: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1 },
    Component: DisableServices,
  },
  'toggle': {
    settings: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1 },
    Component: ToggleServices,
  },
  'live_stream': {
    settings: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1 },
    Component: LiveStream,
  },
  'global_settings': {
    settings: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1 },
    Component: GlobalSettings,
  },
  'manual_watering': {
    settings: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1 },
    Component: ManualWatering,
  },
  'alarms': {
    settings: { x: 0, y: 0, w: 2, h: 2, minW: 1, minH: 1 },
    Component: Alarms,
  }
};
