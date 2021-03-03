async function getServiceStatus() {
  const data = await $.getJSON('/api/status');
  console.log(data);
  this.serviceStatus(data);
}

async function getWateringTime() {
  const data = await $.getJSON('/api/get/water');
  console.log(data);
  this.waterTime(data);
}

async function setWateringTime() {
  await $.get('/api/set/water');
}

async function clearWateringTime() {
  await $.get('/api/clear/water');
}

async function getLatestImage() {
  const data = await $.get('/api/get/latest_image');
  this.latestImage(`data:image/png;base64,${data}`);
}

async function pollData() {
  await Promise.all([
    this.getServiceStatus(),
    this.getWateringTime(),
    this.getLatestImage()
  ]).catch(console.error);
}

async function startPolling() {
  setInterval(this.pollData, 5000);
}

function ViewModel() {
  this.waterTime = ko.observable({ set: null, start: false })
  this.serviceStatus = ko.observable({ board: null, camera: null, video: null, uploader: null });
  this.latestImage = ko.observable("");

  this.setWateringTime = setWateringTime.bind(this);
  this.clearWateringTime = clearWateringTime.bind(this);
  this.getWateringTime = getWateringTime.bind(this);
  this.getServiceStatus = getServiceStatus.bind(this);
  this.getLatestImage = getLatestImage.bind(this);
  this.pollData = pollData.bind(this);
  this.startPolling = startPolling.bind(this);

  this.startPolling();
}

ko.applyBindings(new ViewModel());