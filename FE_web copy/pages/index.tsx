import dynamic from "next/dynamic";
import { BrowserRouter } from "react-router-dom";

const AppRouter = dynamic(
  () => import("../AppRouter").then((mod) => {
    return function Wrapped() {
      return (
        <BrowserRouter>
          <mod.default />
        </BrowserRouter>
      );
    };
  }),
  { ssr: false }
);

export default function Home() {
  return <AppRouter />;
}
