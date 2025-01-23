import { Link } from "react-router-dom";

import { navItems } from "@/constants/nav";

const Navbar = () => {
  return (
    <nav className="flex">
      <ul className="flex items-center justify-center space-x-4 h-full">
        {navItems.map((item, index) => (
          <NavItem key={`${index}-${item.href}`} {...item} />
        ))}
      </ul>
    </nav>
  );
};

interface NavItemProps {
  href: string;
  text: string;
}

const NavItem = ({ href, text }: NavItemProps) => {
  return (
    <li>
      <Link to={href} className="text-base font-medium">
        <span>{text}</span>
      </Link>
    </li>
  );
};

export default Navbar;
