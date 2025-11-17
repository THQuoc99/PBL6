interface TextFieldProps {
  label: string;
  value: any;
  onChange: (value: any) => void;
  type?: string;
  placeholder?: string;
  onBlur?: () => void;
}

export default function TextField({ 
  label, 
  value, 
  onChange, 
  type = "text", 
  placeholder,
  onBlur
}: TextFieldProps) {
  return (
    <label className="grid gap-1 text-sm">
      <span className="text-gray-600">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(type === "number" ? Number(e.target.value) : e.target.value)}
        onBlur={onBlur}
        placeholder={placeholder}
        className="rounded-xl border border-gray-200 bg-white px-3 py-2 outline-none focus:border-gray-300 focus:shadow-sm"
      />
    </label>
  );
}