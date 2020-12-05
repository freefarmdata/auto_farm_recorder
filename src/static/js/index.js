async function getServiceStatus() {
  const data = await $.getJSON('/api/status');
  this.serviceStatus(data);
}

async function getLatestImage() {
  const data = await $.getJSON('/api/latest_image');
  this.latestImage(`data:image/png;base64,${data}`);
}

async function pollData() {
  await Promise.all([this.getServiceStatus(), this.getLatestImage()])
    .catch(console.log);
}

async function startPolling() {
  setInterval(this.pollData, 5000);
}

function ViewModel() {
  this.serviceStatus = ko.observable({ board: null, camera: null });
  this.latestImage = ko.observable("");

  this.getServiceStatus = getServiceStatus.bind(this);
  this.pollData = pollData.bind(this);
  this.startPolling = startPolling.bind(this);

  this.startPolling();
}

ko.applyBindings(new ViewModel());