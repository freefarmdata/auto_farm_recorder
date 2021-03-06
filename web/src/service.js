import axios from 'axios';

const HTTP_FARM_URL =  process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:5000' : window.location.href;

async function fetchWateringTimes() {
  const response = await axios.get(`${HTTP_FARM_URL}/api/watering-times`);
  return response.data;
}

async function fetchActiveAlarms() {
  const response = await axios.get(`${HTTP_FARM_URL}/api/active-alarms`);
  return response.data;
}

export default {
  fetchWateringTimes,
  fetchActiveAlarms
}