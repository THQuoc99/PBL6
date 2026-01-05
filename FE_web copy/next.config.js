/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      // Proxy cho provinces API để bypass CORS
      {
        source: "/api/provinces/:path*",
        destination: "https://provinces.open-api.vn/api/:path*",
      },
      // Proxy cho GHTK API để bypass CORS
      {
        source: "/api/ghtk/:path*",
        destination: "https://services.giaohangtietkiem.vn/services/:path*",
      },
      // Redirect tất cả routes về trang chủ để React Router xử lý
      {
        source: "/:path*",
        destination: "/",
      },
    ];
  },
};

module.exports = nextConfig;
