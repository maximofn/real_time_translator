import subprocess

class Sink_device:
    def __init__(self):
        self.sink_device = None
        self.sink_devices_list = self.get_list_sink_devices()
        self.num_sink_devices = len(self.sink_devices_list)

    def get_list_sink_devices(self, debug=False):
        # Get output audio devices
        result = subprocess.run(["pactl", "list", "sinks"], capture_output=True, text=True)
        if result:
            output = result.stdout
            sink_devices_list = []
            sink_device = None
            for number_line, line in enumerate(output.split("\n")):
                if "Sink #" in line or "Destino #" in line:
                    if sink_device: # If not the first device append the previous device to the list
                        sink_devices_list.append(sink_device)
                    sink_device = {"id": line.split("#")[1]}
                    if debug: print(f"\tOutput device: {sink_device['id']}")
                    properties = 0
                    ports = 0
                    formats = 0
                elif "Properties:" in line:
                    properties = 1
                    ports = 0
                    formats = 0
                    sink_device["properties"] = {}
                elif "Ports:" in line:
                    properties = 0
                    ports = 1
                    formats = 0
                    sink_device["ports"] = {}
                elif "Formats:" in line:
                    properties = 0
                    ports = 0
                    formats = 1
                    sink_device["formats"] = {}
                else:
                    key = line.split(":")[0].strip()
                    if "balance" in key:
                        key = "balance"
                        value = line.split("balance")[1]
                    else:
                        value = line.split(":")[1:]

                    # if value is a list, join it
                    if type(value) == list:
                        value = "".join(value).strip()
                    else:
                        value = value.strip()

                    if properties:
                        sink_device["properties"][key] = value
                    elif ports:
                        sink_device["ports"][key] = value
                    elif formats:
                        if key != "":
                            sink_device["formats"][key] = value
                    else:
                        sink_device[key] = value
                
                if number_line == len(output.split("\n")) - 1:
                    sink_devices_list.append(sink_device)

        return sink_devices_list
    
    def asign_sink_device(self, sink_device_list_position):
        for sink_device in self.sink_devices_list:
            if sink_device["id"] == self.sink_devices_list[sink_device_list_position]["id"]:
                self.sink_device = sink_device
                return True
        return False
    