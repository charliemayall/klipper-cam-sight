import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { selectBusy, useSessionStore } from "@/stores/session";

export function WebcamSelect() {
  const status = useSessionStore((s) => s.status);
  const busy = useSessionStore(selectBusy);
  const selectWebcam = useSessionStore((s) => s.selectWebcam);

  if (!status) return null;

  const options =
    status.webcams.length > 0
      ? status.webcams
      : status.webcam_name
        ? [status.webcam_name]
        : [];

  return (
    <Select
      value={status.webcam_name}
      disabled={busy || options.length <=1}
      onValueChange={(v) => v && void selectWebcam(v)}
    >
      <SelectTrigger size="sm" className="h-7 min-w-28">
        <SelectValue placeholder="Camera" />
      </SelectTrigger>
      {options.length > 1 && (
        <SelectContent>
          {options.map((name) => (
            <SelectItem key={name} value={name}>
              {name}
            </SelectItem>
          ))}
        </SelectContent>
      )}
    </Select>
  );
}
