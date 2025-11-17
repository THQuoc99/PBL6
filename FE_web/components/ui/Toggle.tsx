import clsx from "clsx";

interface ToggleProps {
  checked: boolean;
  onChange: (value: boolean) => void;
}

export default function Toggle({ checked, onChange }: ToggleProps) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={clsx(
        "inline-flex h-6 w-11 items-center rounded-full border transition",
        checked ? "bg-gray-900 border-gray-900" : "bg-gray-200 border-gray-200"
      )}
      aria-pressed={checked}
    >
      <span
        className={clsx(
          "m-0.5 inline-block h-5 w-5 rounded-full bg-white transition",
          checked ? "translate-x-5" : "translate-x-0"
        )}
      />
    </button>
  );
}