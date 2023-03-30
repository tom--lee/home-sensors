function updateTime() {
    // Get the current time
    const currentTime = new Date();
  
    // Get the hours and minutes
    let hours = currentTime.getHours();
    let minutes = currentTime.getMinutes();
  
    // Add leading zeros if necessary
    if (hours < 10) {
      hours = "0" + hours;
    }
    if (minutes < 10) {
      minutes = "0" + minutes;
    }
  
    // Set the time in the span element
    document.getElementById("time").innerHTML = `${hours}:${minutes}`;
  }
  
  // Call the function once to display the time immediately
  updateTime();
  
  // Update the time every second
  setInterval(updateTime, 1000);
  