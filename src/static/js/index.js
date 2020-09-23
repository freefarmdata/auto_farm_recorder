async function getServiceStatus() {
  const data = await $.getJSON('/api/status');
  this.serviceStatus(data);
}

async function pollData() {
  await Promise.all([this.getServiceStatus()])
    .catch(console.log);
}

async function startPolling() {
  setInterval(this.pollData, 3000);
}

function ViewModel() {
  this.serviceStatus = ko.observable({ board: null, camera: null });

  this.getServiceStatus = getServiceStatus.bind(this);
  this.pollData = pollData.bind(this);
  this.startPolling = startPolling.bind(this);

  this.startPolling();
}

ko.applyBindings(new ViewModel());