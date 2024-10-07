import subprocess

class Source_device:
    def __init__(self):
        self.source_device = None
        self.source_devices_list = self.get_list_source_devices()
        self.num_source_devices = len(self.source_devices_list)

    def get_list_source_devices(debug=False):
        # Get output audio devices
        result = subprocess.run(["pactl", "list", "sources"], capture_output=True, text=True)
        if result:
            output = result.stdout
            source_devices_list = []
            source_device = None
            for number_line, line in enumerate(output.split("\n")):
                if "Source #" in line or "Fuente #" in line:
                    if source_device:
                        source_devices_list.append(source_device)
                    source_device = {"id": line.split("#")[1]}
                    properties = 0
                    ports = 0
                    formats = 0
                    activate_port = 0
                elif "Properties:" in line:
                    properties = 1
                    ports = 0
                    formats = 0
                    activate_port = 0
                    source_device["properties"] = {}
                elif "Ports:" in line:
                    properties = 0
                    ports = 1
                    formats = 0
                    activate_port = 0
                    source_device["ports"] = {}
                elif "Formats:" in line:
                    properties = 0
                    ports = 0
                    formats = 1
                    activate_port = 0
                    source_device["formats"] = {}
                elif "Active Port:" in line:
                    properties = 0
                    ports = 0
                    formats = 0
                    activate_port = 1
                    source_device["active_port"] = {}
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
                        source_device["properties"][key] = value
                    elif ports:
                        source_device["ports"][key] = value
                    elif formats:
                        if key != "":
                            source_device["formats"][key] = value
                    elif activate_port:
                        source_device["active_port"][key] = value
                    else:
                        source_device[key] = value
                
                if number_line == len(output.split("\n")) - 1:
                    source_devices_list.append(source_device)
                    
        return source_devices_list
    
    def asign_source_device(self, source_device_list_position):
        for source_device in self.source_devices_list:
            if source_device["id"] == self.source_devices_list[source_device_list_position]["id"]:
                self.source_device = source_device
                return True
        return False