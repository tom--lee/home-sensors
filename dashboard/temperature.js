//import  {pad} from pad

function format_temperature(temperature) {
    return temperature + "°C"
}

async function get_sensor_data() {
    const url = "127.0.0.1"
    const port = "12345"
    const endpointUrl = `http://${url}:${port}`;
    console.log(endpointUrl)
    const response = await fetch(endpointUrl, {mode: "no-cors"})
    if (!response.ok) {
        return response.status
    }
    const responseBody = await response.text();
    return JSON.parse(responseBody);
}

async function get_temperature() {
    return (await get_sensor_data()).temperature
}

async function update_temperature() {
    // Get the current time
    const temperature = await get_temperature()
    if (typeof(temperature) !== "number") {
        console.log("no temperature reading " + temperature)
        return
    }

    const text = format_temperature(temperature);
    // Set the time in the span element
    document.getElementById("temperature").innerHTML = text;
}

// Call the function once to display the time immediately
update_temperature();

// Update the time every second
setInterval(update_temperature, 10000);

