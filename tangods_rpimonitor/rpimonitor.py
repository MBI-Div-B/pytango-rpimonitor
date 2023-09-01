from tango import AttrWriteType, DispLevel, DevState
from tango.server import Device, attribute, command, device_property
import psutil, time, datetime


class RPiMonitor(Device):
    DEFAULT_POLLING_PERIOD = device_property(
        dtype=int, default_value=2000, doc="Default polling period in ms"
    )

    def initialize_dynamic_attributes(self):
        attrs = []
        attrs.append(
            attribute(
                name="cpu_load",
                label="CPU load",
                dtype=float,
                unit="%",
                format="%2.2f",
                fget=self.read_cpu_load,
                polling_period=self.DEFAULT_POLLING_PERIOD,
            )
        )
        attrs.append(
            attribute(
                name="cpu_temp",
                label="CPU temp",
                dtype=float,
                unit="\N{DEGREE SIGN}C",
                format="%.2f",
                fget=self.read_cpu_temp,
                polling_period=self.DEFAULT_POLLING_PERIOD,
            )
        )
        attrs.append(
            attribute(
                name="ram_total",
                label="RAM total",
                dtype=float,
                unit="MB",
                format="%.2f",
                fget=self.read_ram_info,
                polling_period=self.DEFAULT_POLLING_PERIOD,
            )
        )
        attrs.append(
            attribute(
                name="ram_available",
                label="RAM available",
                dtype=float,
                unit="MB",
                format="%.2f",
                fget=self.read_ram_info,
                polling_period=self.DEFAULT_POLLING_PERIOD,
            )
        )
        attrs.append(
            attribute(
                name="ram_used",
                label="RAM used",
                dtype=float,
                unit="MB",
                format="%.2f",
                fget=self.read_ram_info,
                polling_period=self.DEFAULT_POLLING_PERIOD,
            )
        )
        attrs.append(
            attribute(
                name="uptime",
                label="uptime",
                dtype=int,
                unit="min",
                fget=self.read_uptime,
                polling_period=self.DEFAULT_POLLING_PERIOD,
            )
        )
        for attr in attrs:
            self.add_attribute(attr)

    def read_cpu_load(self, attr):
        return psutil.cpu_percent()

    def read_cpu_temp(self, attr):
        return psutil.sensors_temperatures()["cpu_thermal"][0].current

    def read_ram_info(self, attr):
        # called once on ram_total polling
        attr_name = attr.get_name()
        if attr_name == "ram_total":
            self._memory_info = psutil.virtual_memory()
        # since the attributes have prefix "ram_" and then the same postfix as pustil fields:
        # psutil.virtual_memory() -> svmem(total=3978637312, available=2725101568, percent=31.5, used=983683072, free=1757483008, active=1258827776, inactive=595734528, buffers=0, cached=1237471232, shared=190779392, slab=253538304)
        # we can use their name to get the values and then convert it to MB from bytes
        return getattr(self._memory_info, attr_name[4:]) / (2**20)

    def read_uptime(self, attr):
        uptime_sec = time.time() - psutil.boot_time()
        uptime_min = round(uptime_sec / 60)
        return uptime_min

    def init_device(self):
        Device.init_device(self)
        self.initialize_dynamic_attributes()
        self.set_state(DevState.ON)

    def delete_device(self):
        Device.delete_device(self)
