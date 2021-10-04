import axios from 'axios';

const HTTP_FARM_URL =  process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.location.href;


async function clearAlarm(alarm_id) {
  try {
    await axios.get(`${HTTP_FARM_URL}/api/clear-alarm/${alarm_id}`);
  } catch (error) {
    console.error('failed to clear alarm', error);
  }
}

async function fetchLastDataPoints(boards, amount) {
  try {
    const encodedBoards = encodeURIComponent(boards.join(','));
    const response = await axios.get(`${HTTP_FARM_URL}/api/last-points?boards=${encodedBoards}&amount=${amount}`);
    return response.data;
  } catch (error) {
    console.error('failed to fetch sensors', error);
  }
}

async function saveSettings(settings) {
  try {
    await axios.post(`${HTTP_FARM_URL}/api/update-settings`, settings);
  } catch (error) {
    console.error('failed to fetch streams', error);
  }
}

async function fetchStreams() {
  try {
    const response = await axios.get(`${HTTP_FARM_URL}/api/settings`);
    const settings = response.data;
    return settings?.streamer?.streams;
  } catch (error) {
    console.error('failed to fetch streams', error);
  }
}

async function deactivateService(serviceName) {
  try {
    const response = await axios.get(`${HTTP_FARM_URL}/api/deactivate-service/${serviceName}`);
    return response.status === 200;
  } catch(error) {
    console.error('failed to deactivate service', error);
  }
}

async function activateService(serviceName) {
  try {
    const response = await axios.get(`${HTTP_FARM_URL}/api/activate-service/${serviceName}`);
    return response.status === 200;
  } catch(error) {
    console.error('failed to activate service', error);
  }
}

async function fetchServiceStatus() {
  try {
    const response = await axios.get(`${HTTP_FARM_URL}/api/status`);
    return response.data;
  } catch(error) {
    console.error('failed to fetch service status', error);
  }
}

async function fetchWateringTimes() {
  try {
    const response = await axios.get(`${HTTP_FARM_URL}/api/watering-times`);
    return response.data;
  } catch(error) {
    console.error('failed to fetch watering times', error);
  }
}

async function fetchAllSettings() {
  try {
    const response = await axios.get(`${HTTP_FARM_URL}/api/settings`);
    return response.data;
  } catch (error) {
    console.error('failed to fetch all settings', error);
  }
}

async function fetchActiveAlarms() {
  try {
    const response = await axios.get(`${HTTP_FARM_URL}/api/active-alarms`);
    return response.data;
  } catch(error) {
    console.error('failed to fetch active alarms', error);
  }
}

export default {
  fetchStreams,
  deactivateService,
  activateService,
  fetchServiceStatus,
  fetchAllSettings,
  fetchWateringTimes,
  fetchActiveAlarms,
  saveSettings,
  fetchLastDataPoints,
  clearAlarm,
}