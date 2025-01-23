import Drawer from "./Drawer";
import Logo from "./Logo";
import Navbar from "./Navbar";

const Header = () => {
  return (
    <header className="flex justify-between items-center px-2 w-full h-14 lg:h-16 bg-white border-b border-background">
      <Logo />
      <Navbar />
      <Drawer />
    </header>
  );
};

export default Header;
