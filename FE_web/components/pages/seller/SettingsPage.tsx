import { useState } from "react";
import { Save } from "lucide-react";
import { StoreSettings } from "../../../types";
import { TextField, SelectField, Toggle, ToolbarButton } from "../../index";

interface SettingsPageProps {
  settings: StoreSettings;
  setSettings: (settings: StoreSettings) => void;
}

export default function SettingsPage({ settings, setSettings }: SettingsPageProps) {
  const [localSettings, setLocalSettings] = useState<StoreSettings>(settings);

  const handleSave = () => {
    setSettings(localSettings);
    alert("Settings saved successfully!");
  };

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Store Settings</h1>
        <ToolbarButton onClick={handleSave}>
          <Save className="h-4 w-4" /> Save Settings
        </ToolbarButton>
      </div>

      {/* Store Visual Identity */}
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">  
        {/* Cover Image */}
        <div className="mb-6">
          <div className="relative">
            <div 
              className="w-full h-80 bg-gray-100 rounded-lg overflow-hidden border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors"
              style={{
                backgroundImage: localSettings.coverImage 
                  ? `url(${localSettings.coverImage})` 
                  : 'url(https://aobongda.net/pic/Images/Module/News/images/giay-dep-nhat-10.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
            >
              <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                <label className="cursor-pointer bg-white px-4 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                  Change Cover
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        const reader = new FileReader();
                        reader.onload = () => {
                          setLocalSettings({ ...localSettings, coverImage: reader.result as string });
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                  />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Avatar */}
        <div className="mb-6">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div 
                className="w-32 h-32 bg-gray-100 rounded-full overflow-hidden border-4 border-white shadow-md"
                style={{
                  backgroundImage: localSettings.avatar 
                    ? `url(${localSettings.avatar})` 
                    : 'url(https://nganhquangcao.vn/upload/filemanager/files/adidas-logo-lich-su-y-nghia-bieu-tuong-adidas-5.jpg)',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
              >
                <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity rounded-full">
                  <label className="cursor-pointer text-white text-xs font-medium">
                    Change
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          const reader = new FileReader();
                          reader.onload = () => {
                            setLocalSettings({ ...localSettings, avatar: reader.result as string });
                          };
                          reader.readAsDataURL(file);
                        }
                      }}
                    />
                  </label>
                </div>
              </div>
            </div>
            <div>  <div className="text-xl font-bold">Store Avatar</div>
            
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Store Information</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <TextField
            label="Store Name"
            value={localSettings.storeName}
            onChange={(v) => setLocalSettings({ ...localSettings, storeName: v })}
          />
          <TextField
            label="Email"
            type="email"
            value={localSettings.email}
            onChange={(v) => setLocalSettings({ ...localSettings, email: v })}
          />
          <TextField
            label="Phone"
            value={localSettings.phone}
            onChange={(v) => setLocalSettings({ ...localSettings, phone: v })}
          />
          <SelectField
            label="Currency"
            value={localSettings.currency}
            onChange={(v) => setLocalSettings({ ...localSettings, currency: v })}
            options={["USD", "EUR", "GBP", "VND"]}
          />
          <div className="sm:col-span-2">
            <TextField
              label="Address"
              value={localSettings.address}
              onChange={(v) => setLocalSettings({ ...localSettings, address: v })}
            />
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Shipping Options</h2>
        <div className="grid gap-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Cash on Delivery</span>
              <div className="text-sm text-gray-500">Allow COD payments</div>
            </div>
            <Toggle
              checked={localSettings.shipping.cod}
              onChange={(v) => setLocalSettings({
                ...localSettings,
                shipping: { ...localSettings.shipping, cod: v }
              })}
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Express Shipping</span>
              <div className="text-sm text-gray-500">Fast shipping options</div>
            </div>
            <Toggle
              checked={localSettings.shipping.express}
              onChange={(v) => setLocalSettings({
                ...localSettings,
                shipping: { ...localSettings.shipping, express: v }
              })}
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Standard Shipping</span>
              <div className="text-sm text-gray-500">Economy shipping options</div>
            </div>
            <Toggle
              checked={localSettings.shipping.standard}
              onChange={(v) => setLocalSettings({
                ...localSettings,
                shipping: { ...localSettings.shipping, standard: v }
              })}
            />
          </div>
        </div>
      </div>
    </section>
  );
}