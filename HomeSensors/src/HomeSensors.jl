module HomeSensors

import HTTP
using Dates

export serve

const angstrom = "192.168.0.231"

struct Record
    device_id::String
    time::Float64
    temperature::Float64
    humidity::Float64
end

const store = Dict{String, Record}()

function record!(record::Record)
    store[record.device_id] = record
end

function get_temperature_humid()
    command = "tail -n1 /home/tomlee/output/temp.dat"
    read(`ssh -A tomlee@$(angstrom) $(command)`) |> String
end

function record_temperature_humid!(target::String)
    _, id, value = split(target, "/", limit = 3)
    temperature, humidity = parse.(Float64, split(value, "_", limit = 2))
    record!( Record(
        id,
        Dates.time(),
        temperature,
        humidity
    ))
    
end

function handler(request::HTTP.Request)
    println(request)
    println(request.method)
    #dump(request)
    if (request.method == "GET")
        get_temperature_humid()
    elseif (request.method == "PUT")
        record_temperature_humid!(request.target)
    end
end

function serve()
    hostname = "0.0.0.0" # "127.0.0.1"
    port = 12345
    server = HTTP.serve(handler, hostname, port)
    HTTP.run(server)
end

end # module HomeSensors
