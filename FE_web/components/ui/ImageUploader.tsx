import { Upload, X } from "lucide-react";

interface ImageUploaderProps {
  label: string;
  images: string[];
  setImages: (images: string[]) => void;
}

export default function ImageUploader({ label, images, setImages }: ImageUploaderProps) {
  const onFiles = (files: FileList | null) => {
    if (!files) return;
    const readers = Array.from(files).map(
      (file) =>
        new Promise<string>((resolve) => {
          const fr = new FileReader();
          fr.onload = () => resolve(String(fr.result));
          fr.readAsDataURL(file);
        })
    );
    Promise.all(readers).then((res) => setImages([...(images || []), ...res]));
  };

  return (
    <div className="grid gap-2 text-sm">
      <span className="text-gray-600">{label}</span>
      <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl border border-dashed border-gray-300 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50">
        <Upload className="h-4 w-4" />
        <span>Upload images</span>
        <input 
          type="file" 
          accept="image/*" 
          multiple 
          className="hidden" 
          onChange={(e) => onFiles(e.target.files)} 
        />
      </label>
      {!!images?.length && (
        <div className="flex flex-wrap gap-2">
          {images.map((src, i) => (
            <div key={i} className="relative">
              <img src={src} className="h-16 w-16 rounded-lg object-cover" />
              <button
                onClick={() => setImages(images.filter((_, idx) => idx !== i))}
                className="absolute -right-2 -top-2 rounded-full bg-white p-1 shadow"
                title="Remove"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}