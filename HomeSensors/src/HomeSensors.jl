module HomeSensors

import HTTP

export serve

const angstrom = "192.168.0.231"

function get_temperature_humid()
    command = "tail -n1 /home/tomlee/output/temp.dat"
    read(`ssh -A tomlee@$(angstrom) $(command)`) |> String
end

function handler(request)
    get_temperature_humid()
end

function serve()
    hostname = "127.0.0.1"
    port = 12345
    server = HTTP.serve(handler, hostname, port)
    HTTP.run(server)
end

end # module HomeSensors
