import {
  BackendType,
  type BackendFlags,
} from "@/api";

let devBackendType: BackendType = BackendType.BASE;

export function getDevBackendType(): BackendType {
  return devBackendType;
}

export function setDevBackendType(type: BackendType): void {
  devBackendType = type;
}

export function devBackendFlags(type: BackendType): BackendFlags {
  if (type === BackendType.INDX) {
    return {
      auto_toolchange: true,
      requires_apply_macro: false,
      syncs_tool_count: true,
    };
  }
  return {
    auto_toolchange: false,
    requires_apply_macro: true,
    syncs_tool_count: false,
  };
}
