import { LogIn, User, ChevronRight } from "lucide-react";
import { AlignJustify } from "lucide-react";
import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetClose,
} from "@/components/ui/sheet";
import { navItems } from "@/constants/nav";
import ROUTE_MAP from "@/constants/route_map";
import useUser from "@/hooks/useUser";

const Drawer = () => {
  const { user } = useUser();

  return (
    <Sheet>
      <SheetTrigger asChild className="flex">
        <Button variant="outline" size="icon">
          <AlignJustify />
        </Button>
      </SheetTrigger>
      <SheetContent className="bg-white">
        <SheetHeader>
          <SheetTitle>
            <br />
          </SheetTitle>
          <SheetDescription className="flex flex-col gap-8">
            {user ? (
              // <Profile user={user} className="" />
              <></>
            ) : (
              <div className="flex flex-col gap-2">
                <SheetClose asChild>
                  <Button asChild variant="secondary">
                    <Link to={ROUTE_MAP.LOGIN} className="flex gap-1">
                      <LogIn size={18} />
                      로그인
                    </Link>
                  </Button>
                </SheetClose>
                <SheetClose asChild>
                  <Button asChild>
                    <Link to={ROUTE_MAP.SIGNUP} className="flex gap-1">
                      <User size={18} />
                      회원가입
                    </Link>
                  </Button>
                </SheetClose>
              </div>
            )}
            <div className="flex flex-col gap-4">
              {navItems.map((item, index) => (
                <NavItem key={`${index}-${item.href}`} {...item} />
              ))}
            </div>
          </SheetDescription>
        </SheetHeader>
      </SheetContent>
    </Sheet>
  );
};

interface NavItemProps {
  href: string;
  text: string;
}

const NavItem = ({ href, text }: NavItemProps) => {
  return (
    <SheetClose asChild key={`${href}`}>
      <Link
        to={href}
        className="text-base font-medium flex justify-between space-x-4"
      >
        <span className="flex-grow text-start">{text}</span>
        <ChevronRight />
      </Link>
    </SheetClose>
  );
};

export default Drawer;
