import { Outlet } from "react-router-dom";

import Header from "./Header";

const MainLayout = () => {
  return (
    <div className="flex-grow flex flex-col w-full h-full">
      <Header />
      <main>
        <Outlet />
      </main>
      <footer></footer>
    </div>
  );
};

export default MainLayout;
