import { Link } from "react-router-dom";

import { ROUTE_MAP } from "@/constants";

const Logo = () => {
  return (
    <Link to={ROUTE_MAP.MAIN} className="flex items-center gap2">
      <img src="/logo.svg" alt="logo" className="w-8 h-8" />
    </Link>
  );
};

export default Logo;
