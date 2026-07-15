import ctypes
import enum
import pathlib
from . import ioctl_macros as ioctl_macros
from ..common import ExtendedFlag as ExtendedFlag
from _typeshed import Incomplete
from typing import Any

DEFAULT_USB_IDS_PATH: str
USB_DEVICE_PATH: str
TTY_PATH: str
SER_BYPTH_PATH: str
SER_BYID_PATH: str
V4L_DEVICE_PATH: str
V4L_BYPTH_PATH: str
V4L_BYID_PATH: str
OPTIONAL_USB_INFO: Incomplete
NULL_DESCRIPTIONS: Incomplete

def read_item(parent: pathlib.Path, filename: str) -> str: ...
def find_usb_folder(usb_path: pathlib.Path) -> str | None: ...

class UsbIdData:
    usb_id_path: Incomplete
    parsed: bool
    usb_info: dict[str, str]
    def __init__(self, usb_id_path: str | pathlib.Path) -> None: ...
    def get_item(self, key: str, check_null: bool = False) -> str | None: ...
    def parse_usb_ids(self) -> None: ...
    def get_product_info(self, vendor_id: str, product_id: str) -> dict[str, Any]: ...
    def get_class_info(self, cls_id: str, subcls_id: str, proto_id: str) -> dict[str, Any]: ...

def find_usb_devices() -> list[dict[str, Any]]: ...
def find_serial_devices() -> list[dict[str, Any]]: ...

class struct_v4l2_capability(ctypes.Structure): ...
class struct_v4l2_fmtdesc(ctypes.Structure): ...
class struct_v4l2_frmsize_discrete(ctypes.Structure): ...
class struct_v4l2_frmsize_stepwise(ctypes.Structure): ...
class struct_v4l2_frmsize_union(ctypes.Union): ...
class struct_v4l2_frmsizeenum(ctypes.Structure): ...

class V4L2Capability(ExtendedFlag):
    VIDEO_CAPTURE = 1
    VIDEO_OUTPUT = 2
    VIDEO_OVERLAY = 4
    VBI_CAPTURE = 16
    VBI_OUTPUT = 32
    SLICED_VBI_CAPTURE = 64
    SLICED_VBI_OUTPUT = 128
    RDS_CAPTURE = 256
    VIDEO_OUTPUT_OVERLAY = 512
    HW_FREQ_SEEK = 1024
    RDS_OUTPUT = 2048
    VIDEO_CAPTURE_MPLANE = 4096
    VIDEO_OUTPUT_MPLANE = 8192
    VIDEO_M2M_MPLANE = 16384
    VIDEO_M2M = 32768
    TUNER = 65536
    AUDIO = 131072
    RADIO = 262144
    MODULATOR = 524288
    SDR_CAPTURE = 1048576
    EXT_PIX_FORMAT = 2097152
    SDR_OUTPUT = 4194304
    META_CAPTURE = 8388608
    READWRITE = 16777216
    STREAMING = 67108864
    META_OUTPUT = 134217728
    TOUCH = 268435456
    IO_MC = 536870912
    SET_DEVICE_CAPS = 2147483648

class V4L2FrameSizeTypes(enum.IntEnum):
    DISCRETE = 1
    CONTINUOUS = 2
    STEPWISE = 3

class V4L2FormatFlags(ExtendedFlag):
    COMPRESSED = 1
    EMULATED = 2

V4L2_BUF_TYPE_VIDEO_CAPTURE: int
V4L2_QUERYCAP: Incomplete
V4L2_ENUM_FMT: Incomplete
V4L2_ENUM_FRAMESIZES: Incomplete

def v4l2_fourcc_from_fmt(pixelformat: int) -> str: ...
def v4l2_fourcc(format: str) -> int: ...
def find_video_devices() -> list[dict[str, Any]]: ...
