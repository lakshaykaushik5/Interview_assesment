"use client";

import Link from "next/link";
import { Book, Menu, Sunset, Trees, Zap } from "lucide-react";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

interface MenuItem {
  title: string;
  url: string;
  description?: string;
  icon?: React.ReactNode;
  items?: MenuItem[];
}

interface NavbarProps {
  logo?: {
    url: string;
    src: string;
    alt: string;
    title: string;
  };
  menu?: MenuItem[];
  auth?: {
    logout: { title: string; url: string; };
  };
  onNavbarClick?: () => void;
}

export function Navbar({
  logo = {
    url: "/",
    src: "https://deifkwefumgah.cloudfront.net/shadcnblocks/block/logos/shadcnblockscom-icon.svg",
    alt: "logo",
    title: "IA1",
  },
  menu = [],
  auth = {
    logout: { title: "Logout", url: "/" },
  },
  onNavbarClick
}: NavbarProps) {
  return (
    <header className="py-4 border-b bg-background">
      <div className="container flex items-center justify-between">
        {/* Left: Logo + Menu */}
        <div className="flex items-center gap-6">
          <Link href={logo.url} className="flex items-center gap-2">
            <img src={logo.src} alt={logo.alt} className="max-h-8 dark:invert" />
            <span className="text-lg font-semibold tracking-tight">
              {logo.title}
            </span>
          </Link>

          {/* Desktop Menu */}
          <NavigationMenu className="hidden lg:block">
            <NavigationMenuList>
              {menu.map((item) => renderMenuItem(item))}
            </NavigationMenuList>
          </NavigationMenu>
        </div>

        {/* Right: Auth */}
        <div className="hidden gap-2 lg:flex">
          <Button variant="outline" size="sm" onClick={onNavbarClick}>
            {auth.logout.title}
          </Button>
        </div>

        {/* Mobile Menu */}
        <div className="block lg:hidden">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="icon">
                <Menu className="size-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="overflow-y-auto">
              <SheetHeader>
                <SheetTitle>
                  <Link href={logo.url} className="flex items-center gap-2">
                    <img src={logo.src} alt={logo.alt} className="max-h-8 dark:invert" />
                    <span className="font-semibold">{logo.title}</span>
                  </Link>
                </SheetTitle>
              </SheetHeader>

              <div className="mt-6 flex flex-col gap-6">
                <Accordion type="single" collapsible className="w-full flex flex-col gap-2">
                  {menu.map((item) => renderMobileMenuItem(item))}
                </Accordion>

                <div className="flex flex-col gap-3">
                  <Button variant="outline" onClick={onNavbarClick}>
                    {auth.logout.title}
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}

/* Desktop Dropdown Handler */
function renderMenuItem(item: MenuItem) {
  if (item.items) {
    return (
      <NavigationMenuItem key={item.title}>
        <NavigationMenuTrigger>{item.title}</NavigationMenuTrigger>
        <NavigationMenuContent className="p-4 grid gap-2 bg-popover text-popover-foreground">
          {item.items.map((subItem) => (
            <NavigationMenuLink asChild key={subItem.title} className="w-72">
              <SubMenuLink item={subItem} />
            </NavigationMenuLink>
          ))}
        </NavigationMenuContent>
      </NavigationMenuItem>
    );
  }

  return (
    <NavigationMenuItem key={item.title}>
      <NavigationMenuLink asChild>
        <Link
          href={item.url}
          className="hover:bg-muted hover:text-accent-foreground inline-flex h-9 items-center rounded-md px-3 text-sm font-medium transition-colors"
        >
          {item.title}
        </Link>
      </NavigationMenuLink>
    </NavigationMenuItem>
  );
}

/* Mobile Accordion Handler */
function renderMobileMenuItem(item: MenuItem) {
  if (item.items) {
    return (
      <AccordionItem key={item.title} value={item.title} className="border-b-0">
        <AccordionTrigger className="py-2 font-medium">{item.title}</AccordionTrigger>
        <AccordionContent className="mt-2 flex flex-col gap-2">
          {item.items.map((subItem) => (
            <SubMenuLink key={subItem.title} item={subItem} />
          ))}
        </AccordionContent>
      </AccordionItem>
    );
  }

  return (
    <Link key={item.title} href={item.url} className="text-sm font-medium">
      {item.title}
    </Link>
  );
}

/* Submenu Link Block */
function SubMenuLink({ item }: { item: MenuItem }) {
  return (
    <Link
      href={item.url}
      className="hover:bg-muted hover:text-accent-foreground flex items-start gap-3 rounded-md p-3 transition-colors"
    >
      <div className="text-foreground">{item.icon}</div>
      <div>
        <div className="text-sm font-semibold">{item.title}</div>
        {item.description && (
          <p className="text-muted-foreground text-xs">{item.description}</p>
        )}
      </div>
    </Link>
  );
}
