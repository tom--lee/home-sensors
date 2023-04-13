//import  {pad} from pad

function format_time(time) {
    const hours24 = time.getHours()
    const hours = hours24 % 12
    const formatted_hours = (hours === 0 ? 12 : hours).toString().padStart(2, ' ');
    const formatted_minutes = time.getMinutes().toString().padStart(2, '0');
    return formatted_hours + ":" + formatted_minutes
  }

function update_time() {
    // Get the current time
    const current_time = new Date();
    const text = format_time(current_time);
    // Set the time in the span element
    document.getElementById("time").innerHTML = text;
  }
  
  // Call the function once to display the time immediately
  update_time();
  
  // Update the time every second
  setInterval(update_time, 1000);
  
