import { Palette } from "lucide-react";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DEFAULT_THEME,
  THEME_LIST,
  THEME_META,
  type AppTheme,
} from "@/lib/theme";
import { useThemeStore } from "@/stores/theme";

function SchemeSwatch({
  bg,
  accent,
}: {
  bg: string;
  accent: string;
}) {
  return (
    <span
      className="inline-flex size-4 shrink-0 overflow-hidden rounded-full ring-1 ring-border"
      aria-hidden
    >
      <span className="h-full w-1/2" style={{ backgroundColor: bg }} />
      <span className="h-full w-1/2" style={{ backgroundColor: accent }} />
    </span>
  );
}

export function ThemePicker() {
  const theme = useThemeStore((s) => s.theme);
  const setTheme = useThemeStore((s) => s.setTheme);

  const current = THEME_META[theme] ?? THEME_META[DEFAULT_THEME];

  return (
    <Select value={theme} onValueChange={(v) => v && setTheme(v as AppTheme)}>
      <SelectTrigger
        size="sm"
        className="size-8 w-8 shrink-0 justify-center p-0 [&>svg:last-child]:hidden"
        aria-label={`Color scheme: ${current.label}`}
      >
        <Palette className="size-4 shrink-0" />
        <SelectValue className="sr-only">{current.label}</SelectValue>
      </SelectTrigger>
      <SelectContent align="end">
        {THEME_LIST.map((t) => (
          <SelectItem key={t.id} value={t.id}>
            <span className="flex items-center gap-2">
              <SchemeSwatch bg={t.preview.bg} accent={t.preview.accent} />
              {t.label}
            </span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
